import {PeerLink as ObservedPeerLink} from './network/peer.mjs';
import {hash,thumbprint,inspectJws} from './network/crypto.mjs';
import {DeviceMemberIntroductions,verifyDeviceMemberContact} from './network/device-member-introductions.mjs';
import {DeviceReplicaExchange} from './network/device-replica-exchange.mjs';
import {beginSession} from './network/identity.mjs';
import {loadApp,mountApp} from './assets/desktop/apps.mjs';
import {DeviceChannelSession} from './assets/desktop/device-channel-session.mjs';
import {DeviceChannelArchive} from './assets/desktop/channel-archive.mjs';
import {DeviceChannelDirectory} from './assets/desktop/channel-directory.mjs';
import {PersistentDeviceStorage} from './assets/desktop/storage-consent.mjs';
import {DeviceChannelKeys} from './assets/desktop/channel-keys.mjs';
import {DeviceReplica} from './network/device-replica.mjs';
import {DeviceReplicaRound} from './network/device-replica-round.mjs';
import {DeviceMemberChannel} from './network/device-member-channel.mjs';
import {createDeviceChannelPolicy,readDeviceChannelPolicy} from './network/device-channel-state.mjs';
const f=window.hostSessionCase;
// Tests may suppress autonomous topology while arranging exact authorization
// scenarios; inbound routing and native permission checks remain unmodified.
if(new URL(location.href).searchParams.has('manualpeers'))DeviceMemberIntroductions.prototype.maintain=function(){return Promise.resolve();};
const originalAttach=DeviceChannelSession.prototype.attach;DeviceChannelSession.prototype.attach=function(options){const value=originalAttach.call(this,options);if(f.mountingWindow)f.facades.set(f.mountingWindow,value);return value;};
currentSession=await beginSession(identityConfig,'anonymous',new URL(location.href).searchParams.get('side')||'owned session');
f.history=await desktopHistoryServices();const bind=f.history.bindChannelSession.bind(f.history);f.history.bindChannelSession=options=>{f.startCalls++;return bind(options).then(async owner=>{f.owners.push(owner);if(f.holdStart){f.held=true;await new Promise(resolve=>f.releaseStart=resolve);}return owner;});};
const wrap=f.history.wrapApp.bind(f.history);f.history.wrapApp=(app,options)=>wrap({mount:host=>{f.mountingWindow=host.w.id;try{return app.mount(host);}finally{f.mountingWindow=null;}}},options);f.desktop={windows:[]};
f.open=app=>{const id=f.next++,w={id,app,title:app},node=document.createElement('section');node.dataset.window=id;node.className='window';document.querySelector('#windows').append(node);f.windows.set(id,{w,node,instance:null});if(typeof publicAppContent==='function'){f.desktop.windows.push(w);node.append(publicAppContent(app,f.desktop,w));return id;}(async()=>{
 try{const module=await loadApp(app);if(!f.windows.has(id))return;const real={mount:host=>{f.mountingWindow=id;try{return module.mount(host);}finally{f.mountingWindow=null;}}},base={version:2,w,ui:{make,textButton,appInput:(label)=>{const n=make('input');n.setAttribute('aria-label',label);return n;}},session:()=>currentSession,storage:{downloadGuestFile(){}},network:desktopNetwork.appContext()};
 const appModule=['chat','rooms'].includes(app)?f.history.wrapApp(real,{mountApp,issuer:identityConfig.identity.issuer,feature:app,beforeMount:async({session,signal})=>{if(await desktopNetwork.initialize(session,identityConfig,{signal})===false)throw Error('Device session unavailable');}}):real;
 const instance=mountApp(appModule,base);if(!f.windows.has(id)){instance.dispose('Owned window closed while loading');return;}f.windows.get(id).instance=instance;node.append(instance.element);
 }catch(e){node.textContent=e.stack;f.error=e.stack;}
})();return id;};
f.node=id=>f.windows.get(id)?.node;
f.close=id=>{const row=f.windows.get(id);if(!row)return;if(typeof disposePublicAppView==='function'){const i=f.desktop.windows.indexOf(row.w);if(i>=0)f.desktop.windows.splice(i,1);disposePublicAppView(row.node,'Owned app window closed');}else row.instance?.dispose('Owned app window closed');row.node.remove();f.windows.delete(id);};
f.captureConfig=async id=>{const view=f.facades.get(id),configs=await view.channels();return configs[0];};
f.owner=()=>f.owners.at(-1);
f.stats=async()=>({history:f.history.stats(),network:await desktopNetwork.stats(),windows:f.windows.size});
f.holdEnqueue=()=>{const original=DeviceChannelArchive.prototype.enqueue;f.enqueueHeld=false;DeviceChannelArchive.prototype.enqueue=async function(...args){const result=await original.apply(this,args);f.enqueueHeld=true;await new Promise(resolve=>f.releaseEnqueue=resolve);return result;};f.restoreEnqueue=()=>DeviceChannelArchive.prototype.enqueue=original;};
f.probePeerNode=async(config,cid)=>{const owner=f.owner(),receive=owner.receive.bind(owner),request_id=crypto.randomUUID().replaceAll('-',''),entry=desktopNetwork.appContext().pool.firstReady();return new Promise((resolve,reject)=>{let settled=false;const done=(fn,v)=>{if(settled)return;settled=true;clearTimeout(timer);owner.receive=receive;fn(v);},timer=setTimeout(()=>done(reject,Error('Owned peer probe timeout')),5000);owner.receive=(e,a)=>{if(a.body?.request_id===request_id&&a.body.op==='data')hash(a.body.wire).then(value=>done(resolve,value===cid),error=>done(reject,error));return receive(e,a);};entry.link.sendDeviceApplication({op:'get',request_id,channel:config.channel,genesisHash:config.genesisHash,node:cid}).catch(e=>done(reject,e));});};
f.holdSnapshots=async(id,config)=>{const h=await f.facades.get(id).openChannel(config,config.actor),original=DeviceChannelArchive.prototype.load;f.snapshotLoads=0;f.snapshotHeld=false;const barrier=new Promise(resolve=>f.releaseSnapshots=resolve);DeviceChannelArchive.prototype.load=async function(...args){f.snapshotLoads++;const value=await original.apply(this,args);f.snapshotHeld=true;await barrier;return value;};f.snapshotResult=null;Promise.all(Array.from({length:20},()=>h.snapshot())).then(values=>f.snapshotResult={same:values.every(v=>v===values[0]),frozen:values.every(v=>Object.isFrozen(v)&&Object.isFrozen(v.state)&&Object.isFrozen(v.state.messages))},e=>f.snapshotResult={error:e.message}).finally(()=>DeviceChannelArchive.prototype.load=original);};
f.setBinding=b=>{currentSession.public={...currentSession.public,...b};};
f.closeAll=async()=>{for(const id of [...f.windows.keys()])f.close(id);desktopNetwork.close();await Promise.allSettled(f.owners.map(o=>o.idle()));f.history.close();return f.stats();};
f.public=()=>currentSession.public;
f.holdReplicaCommit=()=>{const original=DeviceReplica.prototype.commit;let held=false;f.commitHeld=false;const barrier=new Promise(resolve=>f.releaseCommit=resolve);DeviceReplica.prototype.commit=async function(...args){const vote=await original.apply(this,args);if(!held){held=true;f.commitHeld=true;await barrier;}return vote;};f.restoreCommit=()=>DeviceReplica.prototype.commit=original;};
f.holdOldPendingSnapshot=handle=>{
 const original=DeviceChannelArchive.prototype.pending;let held=false;f.pendingSnapshotHeld=false;f.oldPendingResult=null;const barrier=new Promise(resolve=>f.releaseOldPending=resolve);
 DeviceChannelArchive.prototype.pending=async function(...args){const rows=await original.apply(this,args);if(!held){held=true;f.pendingSnapshotHeld=true;await barrier;}return rows;};
 handle.snapshot().then(value=>f.oldPendingResult={pending:value.pending.length},e=>f.oldPendingResult={error:e.message}).finally(()=>DeviceChannelArchive.prototype.pending=original);
};
f.holdShortcutRestore=(view,channel)=>{
 const original=DeviceChannelDirectory.prototype.get;let held=false;f.shortcutHeld=false;f.shortcutResult=null;
 const barrier=new Promise(resolve=>f.releaseShortcut=resolve);
 DeviceChannelDirectory.prototype.get=async function(...args){const row=await original.apply(this,args);if(args[0]===channel&&!held){held=true;f.shortcutHeld=true;await barrier;}return row;};
 view.restoreChannel(channel).then(async h=>f.shortcutResult={height:(await h.snapshot()).height},e=>f.shortcutResult={error:e.message}).finally(()=>DeviceChannelDirectory.prototype.get=original);
};
f.directoryCases=async()=>{
 const checks=[],check=(name,ok)=>{if(!ok)throw Error(name);checks.push(name);},policy=new PersistentDeviceStorage(),permit=await policy.acquire(),keys=await new DeviceChannelKeys().open(permit),scope='owned-directory-cases',made=[];
 const keyAPI={get:(c,o)=>keys.get(scope,c,o),sign:(c,p,b,o)=>keys.sign(scope,c,p,b,o)};
 const directory=await new DeviceChannelDirectory({scope,keys:keyAPI,maxScopeEntries:3}).open(permit);
 const raw=(mode,job)=>new Promise((resolve,reject)=>{const q=indexedDB.open('codi-device-channel-directory-v1',1);q.onerror=()=>reject(q.error);q.onsuccess=()=>{const db=q.result,tx=db.transaction(['channels','scopes','accounting'],mode,mode==='readwrite'?{durability:'strict'}:undefined);let value;tx.oncomplete=()=>{db.close();resolve(value);};tx.onabort=()=>{db.close();reject(tx.error);};job(tx,v=>value=v);};});
 const audit=()=>raw('readonly',(tx,done)=>{const rows={};for(const name of ['channels','scopes','accounting']){const q=tx.objectStore(name).getAll();q.onsuccess=()=>{rows[name]=q.result;if(Object.keys(rows).length===3)done(JSON.stringify(rows));};}});
 const before=await audit();
 try{
  for(let i=0;i<4;i++){const key=await keys.create(scope,{label:'Directory test '+i});made.push(key);const policyWire=await createDeviceChannelPolicy(keyAPI,key.channel),p=await readDeviceChannelPolicy(policyWire,{channel:key.channel});made[i]={...key,policyWire,genesisHash:p.genesisHash};if(i<3)await directory.remember(made[i],key.channel,{label:'Directory '+i});}
  const first=await directory.list({limit:1}),second=await directory.list({limit:1,after:first.next}),third=await directory.list({limit:1,after:second.next});check('native channel directory pages have no duplicate or skipped bookmarks',new Set([...first.entries,...second.entries,...third.entries].map(v=>v.channel)).size===3&&third.next===null);
  const saved=await directory.get(made[0].channel),idem=await directory.remember(made[0],made[0].channel,{label:'Ignored existing label'});check('idempotent remembering preserves exact bookmark version and label',idem.version===saved.version&&idem.label===saved.label);
  const renewedPolicy=await createDeviceChannelPolicy(keyAPI,saved.channel),renewed=await readDeviceChannelPolicy(renewedPolicy,{channel:saved.channel}),same=await directory.remember({...saved,policyWire:renewedPolicy},saved.actor);check('another valid signature of the same pinned policy retains the first bookmark unchanged',renewedPolicy!==saved.policyWire&&renewed.genesisHash===saved.genesisHash&&same.policyWire===saved.policyWire&&same.version===saved.version);
  let denied=false;try{await directory.remember(made[0],made[1].channel);}catch(e){denied=e.name==='DeviceDirectoryConflict';}check('bookmark cannot silently rebind to another local author',denied&&(await directory.get(saved.channel)).actor===saved.actor);
  denied=false;try{await directory.remember(made[3],made[3].channel);}catch(e){denied=e.name==='DeviceDirectoryCapacity';}check('directory capacity refuses atomically without changing existing bookmarks',denied&&(await directory.list()).entries.length===3&&await directory.get(made[3].channel)===null);
  const race=await Promise.allSettled([directory.rename(saved.channel,'First view',{expected:saved.version}),directory.rename(saved.channel,'Second view',{expected:saved.version})]);check('two racing bookmark edits have exactly one native CAS winner',race.filter(v=>v.status==='fulfilled').length===1&&race.filter(v=>v.status==='rejected'&&v.reason.name==='DeviceDirectoryConflict').length===1);
  const current=await directory.get(saved.channel),baseline=await audit(),put=IDBObjectStore.prototype.put;let aborted=false;
  IDBObjectStore.prototype.put=function(...args){const q=put.apply(this,args);if(this.transaction.db.name==='codi-device-channel-directory-v1'&&this.name==='scopes'&&args[0].key===scope&&!aborted){aborted=true;this.transaction.abort();}return q;};denied=false;try{await directory.rename(current.channel,'Aborted rename',{expected:current.version});}catch{denied=true;}finally{IDBObjectStore.prototype.put=put;}
  check('actual directory transaction abort preserves bookmark and all quota counters',denied&&aborted&&baseline===await audit());
  let original;await raw('readwrite',(tx,done)=>{const st=tx.objectStore('channels'),q=st.get([scope,current.channel]);q.onsuccess=()=>{original=q.result;st.put({...original,genesisHash:'A'.repeat(43)});done(true);};});denied=false;try{await directory.get(current.channel);}catch{denied=true;}check('corrupt native bookmark is refused without deleting saved data',denied);const recoveredList=await directory.list();check('a corrupt shortcut is quarantined while other saved channels remain discoverable',recoveredList.entries.length===2&&recoveredList.unavailable.length===1&&recoveredList.unavailable[0].channel===current.channel);
  await raw('readwrite',(tx,done)=>{tx.objectStore('channels').put(original);done(true);});
  const wrong={...original,genesisHash:await hash('different pinned genesis')};wrong.identityHash=await hash(JSON.stringify([wrong.scope,wrong.channel,wrong.genesisHash,wrong.policyWire,wrong.actor]));await raw('readwrite',(tx,done)=>{tx.objectStore('channels').put(wrong);done(true);});denied=false;try{await directory.get(current.channel);}catch(e){denied=e.message.includes('pinned genesis');}check('even a recomputed metadata checksum cannot authorize a different pinned policy',denied);await raw('readwrite',(tx,done)=>{tx.objectStore('channels').put(original);done(true);});
  const other=await new DeviceChannelDirectory({scope:'other-owned-directory-scope',keys:keyAPI}).open(permit);try{check('directory list and direct lookups stay in their captured account scope',(await other.list()).entries.length===0&&await other.get(current.channel)===null);}finally{other.close();}
  denied=false;try{await directory.forget(current.channel,{expected:saved.version});}catch(e){denied=e.name==='DeviceDirectoryConflict';}check('stale shortcut removal cannot delete the current bookmark',denied&&!!await directory.get(current.channel));
 }finally{
  for(const entry of (await directory.list()).entries)await directory.forget(entry.channel,{expected:entry.version});
  for(const key of made)await keys.remove(scope,key.channel,{expected:await hash(key.genesis)});
  check('explicit test shortcut cleanup returns native directory accounting to baseline',before===await audit());directory.close();keys.close();policy.close();
 }
 return checks;
};
window.fixtureReady=true;

f.falseRepair=async()=>{const original=DeviceReplicaRound.prototype.invoke,block=structuredClone((await f.group.history({limit:1})).entries[0].block),current=await f.group.snapshot();block.header.height=current.height+1;block.header.parent=current.head;f.badHistoryReads=0;DeviceReplicaRound.prototype.invoke=async function(method,...args){if(method==='history'){f.badHistoryReads++;return {block};}const result=await original.call(this,method,...args);if(method==='status')return {...result,position:{...result.position,height:result.position.height+1}};return result;};f.restoreFalseRepair=()=>DeviceReplicaRound.prototype.invoke=original;};
f.copyPromise=wire=>{const original=DeviceReplicaRound.prototype.invoke;f.copiedPromiseReplies=0;DeviceReplicaRound.prototype.invoke=async function(method,...args){const result=await original.call(this,method,...args);if(method==='status'){f.copiedPromiseReplies++;return {...result,round:1000000,viewChange:wire};}return result;};f.restoreCopiedPromise=()=>DeviceReplicaRound.prototype.invoke=original;};

// Observe real native authorization decisions without replacing their result.
f.memberAuth=[];f.syncFailures=[];
const observedMemberSync=DeviceMemberChannel.prototype.sync;
DeviceMemberChannel.prototype.sync=async function(...args){try{return await observedMemberSync.apply(this,args);}catch(error){f.syncFailures.push({name:error.name,message:error.message,at:Math.round(performance.now())});if(f.syncFailures.length>8)f.syncFailures.shift();throw error;}};
f.freezeMemberSync=()=>{const previous=DeviceMemberChannel.prototype.sync;DeviceMemberChannel.prototype.sync=async function(){throw Error('Fixture holds this member at its current accepted floor');};f.restoreMemberSync=()=>{DeviceMemberChannel.prototype.sync=previous;};};
f.scratchStats=async()=>{if(!(await indexedDB.databases()).some(v=>v.name==='codi-device-download-cache-v1'))return null;return new Promise((resolve,reject)=>{const open=indexedDB.open('codi-device-download-cache-v1');open.onerror=()=>reject(open.error);open.onsuccess=()=>{const db=open.result,tx=db.transaction(['accounting','jobs'],'readonly'),a=tx.objectStore('accounting').get('totals'),j=tx.objectStore('jobs').getAll();tx.oncomplete=()=>{db.close();resolve({totals:a.result,jobs:j.result.map(v=>({key:v.key,height:v.offer.height,nodeCount:v.nodeCount,nodeBytes:v.nodeBytes}))});};tx.onabort=()=>{db.close();reject(tx.error);};};});};
const memberAuthorize=DeviceMemberChannel.prototype.authorize;
DeviceMemberChannel.prototype.authorize=async function(actor,options){try{return await memberAuthorize.call(this,actor,options);}catch(error){if(f.memberAuth.length<256)f.memberAuth.push({actor,method:options?.method,error:error.message});throw error;}};
f.holdMemberNode=actor=>{
 const invoke=DeviceMemberChannel.prototype.invoke;f.memberNodeHeld=false;f.memberNodeHolds=[];let active=true,release;
 const barrier=new Promise(resolve=>release=resolve);f.releaseMemberNode=()=>{active=false;release();};
 DeviceMemberChannel.prototype.invoke=async function(method,...args){
  const value=await invoke.call(this,method,...args);
  // Hold retries too: a timeout must not let another request deliver the same
  // content while the test is still arranging the accepted revocation.
  if(active&&method==='node'&&args[1]?.actor===actor){
   f.memberNodeHeld=true;if(f.memberNodeHolds.length<32)f.memberNodeHolds.push({cid:args[0].cid,at:Math.round(performance.now())});
   const signal=args[1].signal;let abort;
   try{signal?.throwIfAborted();await Promise.race([barrier,new Promise((_,reject)=>{abort=()=>reject(signal.reason);signal?.addEventListener('abort',abort,{once:true});})]);signal?.throwIfAborted();}
   finally{if(abort)signal?.removeEventListener('abort',abort);}
  }
  return value;
 };
 f.restoreMemberNode=()=>{f.releaseMemberNode();DeviceMemberChannel.prototype.invoke=invoke;};
};

// Bounded test observations keep the real native verifier and RPC path intact.
f.memberTrace=[];const traceMember=row=>{f.memberTrace.push({...row,at:Math.round(performance.now())});if(f.memberTrace.length>64)f.memberTrace.shift();};
const observedMemberInvoke=DeviceMemberChannel.prototype.invoke;
DeviceMemberChannel.prototype.invoke=async function(method,value,options){try{if(method==='submit'&&f.rejectNextMemberSubmitFor===options?.actor){f.rejectNextMemberSubmitFor=null;f.rejectedMemberSubmits=(f.rejectedMemberSubmits||0)+1;throw Error('Controlled one-shot member submit refusal');}if(method==='head'&&f.rejectNextMemberHeadFor===options?.actor){f.rejectNextMemberHeadFor=null;f.rejectedMemberHeads=(f.rejectedMemberHeads||0)+1;throw Error('Controlled one-shot member head refusal');}const result=await observedMemberInvoke.call(this,method,value,options);if(method==='notice')traceMember({direction:'in',method,value,from:options?.peer?.link.remoteIdentity?.name});return result;}catch(error){if(['notice','node','head'].includes(method))traceMember({direction:'in',method,value,error:error.message});throw error;}};
f.introductions=[];f.topologyFailures=[];
const topologyInvoke=DeviceMemberIntroductions.prototype.invoke;
DeviceMemberIntroductions.prototype.invoke=async function(method,value,options){try{const result=await topologyInvoke.call(this,method,value,options);if(f.poisonContacts&&method==='peers'){const bad=structuredClone(result.self);bad.identity.sid=crypto.randomUUID();return {...result,contacts:[bad]};}return result;}catch(error){if(f.topologyFailures.length<128)f.topologyFailures.push({request:value?.request,error:error.message});throw error;}};
const memberCall=DeviceReplicaExchange.prototype.call;
DeviceReplicaExchange.prototype.call=function(entry,pins,method,value,options){if(this.stats().profile==='member')f.memberExchange=this;let captured;if(this.stats().profile==='member'&&method==='introduce'&&value.operation==='offer'&&f.introductions.length<32){captured={exchange:this,entry,pins:structuredClone(pins),value:structuredClone(value),answered:false};f.introductions.push(captured);}const task=memberCall.call(this,entry,pins,method,value,options);if(captured)task.then(()=>captured.answered=true,()=>{});if(this.stats().profile==='member'&&['notice','head'].includes(method))task.then(result=>traceMember({direction:'out',method,value,to:entry.link.remoteIdentity?.name,result}),error=>traceMember({direction:'out',method,value,to:entry.link.remoteIdentity?.name,error:error.message}));return task;};
f.contactCases=async()=>{
 const permit=await f.history.permit(),vault=await new DeviceChannelKeys().open(permit),scope=f.owner().scope,pins=await f.group.snapshot(),actor=pins.actor,t=Math.floor(Date.now()/1000),identity=structuredClone(currentSession.public),base={profile:'codi-device-member-contact/1',channel:pins.channel,genesisHash:pins.genesisHash,sid:identity.sid,key:await thumbprint(identity.key),issued:t,expires:t+120},proof=body=>vault.sign(scope,actor,'member.grant',body),checks=[];
 const denied=async(contact,otherPins=pins)=>{try{await verifyDeviceMemberContact(contact,otherPins,identityConfig.identity);return false;}catch{return true;}};
 try{
  const good={identity,proof:await proof(base)};checks.push(['a durable contact binds the real native actor to its current transport key',(await verifyDeviceMemberContact(good,pins,identityConfig.identity)).actor===actor]);
  checks.push(['an expired genuinely signed contact grants no introduction',await denied({identity,proof:await proof({...base,issued:t-130,expires:t-10})})]);
  checks.push(['a future genuinely signed contact is rejected',await denied({identity,proof:await proof({...base,issued:t+60,expires:t+120})})]);
  checks.push(['a contact cannot be replayed into another pinned channel',await denied(good,{...pins,genesisHash:'A'.repeat(43)})]);
  checks.push(['a relay cannot substitute another transport identity into a signed contact',await denied({...good,identity:{...identity,sid:crypto.randomUUID()}})]);
  return checks;
 }finally{vault.close();}
};
// Fixture-only signed routing probes against the real retained channel keys.
f.routeContact=async()=>{
 const permit=await f.history.permit(),vault=await new DeviceChannelKeys().open(permit),scope=f.owner().scope,pins=await f.group.snapshot(),actor=pins.actor,t=Math.floor(Date.now()/1000),identity=structuredClone(currentSession.public);
 try{return {identity,proof:await vault.sign(scope,actor,'member.grant',{profile:'codi-device-member-contact/1',channel:pins.channel,genesisHash:pins.genesisHash,sid:identity.sid,key:await thumbprint(identity.key),issued:t,expires:t+120})};}finally{vault.close();}
};
f.routeProbe=async(to,via,peerId)=>{
 const permit=await f.history.permit(),vault=await new DeviceChannelKeys().open(permit),scope=f.owner().scope,pins=await f.group.snapshot(),actor=pins.actor,pool=desktopNetwork.appContext().pool,entry=pool.get(peerId),request=crypto.randomUUID().replaceAll('-',''),t=Math.floor(Date.now()/1000);let offer;
 try{
  const from=await f.routeContact();offer=await pool.offer();const target=inspectJws(to.proof,'codi-device-channel-key-proof+jws',8192).payload.channel;
  const proof=await vault.sign(scope,actor,'member.grant',{profile:'codi-device-member-introduction/1',channel:pins.channel,genesisHash:pins.genesisHash,request,kind:'offer',from:from.identity.sid,to:to.identity.sid,target,signal:await hash(offer.token),issued:t,expires:t+30});
  try{await f.memberExchange.call(entry,pins,'introduce',{operation:'offer',request,from,to,signal:offer.token,proof,via});return {refused:false};}catch(error){return {refused:true,error:error.message};}
 }finally{if(offer)pool.closeEntry(offer.entry.id,'Fixture probe complete');vault.close();}
};
// Hold only fixture topology requests so a real archive RPC can be exercised
// while the routing lane is full. Normal channel authorization remains active.
f.holdRouting=()=>{const prior=DeviceMemberChannel.prototype.invoke,held=[];f.routingHeld=held;f.releaseRouting=()=>{DeviceMemberChannel.prototype.invoke=prior;for(const release of held.splice(0))release();};DeviceMemberChannel.prototype.invoke=async function(method,value,options){if(method==='peers')await new Promise((resolve,reject)=>{const abort=()=>reject(options.signal.reason||Error('Fixture routing cancelled'));options.signal.addEventListener('abort',abort,{once:true});held.push(()=>{options.signal.removeEventListener('abort',abort);resolve();});});return prior.call(this,method,value,options);};};
f.startRoutingBurst=async peerId=>{const contact=await f.routeContact(),pins=await f.group.snapshot(),entry=desktopNetwork.appContext().pool.get(peerId);f.routingBurst=Array.from({length:4},()=>f.memberExchange.call(entry,pins,'peers',{contact,refresh:false}).then(()=>true,()=>false));};
f.finishRoutingBurst=()=>Promise.all(f.routingBurst);
f.replayIntroduction=async()=>{
 const captured=f.introductions.find(p=>p.answered&&!p.entry.link.closed&&desktopNetwork.appContext().pool.list().some(e=>e.peerId===p.value.to.identity.sid&&desktopNetwork.appContext().pool.get(e.id).link.deviceMemberReady));if(!captured)throw Error('No captured live introduction relay');const value=structuredClone(captured.value),permit=await f.history.permit(),vault=await new DeviceChannelKeys().open(permit),actor=inspectJws(value.from.proof,'codi-device-channel-key-proof+jws',8192).payload.channel;
 try{const body=inspectJws(value.proof,'codi-device-channel-key-proof+jws',8192).payload.body,t=Math.floor(Date.now()/1000);value.proof=await vault.sign(f.owner().scope,actor,'member.grant',{...body,issued:t,expires:t+30});await captured.exchange.bind(captured.entry,captured.pins);let refused=false;try{await memberCall.call(captured.exchange,captured.entry,captured.pins,'introduce',value);}catch{refused=true;}return {refused,request:value.request};}finally{vault.close();}
};

f.badInlineRead=async()=>{
 const peer=(await f.group.memberPeers()).find(p=>desktopNetwork.appContext().pool.get(p.peerId)?.link.deviceInlineValuesReady);if(!peer)throw Error('No inline-capable member');const entry=desktopNetwork.appContext().pool.get(peer.peerId),send=entry.link.sendDeviceMember.bind(entry.link),config=(await f.view.channels())[0];let changed=false;
 entry.link.sendDeviceMember=(body,lane)=>{if(!changed&&body.op==='call'&&typeof body.value?.wire==='string'){changed=true;body={...body,value:{...body.value,wire:body.value.wire+' '}};}return send(body,lane);};
 try{let refused=false;try{await f.memberExchange.call(entry,config,'head',{});}catch{refused=true;}return {refused,changed,to:entry.peerId};}finally{entry.link.sendDeviceMember=send;}
};

f.linkStateHistory=new WeakMap();const observedState=ObservedPeerLink.prototype.state;
ObservedPeerLink.prototype.state=function(name,detail){const rows=f.linkStateHistory.get(this)||[];rows.push({name,sentHello:this.sentHello,receivedHello:this.receivedHello,caller:new Error().stack.split('\n').slice(1,5).join('\n')});if(rows.length>8)rows.shift();f.linkStateHistory.set(this,rows);return observedState.call(this,name,detail);};
