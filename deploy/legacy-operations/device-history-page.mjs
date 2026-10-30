import {PersistentDeviceStorage,requireDeviceStorage,mountDeviceStorageGate} from './storage-consent.mjs';
import {DeviceChannelJournal} from './channel-journal.mjs';
import {makeKey,signJws,verifyJws,hash} from './crypto.mjs';
const TYPE='codi-device-storage-test+jws';
const make=(tag,classes='',text='')=>{const n=document.createElement(tag);n.className=classes;n.textContent=text;return n;};
window.storageTest={PersistentDeviceStorage,requireDeviceStorage,DeviceChannelJournal,make,starts:0,databases:()=>indexedDB.databases()};
const t=window.storageTest;
t.policy=new PersistentDeviceStorage();
t.verify=async(wire,{scope,channel,previous,signal})=>{
  signal?.throwIfAborted();
  const p=await verifyJws(wire,t.publicKey,TYPE,500000);
  if(Object.keys(p).sort().join()!==['channel','count','head','previous','revision','scope','text','version'].sort().join()||p.version!==1||p.channel!==channel||p.scope!==scope)throw Error('Wrong signed history scope');
  if(p.head!==await hash(JSON.stringify([p.count,p.text])))throw Error('Invalid signed content hash');
  if(previous&&p.count>previous.floor.count&&p.previous!==previous.hash)throw Error('Wrong signed predecessor');
  signal?.throwIfAborted();return {channel:p.channel,revision:p.revision,count:p.count,head:p.head};
};
t.init=async()=>{t.key=await makeKey();t.publicKey=t.key.publicKey;t.channel=await hash('real browser storage fixture');};
t.packet=async({scope='account-a',channel=t.channel,count=1,revision=1,text='Saved signed device text',previous=null}={})=>signJws({version:1,scope,channel,count,revision,text,previous,head:await hash(JSON.stringify([count,text]))},t.key.privateKey,TYPE);
t.gate=(options={})=>{
  t.view?.dispose();t.life?.abort();t.life=new AbortController();t.starts=0;t.error=null;
  t.view=mountDeviceStorageGate({policy:options.policy||t.policy,signal:t.life.signal,make,onReady:async permit=>{await requireDeviceStorage(permit,{signal:t.life.signal});t.permit=permit;t.starts++;document.querySelector('#feature').textContent='History feature ready';}});
  document.querySelector('#gate').replaceChildren(t.view.element);
};
t.open=async(options={})=>{const j=new DeviceChannelJournal({verify:t.verify,...options});await j.open(t.permit,{signal:t.life.signal});t.journals??=[];t.journals.push(j);return j;};
t.close=()=>{t.view?.dispose();t.life?.abort();for(const j of t.journals||[])j.close();t.journals=[];t.policy.close();};
t.raw=async(work)=>{
  const db=await new Promise((resolve,reject)=>{const q=indexedDB.open('codi-device-channel-journal-v1',1);q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);});
  try{return await new Promise((resolve,reject)=>{const tx=db.transaction(['channels','accounting'],'readwrite');let value;work(tx.objectStore('channels'),tx.objectStore('accounting'),v=>value=v);tx.oncomplete=()=>resolve(value);tx.onabort=()=>reject(tx.error);});}finally{db.close();}
};
window.fixtureReady=true;
