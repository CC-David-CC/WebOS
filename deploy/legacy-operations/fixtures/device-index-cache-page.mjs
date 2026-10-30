import {DeviceChannelArchive} from '../../assets/desktop/channel-archive.mjs';
import {DeviceChannelDownloadCache} from '../../assets/desktop/channel-download-cache.mjs';
import {DeviceOperationTree,DeviceOperationTreeVerifier} from '../../network/device-operation-tree.mjs';
import {DeviceReplica,deviceReplicaLeader} from '../../network/device-replica.mjs';
import {DeviceChannelKeys} from '../../assets/desktop/channel-keys.mjs';
import {PersistentDeviceStorage,mountDeviceStorageGate} from '../../assets/desktop/storage-consent.mjs';
import * as protocol from '../../network/device-channel-state.mjs';
import {operationSetEmpty,operationSetNode,operationSetLeaf} from '../../network/device-operation-set.mjs';
import {hash,unb64} from '../../network/crypto.mjs';
const encLength=v=>new TextEncoder().encode(v).length;
const checks=[],scope='owned-archive-account',policy=new PersistentDeviceStorage(),life=new AbortController(),owned=new Set();let vault,keys,config,archive;
const make=(tag,classes,text)=>{const n=document.createElement(tag);n.className=classes;n.textContent=text??'';return n;};
const check=(name,ok)=>{if(!ok)throw Error(name);checks.push(name);};
const refuses=async(fn,needle)=>{try{await fn();return false;}catch(e){if(needle&&!e.message.includes(needle))throw e;return true;}};
async function openKeys(){vault=await new DeviceChannelKeys().open(await policy.acquire());owned.add(vault);keys={create:o=>vault.create(scope,o),get:(actor,o)=>vault.get(scope,actor,o),sign:(actor,purpose,body,o)=>vault.sign(scope,actor,purpose,body,o)};}
async function openArchive(options={}){const a=new DeviceChannelArchive({keys,scope,...config,...options});owned.add(a);return a.open(await policy.acquire());}
async function raw(work){const db=await new Promise((resolve,reject)=>{const q=indexedDB.open('codi-device-channel-archive-v1',1);q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error);});try{return await new Promise((resolve,reject)=>{const tx=db.transaction(['nodes','heads','pending','accounting'],'readwrite',{durability:'strict'});let result;tx.oncomplete=()=>resolve(result);tx.onabort=()=>reject(tx.error);work(tx,v=>result=v);});}finally{db.close();}}
// Independent full-level oracle for a small test set only. Production tests
// below use the compact node provider and actual IndexedDB archive.
async function oracle(ids){
 const zero=await operationSetEmpty(),index=id=>BigInt('0x'+[...unb64(id)].map(v=>v.toString(16).padStart(2,'0')).join(''));let map=new Map();for(const id of ids)map.set(index(id),await operationSetLeaf(id));
 for(let d=0;d<256;d++){const next=new Map();for(const n of new Set([...map.keys()].map(k=>k>>1n)))next.set(n,await operationSetNode(map.get(n<<1n)||zero[d],map.get((n<<1n)|1n)||zero[d]));map=next;}return map.get(0n)||zero[256];
}
async function treeChecks(){
 const stored=new Map();let reads=0;const tree=new DeviceOperationTree({get:async cid=>{reads++;return stored.get(cid);},put:async(cid,wire)=>stored.set(cid,wire)}),ids=['A'.repeat(43),'_'.repeat(42)+'8'];for(let i=0;i<18;i++)ids.push(await hash('owned-tree-item-'+i));let root=null;
 for(const id of ids){const next=await tree.insert(root,id);for(const cid of next.obsolete)stored.delete(cid);root=next.link;}
 check('compact tree matches an independent sparse oracle including opposite key extremes',await tree.root(root)===await oracle(ids));
 check('obsolete branch pruning retains exactly two nodes per accepted ID minus one',stored.size===2*ids.length-1);
 reads=0;await tree.witness(root,await hash('new independent target'));check('a witness loads only a compact binary path instead of the full ID history',reads<=20);
 check('the compact provider refuses an already accepted original ID',await refuses(()=>tree.witness(root,ids[4]),'already accepted'));
 const second=new Map(),other=new DeviceOperationTree({get:async cid=>second.get(cid),put:async(cid,wire)=>second.set(cid,wire)});let reordered=null;
 for(const id of [...ids].reverse())reordered=(await other.insert(reordered,id)).link;
 check('content root and sparse accepted-set root are independent of insertion order',reordered.cid===root.cid&&await other.root(reordered)===await tree.root(root));
 const wire=stored.get(root.cid);stored.set(root.cid,wire+' ');check('corrupt graph bytes are rejected before a witness is produced',await refuses(async()=>tree.witness(root,await hash('new independent target')),'hash mismatch'));stored.set(root.cid,wire);
 stored.delete(root.cid);check('missing graph chunks fail explicitly without an implicit server fetch',await refuses(async()=>tree.witness(root,await hash('new independent target')),'Missing operation-tree'));
}
async function begin(){
 await openKeys();const people=[];for(let i=0;i<4;i++)people.push(await keys.create({label:'Archive replica '+i}));const actor=people[0].channel;
 const policyWire=await protocol.createDeviceChannelPolicy(keys,actor,{validators:people.map(v=>v.channel),publicWrite:true}),p=await protocol.readDeviceChannelPolicy(policyWire,{channel:actor});
 config={actor,channel:actor,genesisHash:p.genesisHash,policyWire,actors:[...p.validators]};archive=await openArchive();
 const original=await protocol.createDeviceChannelProposal(keys,actor,actor,'chat',{text:'Original pending message survives browser death. '+ 'z'.repeat(4000)}),saved=await archive.enqueue(original);
 window.crashPublic={config,original,id:saved.id};window.pendingPhase='durable-original';
}
async function certify(at,records){
 const candidate=await protocol.prepareDeviceChannelBlock(at,records),p=protocol.deviceChannelPolicy(at),prepare=[],commit=[];
 for(const actor of p.validators.slice(0,p.quorum)){prepare.push(await keys.sign(actor,'checkpoint',await protocol.deviceChannelVoteBody(p,candidate.header,'prepare')));commit.push(await keys.sign(actor,'checkpoint',await protocol.deviceChannelVoteBody(p,candidate.header,'commit')));}
 return protocol.materializeDeviceChannelBlock(candidate,prepare,commit);
}
async function finish(retained){
 config=retained.config;await openKeys();archive=await openArchive();let pending=await archive.pending();
 check('an original signed pending message survives actual browser SIGKILL unchanged',pending.length===1&&pending[0].id===retained.id&&pending[0].wire===retained.original);
 check('pending status claims only device storage rather than accepted delivery',pending[0].status==='pending-on-device');
 check('repeated enqueue keeps the first exact original and one accounting row',(await archive.enqueue(retained.original)).idempotent&&(await archive.stats()).pending===1);
 await treeChecks();const p=await protocol.readDeviceChannelPolicy(config.policyWire,config),replicas=new Map();
 for(const actor of config.actors){const r=await new DeviceReplica({keys,scope,...config,actor}).open(await policy.acquire());owned.add(r);replicas.set(actor,r);}
 const leader=deviceReplicaLeader(p,1,0),r=replicas.get(leader),record=await archive.record(retained.original),proposal=await r.propose([record]),prepare=[];
 for(const actor of config.actors.slice(0,p.quorum))prepare.push((await replicas.get(actor).prepare(proposal.proposal)).prepareVote);
 const cert={header:proposal.proposal.header,prepare},commit=[];for(const actor of config.actors.slice(0,p.quorum))commit.push(await replicas.get(actor).commit(cert));
 const block={header:cert.header,operations:[record],prepare,commit};
 const saved=await archive.acceptReplica(r,block);check('real durable replica votes feed a full archive commit before retiring prepared bytes',saved.position.count===1&&(await r.status()).position.head===saved.position.head);
 check('accepted pin, complete signed block and pending removal commit together',(await archive.pending()).length===0&&(await archive.history()).entries[0].block.operations[0].proposal===retained.original);
 const firstNode=JSON.parse(await archive.readNode(saved.history)),firstBlob=JSON.parse(await archive.readNode(firstNode.block));check('a large signed block is stored and reconstructed through multiple hashed chunks',encLength(JSON.stringify(block))>8192&&firstBlob.tree.height===1&&(await archive.history()).entries[0].block.operations[0].proposal===retained.original);
 const before=await archive.stats();check('repeating the same accepted archive commit is idempotent',(await archive.append(block)).idempotent&&JSON.stringify(await archive.stats())===JSON.stringify(before));
 const resumed=await openArchive(),restored=await resumed.load();check('a fresh archive handle restores the quorum checkpoint and accepted index',restored.position.head===saved.position.head&&restored.checkpoint===saved.checkpoint);resumed.close();
 check('a restored accepted operation cannot be inserted a second time',await refuses(()=>archive.record(retained.original),'already accepted'));
 check('an already accepted original cannot become a new pending entry',await refuses(()=>archive.enqueue(retained.original),'already accepted')&&(await archive.pending()).length===0);
 const outsider=await keys.create({label:'Another account author'}),foreign=await protocol.createDeviceChannelProposal(keys,outsider.channel,config.channel,'chat',{text:'Foreign queue attempt'});
 check('another signing identity cannot enter this author pending queue',await refuses(()=>archive.enqueue(foreign),'Only this account author'));
 const otherScope='separate-archive-account',otherKeys={get:(actor,o)=>vault.get(otherScope,actor,o),sign:(actor,purpose,body,o)=>vault.sign(otherScope,actor,purpose,body,o)};
 check('another account cannot reopen the private author or its archive',await refuses(async()=>new DeviceChannelArchive({keys:otherKeys,scope:otherScope,...config}).open(await policy.acquire()),'private author key'));
 // Native abort AFTER the queued writes: no orphan graph nodes, accepted pin
 // or outbox acknowledgement may escape the aborted native transaction.
 const nextOriginal=await protocol.createDeviceChannelProposal(keys,config.actor,config.channel,'chat',{text:'Keep pending across atomic archive abort'});await archive.enqueue(nextOriginal);const nextRecord=await archive.record(nextOriginal),nextBlock=await certify(saved.position,[nextRecord]),priorStats=await archive.stats(),priorPin=(await archive.load()).hash;
 const originalPut=IDBObjectStore.prototype.put;let aborted=false;
 IDBObjectStore.prototype.put=function(value,...args){const q=originalPut.call(this,value,...args);if(this.name==='heads'&&!aborted){aborted=true;this.transaction.abort();}return q;};
 try{check('actual native archive abort refuses the staged block',await refuses(()=>archive.append(nextBlock)));}finally{IDBObjectStore.prototype.put=originalPut;}
 check('aborted graph/pin/outbox transaction leaves no orphan nodes or acknowledgement',aborted&&(await archive.load()).hash===priorPin&&JSON.stringify(await archive.stats())===JSON.stringify(priorStats)&&(await archive.pending())[0].wire===nextOriginal);
 r.close();check('replica closure after archive commit does not roll back saved history',await refuses(()=>archive.acceptReplica(r,nextBlock),'closed')&&(await archive.load()).position.count===2&&(await archive.pending()).length===0);
 const recovered=await new DeviceReplica({keys,scope,...config,actor:leader}).open(await policy.acquire());owned.add(recovered);await recovered.sync((await archive.load()).checkpoint);check('a reopened replica repairs from the already committed archive checkpoint',(await recovered.status()).position.count===2);
 const mutable=structuredClone(nextBlock),same=archive.append(mutable);mutable.operations[0].proposal='changed after call';check('archive snapshots caller input before its first asynchronous permission check',(await same).idempotent);
 // Capacity exhaustion must preserve the committed head and original pending
 // record. It must not consume votes or block independent desktop tools.
 const smallRoot=await keys.create({label:'Small history budget'}),smallWire=await protocol.createDeviceChannelPolicy(keys,smallRoot.channel),smallPolicy=await protocol.readDeviceChannelPolicy(smallWire,{channel:smallRoot.channel}),smallConfig={actor:smallRoot.channel,channel:smallRoot.channel,genesisHash:smallPolicy.genesisHash,policyWire:smallWire};
 const small=new DeviceChannelArchive({keys,scope,...smallConfig,maxChannelPending:1});owned.add(small);await small.open(await policy.acquire());
 const s1=await protocol.createDeviceChannelProposal(keys,smallConfig.actor,smallConfig.channel,'chat',{text:'First small pending'}),s2=await protocol.createDeviceChannelProposal(keys,smallConfig.actor,smallConfig.channel,'chat',{text:'Second small pending'});await small.enqueue(s1);
 check('per-channel pending capacity refuses extra work and retains the original',await refuses(()=>small.enqueue(s2),'allowance reached')&&(await small.pending()).length===1&&(await archive.load()).position.count===2);
 small.close();
 const forkAt=(await archive.load()).position,wireA=await protocol.createDeviceChannelProposal(keys,config.actor,config.channel,'chat',{text:'Concurrent branch A'}),wireB=await protocol.createDeviceChannelProposal(keys,config.actor,config.channel,'chat',{text:'Concurrent branch B'});
 await archive.enqueue(wireA);await archive.enqueue(wireB);const blockA=await certify(forkAt,[await archive.record(wireA)]),blockB=await certify(forkAt,[await archive.record(wireB)]),competitor=await openArchive();
 // These deliberately conflicting fixture certificates test archive CAS, not
 // a claim that honest replica engines sign conflicting accepted branches.
 const originalInsert=DeviceOperationTree.prototype.insert;let arrivals=0,release;const barrier=new Promise(r=>release=r);
 DeviceOperationTree.prototype.insert=async function(...args){if(++arrivals===2)release();await barrier;return originalInsert.apply(this,args);};let race;
 try{race=await Promise.allSettled([archive.append(blockA),competitor.append(blockB)]);}finally{DeviceOperationTree.prototype.insert=originalInsert;competitor.close();}
 check('two views staging conflicting accepted heads commit only one archive transaction',race.filter(r=>r.status==='fulfilled').length===1&&race.filter(r=>r.status==='rejected'&&r.reason.name==='DeviceArchiveConflict').length===1);
 const leftover=await archive.pending();check('the valid original on the losing branch remains pending with its exact signature',leftover.length===1&&[wireA,wireB].includes(leftover[0].wire));
 const restoredOriginal=leftover[0],reinclude=await certify((await archive.load()).position,[await archive.record(restoredOriginal.wire)]),reincluded=await archive.append(reinclude);
 check('a valid losing-branch original is reauthorized and included exactly once without changing its signature',protocol.deviceChannelState(reincluded.position).messages.at(-1).id===restoredOriginal.id&&reinclude.operations[0].proposal===restoredOriginal.wire&&(await archive.pending()).length===0);
 const cancelWire=await protocol.createDeviceChannelProposal(keys,config.actor,config.channel,'chat',{text:'Explicitly cancelled pending original'});await archive.enqueue(cancelWire);const cancel=(await archive.pending())[0];
 check('pending cancellation requires its exact retained original hash',await refuses(()=>archive.cancelPending(cancel.id,{expectedWireHash:'A'.repeat(43)}),'changed before cancellation'));
 await archive.cancelPending(cancel.id,{expectedWireHash:cancel.wireHash});check('explicit pending cancellation removes only that exact original',(await archive.pending()).length===0);
 const nodeBound=(await archive.stats()).nodes,limited=await openArchive({maxNodes:nodeBound}),capacityWire=await protocol.createDeviceChannelProposal(keys,config.actor,config.channel,'chat',{text:'Retain pending when complete graph cannot fit'});await archive.enqueue(capacityWire);
 const capacityBlock=await certify((await archive.load()).position,[await archive.record(capacityWire)]),capacityStats=await archive.stats(),capacityHead=(await archive.load()).hash;
 check('complete graph capacity refusal is atomic and retains the prior head and pending original',await refuses(()=>limited.append(capacityBlock),'allowance reached')&&(await archive.load()).hash===capacityHead&&JSON.stringify(await archive.stats())===JSON.stringify(capacityStats));limited.close();
 const capacityPending=(await archive.pending())[0];await archive.cancelPending(capacityPending.id,{expectedWireHash:capacityPending.wireHash});
 let at=(await archive.load()).position;
 // Manual certificate fixtures exercise retention only; the first accepted
 // block above is driven by the actual replica engine, not these helpers.
 for(let i=at.count;i<68;i++){
  const original=await protocol.createDeviceChannelProposal(keys,config.actor,config.channel,'chat',{text:'Historical message '+i});const record=await archive.record(original),b=await certify(at,[record]);at=(await archive.append(b)).position;
 }
 check('checkpoint recent window stays bounded while the full archive retains older originals',protocol.deviceChannelState(at).messages.length===64&&!protocol.deviceChannelState(at).messages.some(m=>m.id===retained.id));
 let ancestryCursor=null,proofs=[],pages=0;do{const page=await archive.ancestryPage({before:ancestryCursor,limit:16});pages++;check('ancestry page contains certificates without chat operation bodies '+pages,page.entries.every(e=>Object.keys(e).sort().join(',')==='commit,header,prepare'&&!JSON.stringify(e).includes('Historical message')));proofs.push(...page.entries);ancestryCursor=page.next;}while(ancestryCursor);
 const ancestry=new protocol.DeviceChannelAncestryVerifier(saved.position),suffix=proofs.filter(e=>e.header.height>saved.position.height).reverse();for(let i=0;i<suffix.length;i+=32)await ancestry.append(suffix.slice(i,i+32));const snap=await ancestry.finish(protocol.encodeDeviceChannelCheckpoint(at));check('archive ancestry pages link a retained floor to a newer quorum snapshot',proofs.length===at.height&&pages>1&&snap.head===at.head);ancestry.close();
 check('invalid ancestry page limit is refused',await refuses(()=>archive.ancestryPage({limit:33}),'page limit'));

 let cursor=null,total=0,found=false;do{const page=await archive.history({before:cursor,limit:9});total+=page.entries.length;found||=page.entries.some(e=>e.block.operations[0].proposal===retained.original);cursor=page.next;}while(cursor);
 check('paged complete history includes the exact first signed message beyond the recent checkpoint window',total===68&&found);
 const audited=await raw((tx,done)=>{let bytes=0,nodes=0,pending=0,heads=0,treeNodes=0;const names=['nodes','pending','heads'];let i=0;const next=()=>{if(i===names.length){done({bytes,nodes,pending,heads,treeNodes});return;}const name=names[i++],q=tx.objectStore(name).openCursor();q.onsuccess=()=>{const c=q.result;if(!c){next();return;}bytes+=c.value.bytes;if(name==='nodes'){nodes++;if(JSON.parse(c.value.wire).profile==='codi-operation-tree/1')treeNodes++;}else if(name==='pending')pending++;else heads++;c.continue();};};next();});
 const stats=await archive.stats();check('actual retained graph prunes replaced index branches and accounts every stored byte',audited.treeNodes===2*68-1&&['bytes','nodes','pending','heads'].every(k=>audited[k]===stats[k]));window.archiveMetrics={blocks:total,contentNodes:stats.nodes,bytes:stats.bytes,pending:stats.pending};
 const loaded=await archive.load(),expectedRoot=protocol.deviceChannelState(loaded.position).acceptedRoot,treeReader=new DeviceOperationTree({get:cid=>archive.readNode(cid),put:async()=>{throw Error('fixture is read-only');}}),indexVerifier=new DeviceOperationTreeVerifier({tree:treeReader,root:loaded.tree,expectedRoot});let indexStatus,steps=0;do{indexStatus=await indexVerifier.step({limit:13});steps++;}while(!indexStatus.complete);check('bounded incremental index verification matches the signed checkpoint',steps>1&&indexStatus.checked===audited.treeNodes&&indexStatus.pending===0);indexVerifier.close();
 const wrongRoot=new DeviceOperationTreeVerifier({tree:treeReader,root:loaded.tree,expectedRoot:await hash('wrong-root')});check('wrong checkpoint index root is refused',await refuses(()=>wrongRoot.step(),'root differs'));wrongRoot.close();
 const alteredReader=new DeviceOperationTree({get:async cid=>(await archive.readNode(cid))+' ',put:async()=>{}}),alteredVerifier=new DeviceOperationTreeVerifier({tree:alteredReader,root:loaded.tree,expectedRoot});check('altered operation-index content fails its hash check',await refuses(()=>alteredVerifier.step(),'hash mismatch'));alteredVerifier.close();
 const cancelledIndex=new DeviceOperationTreeVerifier({tree:treeReader,root:loaded.tree,expectedRoot}),abortIndex=new AbortController();abortIndex.abort(Error('index cancelled'));check('cancelled index verification cannot report completion',await refuses(()=>cancelledIndex.step({signal:abortIndex.signal}),'index cancelled')&&!cancelledIndex.snapshot().complete);cancelledIndex.close();


 const offer=await archive.transferHead(),cacheOptions={scope,channel:config.channel,genesisHash:config.genesisHash};let indexCache=await new DeviceChannelDownloadCache(cacheOptions).open(await policy.acquire(),offer);const rootWire=await archive.readNode(loaded.tree.cid);
 await indexCache.putIndex(loaded.tree,rootWire);check('verified index node is retained as unaccepted scratch data',(await indexCache.stats()).nodes===1&&(await indexCache.getIndex(loaded.tree))===rootWire);
 const wrongLink={...loaded.tree,hash:(loaded.tree.hash[0]==='A'?'B':'A')+loaded.tree.hash.slice(1)};check('scratch cache refuses forged index link and modified bytes',await refuses(()=>indexCache.getIndex(wrongLink),'link differs')&&await refuses(()=>indexCache.putIndex(loaded.tree,rootWire+' '),'hash mismatch'));
 indexCache.close();indexCache=await new DeviceChannelDownloadCache(cacheOptions).open(await policy.acquire(),offer);check('fresh cache handle restores verified index node without an accepted-floor change',(await indexCache.getIndex(loaded.tree))===rootWire&&(await archive.load()).position.head===at.head);await indexCache.trim([],{removeJob:true});indexCache.close();
 const latest=(await archive.load()).history,node=await archive.readNode(latest);await raw((tx,done)=>{const q=tx.objectStore('nodes').get([scope,config.channel,latest]);q.onsuccess=()=>{q.result.wire+=' ';tx.objectStore('nodes').put(q.result);done(true);};});
 check('corrupt retained history bytes fail closed instead of creating a new channel',await refuses(()=>archive.load(),'Corrupt device archive'));
 await raw((tx,done)=>{const q=tx.objectStore('nodes').get([scope,config.channel,latest]);q.onsuccess=()=>{q.result.wire=node;tx.objectStore('nodes').put(q.result);done(true);};});
 check('repairing exact retained content restores the same accepted head',(await archive.load()).position.head===at.head);
 const cancelled=new AbortController();cancelled.abort(Error('Owned view ended'));check('cancelled history work cannot return a late accepted result',await refuses(()=>archive.history({signal:cancelled.signal}),'Owned view ended'));
 const oldOpen=IDBFactory.prototype.open,oldSet=window.setTimeout,oldClear=window.clearTimeout;let connections=0;const timers=new Set();
 IDBFactory.prototype.open=function(...args){const q=oldOpen.apply(this,args);q.addEventListener('success',()=>{connections++;const db=q.result,close=db.close.bind(db);let active=true;db.close=()=>{if(active){active=false;connections--;}return close();};});return q;};
 window.setTimeout=function(fn,delay,...args){let token;token=oldSet(()=>{timers.delete(token);fn(...args);},delay);timers.add(token);return token;};window.clearTimeout=function(token){timers.delete(token);return oldClear(token);};
 try{for(let i=0;i<30;i++){const a=await openArchive();await a.load();await a.pending();a.close();}check('thirty archive reopens leave no native database connections or operation timers',connections===0&&timers.size===0);}finally{IDBFactory.prototype.open=oldOpen;window.setTimeout=oldSet;window.clearTimeout=oldClear;}
 archive.close();check('closed archive handles refuse further queue or history work',await refuses(()=>archive.pending(),'closed'));
 return checks;
}
const gate=mountDeviceStorageGate({policy,signal:life.signal,make,feature:'Channel archive fixture',onReady:async()=>window.storageReady=true});document.querySelector('#gate').append(gate.element);
window.archiveFixture={checks,policy,begin,finish,close(){life.abort();gate.dispose();for(const r of owned)r.close();policy.close();}};window.fixtureReady=true;
