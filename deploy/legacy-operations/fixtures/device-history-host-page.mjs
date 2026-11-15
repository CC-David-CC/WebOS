import {DeviceHistoryHost} from './assets/desktop/device-history-host.mjs';
import {PersistentDeviceStorage} from './assets/desktop/storage-consent.mjs';
import {makeKey,hash,signJws,verifyJws} from './network/crypto.mjs';
const f=window.hostFixture,TYPE='codi-device-host-test+jws';
f.DeviceHistoryHost=DeviceHistoryHost;f.PersistentDeviceStorage=PersistentDeviceStorage;
f.key=await makeKey();f.channel=await hash('shared host device journal');
f.payload=wire=>verifyJws(wire,f.key.publicKey,TYPE,500000);
f.verify=async(wire,{scope,channel,previous,signal})=>{
  signal?.throwIfAborted();const p=await f.payload(wire);
  if(p.scope!==scope||p.channel!==channel||p.head!==await hash(JSON.stringify([p.count,p.text])))throw Error('Wrong history scope or signed content');
  if(previous&&p.count>previous.floor.count&&p.previous!==previous.hash)throw Error('Wrong signed predecessor');
  return {channel:p.channel,revision:1,count:p.count,head:p.head};
};
f.packet=async(scope,count,text,previous)=>signJws({scope,channel:f.channel,count,text,previous,head:await hash(JSON.stringify([count,text]))},f.key.privateKey,TYPE);
f.desktop={windows:f.windows};surfaces.set("fixture",f.desktop);
f.open=app=>{
  const w={id:f.next++,app,title:app,workspace:1};f.windows.push(w);
  const node=document.createElement('section');node.className='window';node.dataset.window=w.id;
  node.append(publicAppContent(app,f.desktop,w));document.querySelector('#windows').append(node);return w.id;
};
f.node=id=>document.querySelector('[data-window="'+id+'"]');
f.close=id=>{const i=f.windows.findIndex(w=>w.id===id);if(i>=0)f.windows.splice(i,1);const node=f.node(id);if(node){disposePublicAppView(node);node.remove();}};
f.account=subject=>{
  for(const w of [...f.windows])if(w.app==='chat'||w.app==='rooms')f.close(w.id);
  currentSession={public:{kind:subject?'registered':'anonymous',sub:subject||crypto.randomUUID(),sid:crypto.randomUUID()}};
};
f.stats=async()=>({...(await desktopHistoryServices()).stats(),active:f.active,mounts:f.mounts,windows:f.windows.length});
f.closeAll=async()=>{for(const w of [...f.windows])f.close(w.id);(await desktopHistoryServices()).close();};
window.fixtureReady=true;
