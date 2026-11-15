#!/usr/bin/env python3
"""Run adversarial protocol fixtures in real browser Web Crypto."""
import argparse,json,urllib.request,urllib.error
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8097/');options=parser.parse_args()
base='http://127.0.0.1:19515'
def req(path,data=None,method=None):
 r=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 try:
  with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
 except urllib.error.HTTPError as error:raise RuntimeError(error.read().decode()) from error
s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
try:
 req('/session/'+s+'/url',{'url':options.url})
 code='''const done=arguments[0];(async()=>{
 const c=await import('./network/crypto.mjs');const results=[];
 function check(name,fn){try{fn();results.push({name,status:'PASS'});}catch(e){results.push({name,status:'FAIL',error:e.message});}}
 function rejects(fn){let rejected=false;try{fn();}catch{rejected=true;}if(!rejected)throw Error('Invalid input accepted');}
 const token=(header,payload)=>c.b64(c.enc.encode(header))+'.'+c.b64(c.enc.encode(payload))+'.'+c.b64(new Uint8Array(64));
 const header='{"alg":"ES256","typ":"fixture"}';
 check('duplicate header',()=>rejects(()=>c.inspectJws(token('{"alg":"ES256","alg":"ES256","typ":"fixture"}','{}'),'fixture')));
 check('duplicate payload',()=>rejects(()=>c.inspectJws(token(header,'{"seq":1,"seq":2}'),'fixture')));
 check('escaped duplicate nested key',()=>rejects(()=>c.inspectJws(token(header,'{"x":{"a":1,"\\\\u0061":2}}'),'fixture')));
 check('valid signed bytes',()=>{const p=c.inspectJws(token(header,'{"seq":1,"x":[true,null,"hello"]}'),'fixture');if(p.payload.seq!==1)throw Error('Bad parse');});
 check('oversized token',()=>rejects(()=>c.inspectJws(token(header,'{}'),'fixture',10)));
 check('noncanonical base64',()=>rejects(()=>c.unb64('Zh')));
 check('unsupported algorithm',()=>rejects(()=>c.inspectJws(token('{"alg":"none","typ":"fixture"}','{}'),'fixture')));
 check('bounded nesting',()=>rejects(()=>c.inspectJws(token(header,'{"x":'+ '['.repeat(40)+'0'+']'.repeat(40)+'}'),'fixture')));
 const mesh=await import('./network/mesh-contract.mjs');
 const node=mesh.newNodeId(),room=await mesh.roomId(node),moveRoom=await mesh.roomId(node,'chess.moves');
 const renamed={node,label:'Renamed',parent:mesh.newNodeId()};
 check('rename and move preserve room ID',()=>{if(renamed.node!==node||room===moveRoom)throw Error('Namespace/lane identity collision');});
 if(await mesh.roomId(renamed.node)!==room)throw Error('Room ID changed after presentation move');
 check('mesh negotiation',()=>mesh.negotiateMesh(JSON.stringify({type:'hello',version:'codi-mesh/1',mode:'public-jws/1'})));
 for(const [name,version,mode] of [['unknown version','codi-mesh/2','public-jws/1'],['private profile disabled','codi-mesh/1','private'],['legacy frame not upgraded','codi-peer/1','public-jws/1']])check(name,()=>rejects(()=>mesh.negotiateMesh(JSON.stringify({type:'hello',version,mode}))));
 const frame={version:'codi-mesh/1',type:'public-event',request_id:node,destination_cell:node,hops_remaining:16,event:'e30.e30.'+c.b64(new Uint8Array(64))};
 check('bounded frame shape',()=>mesh.parseMeshFrame(JSON.stringify(frame)));
 check('extra frame field',()=>rejects(()=>mesh.parseMeshFrame(JSON.stringify({...frame,admin:true}))));
 check('bad hop length',()=>rejects(()=>mesh.parseMeshFrame(JSON.stringify({...frame,hops_remaining:17}))));
 check('oversize origin event',()=>rejects(()=>mesh.parseMeshFrame(JSON.stringify({...frame,event:'x'.repeat(16385)}))));
 check('duplicate framing field',()=>rejects(()=>mesh.parseMeshFrame(JSON.stringify(frame).replace('"hops_remaining":16','"hops_remaining":1,"hops_remaining":16'))));
 const origin=await import('./network/origin-event.mjs');
 const identity=await import('./network/identity.mjs');
 const turnNow=Math.floor(Date.now()/1000),turnExpiry=turnNow+300,turnConfig={identity:{mode:'server'},rtc:{credentialMode:'session-turn/1',turnUrls:['turns:localhost:18443?transport=tcp']}},turnTrust={claims:{exp:turnNow+900}},turnReply={rtc:{iceTransportPolicy:'relay',expiresAt:turnExpiry,iceServers:[{urls:['turns:localhost:18443?transport=tcp'],username:turnExpiry+':opaque',credential:'AAAAAAAAAAAAAAAAAAAAAAAAAAA=',credentialType:'password'}]}};
 check('explicit modern preference selects all while legacy default remains relay',()=>{const cfg=structuredClone(turnConfig),reply=structuredClone(turnReply);cfg.rtc.iceTransportPolicy='relay';cfg.rtc.preference={version:'codi-session-ice/1',allowed:['relay','all'],preferred:'all'};reply.rtc.iceTransportPolicy='all';if(identity.sessionTurnConfig(cfg,reply,turnTrust).iceTransportPolicy!=='all'||cfg.rtc.iceTransportPolicy!=='relay')throw Error('Preference/default confused');rejects(()=>identity.sessionTurnConfig(cfg,turnReply,turnTrust));});
 for(const [name,preference] of [['null',null],['unknown version',{version:'unknown',allowed:['relay'],preferred:'relay'}],['extra destination',{version:'codi-session-ice/1',allowed:['relay'],preferred:'relay',url:'https://wrong.invalid'}],['duplicate choice',{version:'codi-session-ice/1',allowed:['relay','relay'],preferred:'relay'}],['unknown choice',{version:'codi-session-ice/1',allowed:['relay','auto'],preferred:'auto'}],['unadvertised preferred',{version:'codi-session-ice/1',allowed:['relay'],preferred:'all'}],['wrong type',{version:'codi-session-ice/1',allowed:['relay'],preferred:true}]])check('ICE preference capability rejects '+name,()=>{const cfg=structuredClone(turnConfig);cfg.rtc.iceTransportPolicy='relay';cfg.rtc.preference=preference;rejects(()=>identity.icePreference(cfg));});
 check('session TURN response accepted and copied',()=>{const rtc=identity.sessionTurnConfig(turnConfig,turnReply,turnTrust);if(rtc===turnReply.rtc||rtc.expiresAt!==turnExpiry)throw Error('Bad session TURN copy');});
 check('direct ICE plus TURN fallback requires explicit policy',()=>{const cfg=structuredClone(turnConfig),r=structuredClone(turnReply);cfg.rtc.iceTransportPolicy='all';r.rtc.iceTransportPolicy='all';if(identity.sessionTurnConfig(cfg,r,turnTrust).iceTransportPolicy!=='all')throw Error('Direct ICE policy lost');rejects(()=>identity.sessionTurnConfig(cfg,turnReply,turnTrust));});
 check('unknown ICE policy rejected',()=>rejects(()=>identity.sessionTurnConfig({...turnConfig,rtc:{...turnConfig.rtc,iceTransportPolicy:'unknown'}},turnReply,turnTrust)));
 for(const [name,change] of [
  ['missing',r=>delete r.rtc],['expired',r=>r.rtc.expiresAt=turnNow-1],['too long',r=>r.rtc.expiresAt=turnNow+601],['wrong endpoint',r=>r.rtc.iceServers[0].urls=['turns:wrong.invalid?transport=tcp']],['wrong password',r=>r.rtc.iceServers[0].credential='bad'],['direct fallback',r=>r.rtc.iceTransportPolicy='all']
 ])check('session TURN rejects '+name,()=>{const r=JSON.parse(JSON.stringify(turnReply));change(r);rejects(()=>identity.sessionTurnConfig(turnConfig,r,turnTrust));});
 check('session TURN cannot outlive identity',()=>rejects(()=>identity.sessionTurnConfig(turnConfig,turnReply,{claims:{exp:turnNow+30}})));

 const config={identity:{mode:'local-development'}};
 for(const apiBase of ['https://wrong.invalid/api/v1','//wrong.invalid/api/v1','/hidden/../api/v1','/hidden/api/v1/','/hidden%2fapi/v1'])await testAsync('reject noncanonical API mount '+apiBase,()=>rejectsAsync(()=>identity.authenticatedRequest({mode:'server',apiBase}, {},apiBase+'/anonymous',{})));
 await testAsync('root route cannot bypass configured API mount',()=>rejectsAsync(()=>identity.authenticatedRequest({mode:'server',apiBase:'/hidden/api/v1'}, {},'/api/v1/anonymous',{})));

 const session=await identity.beginSession(config,'anonymous');
 const scope={room_id:room,descriptor_hash:node,membership_epoch:1,kinds:['chat']};
 const t=Math.floor(Date.now()/1000);
 const event={version:'codi-mesh/1',room_id:room,descriptor_hash:node,membership_epoch:1,author_session_id:session.public.sid,stream_incarnation:mesh.newNodeId(),sequence:1,issued_at:t,expires_at:t+60,kind:'chat',payload:{text:'test'}};
 const signed=await origin.signOrigin(event,session,config.identity,scope);
 async function testAsync(name,fn){try{await fn();results.push({name,status:'PASS'});}catch(e){results.push({name,status:'FAIL',error:e.message});}}
 async function rejectsAsync(fn){let rejected=false;try{await fn();}catch{rejected=true;}if(!rejected)throw Error('Invalid signed input accepted');}
 await testAsync('origin signature and scope',()=>origin.verifyOrigin(signed,session.public,config.identity,scope));
 await testAsync('signature-independent origin ID',async()=>{
   const second=await origin.signOrigin(event,session,config.identity,scope);
   if(await origin.originEventId(signed)!==await origin.originEventId(second))throw Error('Signature changed event ID');
 });
 await testAsync('wrong authorized room',()=>rejectsAsync(()=>origin.verifyOrigin(signed,session.public,config.identity,{...scope,room_id:node})));
 await testAsync('extra signed field',async()=>{const token=await c.signJws({...event,admin:true},session.privateKey,origin.ORIGIN_TYPE);await rejectsAsync(()=>origin.verifyOrigin(token,session.public,config.identity,scope));});
 await testAsync('expired signed event',async()=>{const token=await c.signJws({...event,issued_at:t-61,expires_at:t-1},session.privateKey,origin.ORIGIN_TYPE);await rejectsAsync(()=>origin.verifyOrigin(token,session.public,config.identity,scope));});
 await testAsync('wrong author key',async()=>{const other=await identity.beginSession(config,'anonymous');await rejectsAsync(()=>origin.verifyOrigin(signed,other.public,config.identity,scope));});
 await testAsync('chat cannot enter move lane',()=>rejectsAsync(()=>origin.verifyOrigin(signed,session.public,config.identity,{...scope,kinds:['chess.move']})));
 check('unsafe sequence',()=>rejects(()=>mesh.validateOrigin({...event,sequence:9007199254740992},scope)));
 const {ResourceBudget,sessionBudget,NETWORK_LIMITS}=await import('./network/resource-budget.mjs');
 check('one budget per session object',()=>{if(sessionBudget(session)!==sessionBudget(session))throw Error('Duplicate session budgets');});
 check('connection reservations include pending',()=>{
   const b=new ResourceBudget(),leases=[];for(let i=0;i<20;i++)leases.push(b.connection());
   rejects(()=>b.connection());leases.push(b.connection('support'),b.connection('support'),b.connection('replacement'),b.connection('replacement'));
   rejects(()=>b.connection('replacement'));if(b.snapshot().connections!==24)throw Error('Wrong total');
   leases.forEach(f=>{f();f();});if(b.snapshot().connections!==0)throw Error('Release is not idempotent');
 });
 check('global crypto work cap',()=>{const b=new ResourceBudget(),leases=Array.from({length:32},()=>b.crypto());rejects(()=>b.crypto());leases.forEach(f=>f());if(b.snapshot().crypto)throw Error('Crypto reservation leaked');});
 check('application queue preserves control reserve',()=>{const b=new ResourceBudget(),release=b.wire(NETWORK_LIMITS.queuedBytes-NETWORK_LIMITS.controlBytes);rejects(()=>b.wire(1));const control=b.wire(NETWORK_LIMITS.controlBytes,true);rejects(()=>b.wire(1,true));release();control();if(b.snapshot().queuedBytes)throw Error('Wire leaked');});
 check('metadata budget cannot be bypassed',()=>{const b=new ResourceBudget(),release=b.metadata(NETWORK_LIMITS.metadataBytes);rejects(()=>b.metadata(1));release();rejects(()=>b.metadata(-1));});
 check('bounded subscriptions and hints',()=>{for(const [kind,max] of [['subscriptions',4],['hints',256],['replayStreams',65536]]){const b=new ResourceBudget(),leases=Array.from({length:max},()=>b.slot(kind));rejects(()=>b.slot(kind));leases.forEach(f=>f());}});
 check('closing blocks new work without erasing active charges',()=>{const b=new ResourceBudget(),release=b.crypto();b.close();rejects(()=>b.crypto());if(b.snapshot().crypto!==1)throw Error('Active work hidden');release();});
 await testAsync('rejected crypto job releases reservation',async()=>{const b=new ResourceBudget();await rejectsAsync(()=>b.runCrypto(async()=>{throw Error('fixture')}));if(b.snapshot().crypto)throw Error('Leaked failure');});
 const {PeerLink}=await import('./network/peer.mjs');
 check('missing or expired session TURN cannot open RTC',()=>{for(const rtc of [undefined,{iceTransportPolicy:'relay',iceServers:[],expiresAt:0}]){const link=new PeerLink({rtc},{rtc:{credentialMode:'session-turn/1'}});try{rejects(()=>link.create());if(link.pc)throw Error('RTC opened before fresh credential');}finally{link.close();}}});

 await testAsync('relay-only without TURN exposes no direct candidates',async()=>{const link=new PeerLink({}, {...config,rtc:{iceServers:[],iceTransportPolicy:'relay'}});try{link.create();link.pc.createDataChannel('fixture');await link.pc.setLocalDescription(await link.pc.createOffer());await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('ICE fixture timeout')),3000);const done=()=>{if(link.pc.iceGatheringState==='complete'){clearTimeout(timer);resolve();}};link.pc.addEventListener('icegatheringstatechange',done);done();});if(/a=candidate:/.test(link.pc.localDescription.sdp))throw Error('Direct candidate leaked');}finally{link.close();}});
 check('configured relay policy reaches native RTC',()=>{const owner={},link=new PeerLink(owner,{...config,rtc:{iceServers:[],iceTransportPolicy:'relay'}});try{link.create();if(link.pc.getConfiguration().iceTransportPolicy!=='relay')throw Error('Relay-only policy ignored');}finally{link.close();}});
 check('unknown ICE policy fails closed',()=>{const owner={},link=new PeerLink(owner,{...config,rtc:{iceServers:[],iceTransportPolicy:'relayy'}});try{rejects(()=>link.create());if(link.pc)throw Error('Invalid policy opened RTC');}finally{link.close();}});

 check('room renewal requires explicit application opt-in',()=>{
   const owner={},generic=new PeerLink(owner,config,{onApplication:()=>{}}),enabled=new PeerLink(owner,config,{onApplication:()=>{},roomRenewal:true});
   try{if(generic.applications.includes('codi-room-renew/1')||!enabled.applications.includes('codi-room-renew/1'))throw Error('Incorrect capability advertisement');rejects(()=>new PeerLink(owner,config,{roomRenewal:true}));}finally{generic.close();enabled.close();}
   if(sessionBudget(owner).snapshot().metadataBytes||sessionBudget(owner).snapshot().connections)throw Error('Opt-in fixture leaked');
 });
 check('peer constructors share pending connection cap',()=>{const isolated={},links=[];try{for(let i=0;i<15;i++)links.push(new PeerLink(isolated,config));rejects(()=>new PeerLink(isolated,config));}finally{links.forEach(link=>link.close());}if(sessionBudget(isolated).snapshot().connections||sessionBudget(isolated).snapshot().metadataBytes)throw Error('Peer reservation leaked');});
 await testAsync('closed peer retains in-flight metadata charge',async()=>{
   const owner={},link=new PeerLink(owner,config);let finish;
   const pending=link.trackOperation(()=>new Promise(resolve=>finish=resolve));link.close();
   if(sessionBudget(owner).snapshot().metadataBytes===0)throw Error('In-flight metadata unaccounted');
   finish();await pending;
   if(sessionBudget(owner).snapshot().metadataBytes!==0)throw Error('In-flight metadata leaked');
 });
 const ns=await import('./network/namespace.mjs');
 const controller=await c.makeKey(),childKey=await c.makeKey(),siblingKey=await c.makeKey();
 const rootId=mesh.newNodeId(),childId=mesh.newNodeId(),siblingId=mesh.newNodeId();
 const owner={};const directory=new ns.PublicDirectory(owner,{rootId,rootKey:controller.publicKey,expiresAt:t+3600});
 const descriptor=(node,parent,label,key)=>({version:1,node_id:node,parent_id:parent,revision:1,previous_hash:null,label,controller_key:key.publicKey,policy_hash:mesh.newNodeId(),routing_revision:1,deleted:false,issued_at:t,expires_at:t+3600});
 const signNode=(p,key)=>c.signJws(p,key.privateKey,ns.NODE_TYPE);
 const grant=async(parent,child,token,action,key)=>c.signJws({version:1,parent_id:parent,parent_revision:directory.get(parent).descriptor.revision,child_id:child,descriptor_hash:await ns.namespaceContentId(token,ns.NODE_TYPE),action,issued_at:t,expires_at:t+60},key.privateKey,ns.NODE_GRANT_TYPE);
 let root=descriptor(rootId,null,'Local test realm',controller);await directory.ingest(await signNode(root,controller));
 let child=descriptor(childId,rootId,'Child',childKey),childToken=await signNode(child,childKey);
 await testAsync('node create needs parent authorization',()=>rejectsAsync(()=>directory.ingest(childToken)));
 await testAsync('parent grant creates independently identified room',async()=>{await directory.ingest(childToken,{create:await grant(rootId,childId,childToken,'create',controller)});if(await directory.room(childId)===await directory.room(rootId))throw Error('Parent room collision');});
 const childRoom=await directory.room(childId);
 child={...child,revision:2,previous_hash:directory.get(childId).hash,label:'Renamed'};await directory.ingest(await signNode(child,childKey));
 await testAsync('signed rename retains room identity',async()=>{if(await directory.room(childId)!==childRoom)throw Error('Rename changed room');});
 const sibling=descriptor(siblingId,rootId,'Sibling',siblingKey),siblingToken=await signNode(sibling,siblingKey);
 await directory.ingest(siblingToken,{create:await grant(rootId,siblingId,siblingToken,'create',controller)});
 const moved={...child,revision:3,previous_hash:directory.get(childId).hash,parent_id:siblingId};const movedToken=await signNode(moved,childKey);
 await testAsync('unauthorized parent move rejected',()=>rejectsAsync(()=>directory.ingest(movedToken)));
 await testAsync('two-parent grants authorize move without changing room',async()=>{await directory.ingest(movedToken,{out:await grant(rootId,childId,movedToken,'move-out',controller),into:await grant(siblingId,childId,movedToken,'move-in',siblingKey)});if(await directory.room(childId)!==childRoom)throw Error('Move changed room');});
 await testAsync('stale namespace update rejected',async()=>{const stale=await signNode(child,childKey);await rejectsAsync(()=>directory.ingest(stale));});
 await testAsync('oversized parent grant rejected before crypto',()=>rejectsAsync(()=>directory.ingest(movedToken,{into:'x'.repeat(8193)})));
 await testAsync('unknown ancestor refused',()=>rejectsAsync(()=>directory.room(mesh.newNodeId())));
 await testAsync('authorized edges still reject ancestor cycle',async()=>{
   const cyclic={...sibling,parent_id:childId,revision:2,previous_hash:directory.get(siblingId).hash};const token=await signNode(cyclic,siblingKey);
   const grants={out:await grant(rootId,siblingId,token,'move-out',controller),into:await grant(childId,siblingId,token,'move-in',childKey)};await rejectsAsync(()=>directory.ingest(token,grants));
 });
 await testAsync('bounded empty namespace page',()=>directory.page(JSON.stringify({version:1,parent_id:rootId,next:null,entries:[]}),rootId));
 await testAsync('oversized namespace page refused',()=>rejectsAsync(()=>directory.page(' '.repeat(32769),rootId)));
 await testAsync('namespace page count refused',()=>rejectsAsync(()=>directory.page(JSON.stringify({version:1,parent_id:rootId,next:null,entries:Array.from({length:129},()=>({}))}),rootId)));
 await testAsync('deep namespace path refuses beyond cap',async()=>{
   let parent=rootId,count=0;
   for(let n=0;n<33;n++){
     const next=mesh.newNodeId(),p=descriptor(next,parent,'depth',controller),token=await signNode(p,controller),authorization=await grant(parent,next,token,'create',controller);
     try{await directory.ingest(token,{create:authorization});parent=next;count++;}catch(e){if(!e.message.includes('depth limit'))throw e;break;}
   }
   if(count!==31)throw Error('Unexpected depth count '+count);
 });
 await testAsync('signed fork freezes node access',async()=>{const fork=await signNode({...moved,label:'Conflicting same revision'},childKey);await rejectsAsync(()=>directory.ingest(fork));if(!directory.get(childId).forked)throw Error('Fork not exposed');await rejectsAsync(()=>directory.room(childId));});
 directory.close();await new Promise(resolve=>setTimeout(resolve,0));
 check('directory disposal releases metadata',()=>{if(sessionBudget(owner).snapshot().metadataBytes!==0)throw Error('Directory metadata leaked');});
 const {RoomSubscriptions}=await import('./network/subscriptions.mjs');
 check('subscription replacement uses variable allowance above32MiB',()=>{
   const owner={},b=sessionBudget(owner);b.setMetadataLimit(128*1048576);const r=new RoomSubscriptions(owner),a=mesh.newNodeId(),c=mesh.newNodeId();
   r.register({room_id:a,label:'old',kinds:['chat']});r.register({room_id:c,label:'new',kinds:['chat']});let handles=[r.acquire(a)];const hold=b.metadata(40*1048576);
   try{handles=r.replace(handles,[c]);if(r.snapshot(a).views||r.snapshot(c).views!==1||b.snapshot().subscriptions!==1)throw Error('Replacement did not preserve one hot room');}
   finally{handles.forEach(h=>h.release());hold();r.close();}if(b.snapshot().metadataBytes||b.snapshot().subscriptions)throw Error('Variable replacement leaked');
 });
 check('variable allowance exhaustion refuses replacement atomically',()=>{
   const owner={},b=sessionBudget(owner);b.setMetadataLimit(64*1048576);const r=new RoomSubscriptions(owner),a=mesh.newNodeId(),c=mesh.newNodeId();
   r.register({room_id:a,label:'old',kinds:['chat']});r.register({room_id:c,label:'new',kinds:['chat']});const handle=r.acquire(a);r.deliver(a,{kind:'chat',author:'peer',sequence:1,text:'keep'});
   const hold=b.metadata(b.limits().metadataBytes-b.snapshot().metadataBytes-200000);
   try{rejects(()=>r.replace([handle],[c]));if(r.snapshot(a).views!==1||r.snapshot(a).history[0]?.text!=='keep'||r.snapshot(c).views||b.snapshot().subscriptions!==1)throw Error('Failed replacement changed existing state');}
   finally{hold();handle.release();r.close();}if(b.snapshot().metadataBytes||b.snapshot().subscriptions)throw Error('Refusal leaked');
 });
 const subscriptionOwner={},subscriptions=new RoomSubscriptions(subscriptionOwner);
 const ids=Array.from({length:5},()=>mesh.newNodeId());
 for(let i=0;i<ids.length;i++)subscriptions.register({room_id:ids[i],label:'fixture '+i,kinds:[i===3?'chess.move':'chat']});
 check('bookmarks do not subscribe or create connections',()=>{for(let i=0;i<2000;i++)subscriptions.register({room_id:mesh.newNodeId(),label:'saved',kinds:['chat']});if(subscriptions.stats().active!==0||sessionBudget(subscriptionOwner).snapshot().connections!==0)throw Error('Bookmark started network');});
 const first=subscriptions.acquire(ids[0]),second=subscriptions.acquire(ids[0]),childView=subscriptions.acquire(ids[1]),siblingView=subscriptions.acquire(ids[2]);
 check('two room views share one subscription',()=>{if(subscriptions.stats().active!==3||subscriptions.snapshot(ids[0]).views!==2)throw Error('Duplicate subscriptions');});
 check('room histories do not bleed to parent or sibling',()=>{subscriptions.deliver(ids[1],{kind:'chat',author:'peer',sequence:1,text:'child only'});if(subscriptions.snapshot(ids[0]).history.length||subscriptions.snapshot(ids[2]).history.length||subscriptions.snapshot(ids[1]).history.length!==1)throw Error('Cross-room delivery');});
 const moveView=subscriptions.acquire(ids[3]);
 check('chat cannot become a move history event',()=>rejects(()=>subscriptions.deliver(ids[3],{kind:'chat',author:'peer',sequence:2,text:'e4'})));
 check('move history is a separate lane',()=>{subscriptions.deliver(ids[3],{kind:'chess.move',author:'peer',sequence:1,match_id:node,ply:1,notation:'e4'});if(subscriptions.snapshot(ids[3]).history[0].kind!=='chess.move'||subscriptions.snapshot(ids[1]).history.length!==1)throw Error('Lane collision');});
 check('fifth room join fails atomically',()=>{rejects(()=>subscriptions.acquire(ids[4]));if(subscriptions.stats().active!==4||subscriptions.snapshot(ids[4]).views!==0)throw Error('Partial join');});
 check('closing first view keeps shared subscription',()=>{first.release();first.release();if(subscriptions.snapshot(ids[0]).views!==1||subscriptions.stats().active!==4)throw Error('Early unsubscribe');});
 check('last view releases subscription once',()=>{second.release();second.release();if(subscriptions.stats().active!==3||sessionBudget(subscriptionOwner).snapshot().subscriptions!==3)throw Error('Last view leaked');});
 check('invalid inactive delivery cannot mark history incomplete',()=>{rejects(()=>subscriptions.deliver(ids[0],{kind:'chat',author:'peer',sequence:3,text:''}));if(subscriptions.snapshot(ids[0]).missed)throw Error('Invalid record changed missed state');});
 check('unsubscribed room drops live events with bounded incomplete marker',()=>{const before=sessionBudget(subscriptionOwner).snapshot().metadataBytes;if(subscriptions.deliver(ids[0],{kind:'chat',author:'peer',sequence:3,text:'not subscribed'}))throw Error('Unsubscribed delivery');if(!subscriptions.snapshot(ids[0]).missed||subscriptions.snapshot(ids[0]).history.length||sessionBudget(subscriptionOwner).snapshot().metadataBytes!==before)throw Error('Discarded history not marked or allocated');});
 check('reopening a room retains its missed-history warning',()=>{const view=subscriptions.acquire(ids[0]);if(!subscriptions.snapshot(ids[0]).missed)throw Error('Reopen hid discarded messages');view.release();});
 childView.release();siblingView.release();moveView.release();subscriptions.close();
 check('subscription disposal releases all charges',()=>{const s=sessionBudget(subscriptionOwner).snapshot();if(s.metadataBytes||s.subscriptions)throw Error('Subscription metadata leaked');});
 check('failed history allocation does not evict existing history',()=>{
   const owner={},r=new RoomSubscriptions(owner),ids=[];
   for(let i=0;i<17;i++){const id=mesh.newNodeId();ids.push(id);r.register({room_id:id,label:'history',kinds:['chat']});if(i<16){const view=r.acquire(id);r.deliver(id,{kind:'chat',author:'peer',sequence:1,text:'retained '+i});view.release();}}
   const budget=sessionBudget(owner),hold=budget.metadata(NETWORK_LIMITS.metadataBytes-budget.snapshot().metadataBytes);
   rejects(()=>r.acquire(ids[16]));if(r.snapshot(ids[0]).history.length!==1||budget.snapshot().subscriptions!==0)throw Error('Failed join altered existing state');hold();
   const last=r.acquire(ids[16]);if(r.snapshot(ids[0]).history.length!==0||!r.snapshot(ids[0]).evicted)throw Error('Cold history not bounded');last.release();r.close();if(budget.snapshot().metadataBytes)throw Error('Cold histories leaked');
 });
 const {OriginReplayGate}=await import('./network/replay.mjs');
 const replayOwner={},gate=new OriginReplayGate(replayOwner,config.identity);
 const admission={scope,identity:session.public,incarnation:event.stream_incarnation,expiresAt:t+120};
 gate.admit(admission);
 const originFor=async(sequence,changes={})=>origin.signOrigin({...event,sequence,...changes},session,config.identity,scope);
 await testAsync('origin replay window tolerates bounded reordering',async()=>{await gate.receive(await originFor(1));const gap=await gate.receive(await originFor(3));if(gap.gap?.from!==2||gap.gap?.to!==2)throw Error('Missing repair range');await gate.receive(await originFor(2));});
 await testAsync('duplicate signed origin rejected across paths',async()=>{await rejectsAsync(()=>gate.receive(signed));});
 await testAsync('repeated admission cannot reset replay floor',async()=>{gate.admit(admission);await rejectsAsync(()=>gate.receive(signed));});
 await testAsync('invalid signature cannot advance replay state',async()=>{const good=await originFor(4),parts=good.split('.'),sig=c.unb64(parts[2]);sig[0]^=1;parts[2]=c.b64(sig);await rejectsAsync(()=>gate.receive(parts.join('.')));await gate.receive(good);});
 await testAsync('unknown incarnation does not allocate replay state',async()=>{const before=gate.snapshot().streams;const token=await originFor(1,{stream_incarnation:mesh.newNodeId()});await rejectsAsync(()=>gate.receive(token));if(gate.snapshot().streams!==before)throw Error('Unknown stream allocated');});
 await testAsync('large sequence jump keeps constant-size replay window',async()=>{await gate.receive(await originFor(9007199254740991));const old=await originFor(5);await rejectsAsync(()=>gate.receive(old));});
 gate.closeRoom(scope.room_id);
 await testAsync('closed admission cannot be reused',async()=>{rejects(()=>gate.admit(admission));await rejectsAsync(()=>gate.receive(signed));});
 gate.close();
 check('replay disposal releases stream and metadata leases',()=>{const b=sessionBudget(replayOwner).snapshot();if(b.replayStreams||b.metadataBytes||b.crypto||b.queuedBytes)throw Error('Replay resources leaked');});
 await testAsync('concurrent origin duplicates commit once',async()=>{
   const gate=new OriginReplayGate({},config.identity);gate.admit(admission);
   const attempts=await Promise.allSettled([gate.receive(signed),gate.receive(signed)]);
   if(attempts.filter(r=>r.status==='fulfilled').length!==1)throw Error('Concurrent duplicate accepted');gate.close();
 });
 await testAsync('origin cannot outlive admitted stream lease',async()=>{
   const owner={},gate=new OriginReplayGate(owner,config.identity);gate.admit({...admission,expiresAt:t+10});
   await rejectsAsync(()=>gate.receive(signed));
   const shorter=await originFor(1,{expires_at:t+9});await gate.receive(shorter);gate.close();
 });
 await testAsync('expired admission rejects without resetting state',async()=>{
   let clock=t;const gate=new OriginReplayGate({},config.identity,{clock:()=>clock});gate.admit({...admission,expiresAt:t+10});clock=t+11;await rejectsAsync(()=>gate.receive(signed));if(gate.snapshot().streams!==1)throw Error('Expired floor evicted');gate.close();
 });
 check('replay capacity rejects new streams without evicting floors',()=>{
   const owner={},gate=new OriginReplayGate(owner,config.identity);
   for(let i=0;i<1024;i++)gate.admit({...admission,incarnation:mesh.newNodeId()});
   rejects(()=>gate.admit({...admission,incarnation:mesh.newNodeId()}));
   if(gate.snapshot().streams!==1024||sessionBudget(owner).snapshot().replayStreams!==1024)throw Error('Replay cap or floor retention failed');gate.close();if(sessionBudget(owner).snapshot().metadataBytes)throw Error('Replay capacity leaked');
 });
 const invitation=await import('./network/room-invitation.mjs');
 const peerSession=await identity.beginSession(config,'anonymous');
 const invitationLink=mesh.newNodeId();
 const roomBundle=await invitation.createRoomInvitation(session,peerSession.public,config.identity,'Peer-owned room',invitationLink);
 let acceptedRoom;
 await testAsync('authenticated peer room invitation verifies separate lane admissions',async()=>{
   acceptedRoom=await invitation.acceptRoomInvitation(roomBundle,session.public,peerSession,config.identity,invitationLink);
   if(acceptedRoom.lanes.length!==4||new Set(acceptedRoom.lanes.map(l=>l.scope.room_id)).size!==2)throw Error('Room lanes/admissions missing');
   const chatId=await acceptedRoom.directory.room(acceptedRoom.nodeId),moveId=await acceptedRoom.directory.room(acceptedRoom.nodeId,'chess.moves');if(chatId===moveId)throw Error('Move/chat lanes collided');
 });
 await testAsync('invitation cannot impersonate another authenticated sender',async()=>{const other=await identity.beginSession(config,'anonymous');await rejectsAsync(()=>invitation.verifyRoomInvitation(roomBundle,other.public,peerSession,config.identity,invitationLink));});
 await testAsync('invitation cannot substitute a participant key',async()=>{const changed=JSON.parse(JSON.stringify(roomBundle));changed.participants[1].key=session.public.key;await rejectsAsync(()=>invitation.verifyRoomInvitation(changed,session.public,peerSession,config.identity,invitationLink));});
 await testAsync('invitation duplicate lane grants rejected',async()=>{const changed=JSON.parse(JSON.stringify(roomBundle));changed.admissions[1]=changed.admissions[0];await rejectsAsync(()=>invitation.verifyRoomInvitation(changed,session.public,peerSession,config.identity,invitationLink));});
 await testAsync('accepted peer room admission feeds origin replay gate',async()=>{
   const owner={},gate=new OriginReplayGate(owner,config.identity),admission=acceptedRoom.lanes.find(l=>l.identity.sid===session.public.sid&&l.scope.kinds[0]==='chat');gate.admit(admission);
   const now=Math.floor(Date.now()/1000),p={version:'codi-mesh/1',room_id:admission.scope.room_id,descriptor_hash:admission.scope.descriptor_hash,membership_epoch:1,author_session_id:session.public.sid,stream_incarnation:admission.incarnation,sequence:1,issued_at:now,expires_at:Math.min(now+60,admission.expiresAt),kind:'chat',payload:{text:'admitted room event'}};
   const token=await origin.signOrigin(p,session,config.identity,admission.scope);await gate.receive(token);await rejectsAsync(()=>gate.receive(token));gate.close();
 });
 await testAsync('room invitation cannot be rebound to another link',async()=>{const changed=JSON.parse(JSON.stringify(roomBundle)),newLink=mesh.newNodeId();changed.connection_id=newLink;await rejectsAsync(()=>invitation.verifyRoomInvitation(changed,session.public,peerSession,config.identity,newLink));});
 acceptedRoom?.directory.close();
 check('atomic room view replacement fits final global capacity',()=>{
   const owner={},rooms=new RoomSubscriptions(owner),ids=Array.from({length:7},()=>mesh.newNodeId());ids.forEach(id=>rooms.register({room_id:id,label:'swap',kinds:['chat']}));
   const views=ids.slice(0,4).map(id=>rooms.acquire(id)),replaced=rooms.replace(views.slice(0,2),ids.slice(4,6));
   if(rooms.stats().active!==4||rooms.snapshot(ids[0]).views!==0||rooms.snapshot(ids[4]).views!==1)throw Error('Room replacement failed');
   rejects(()=>rooms.replace(replaced,ids.slice(4,7)));if(rooms.stats().active!==4||rooms.snapshot(ids[4]).views!==1)throw Error('Failed replacement altered views');
   rooms.close();if(sessionBudget(owner).snapshot().subscriptions)throw Error('Replacement leaked slots');
 });
 const {ChessRecord,importPgnMainLine}=await import('./network/chess-record.mjs');
 check('illegal chess preview leaves position unchanged',()=>{const game=new ChessRecord(),before=game.status().fen;rejects(()=>game.preview('e5'));rejects(()=>game.preview('--'));if(game.status().fen!==before)throw Error('Illegal move changed position');if(game.preview('e4+')!=='e4'||game.status().fen!==before)throw Error('Preview did not normalize/restore');});
 check('castling and en passant validated',()=>{const castle=new ChessRecord();for(const move of ['e4','e5','Nf3','Nc6','Bc4','Nf6','O-O'])castle.commit(move);const ep=new ChessRecord();for(const move of ['e4','a6','e5','d5','exd6'])ep.commit(move);if(!castle.status().fen.includes('RK1')||ep.moves().at(-1)!=='exd6')throw Error('Special move failed');});
 check('pinned piece cannot expose own king',()=>{const game=new ChessRecord('k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1');rejects(()=>game.preview('Ra2'));});
 check('promotion and checkmate validated',()=>{const promotion=new ChessRecord('7k/2P5/8/8/8/8/8/K7 w - - 0 1');promotion.commit('c8=Q+');const mate=new ChessRecord();for(const move of ['f3','e5','g4','Qh4#'])mate.commit(move);if(mate.status().result!=='0-1'||!mate.status().terminal)throw Error('Mate not detected');rejects(()=>mate.preview('e4'));});
 check('fivefold automatic draw is distinct from claimable threefold',()=>{const game=new ChessRecord();for(let i=0;i<2;i++)for(const move of ['Nf3','Nf6','Ng1','Ng8'])game.commit(move);if(game.status().terminal)throw Error('Unclaimed threefold ended game');for(let i=0;i<2;i++)for(const move of ['Nf3','Nf6','Ng1','Ng8'])game.commit(move);if(game.status().result!=='1/2-1/2')throw Error('Fivefold draw missing');});
 check('PGN legal main line roundtrips independently of chat',()=>{const game=new ChessRecord();for(const move of ['e4','e5','Nf3'])game.commit(move);const pgn=game.pgn({White:'Alice',Black:'Bob'}),record=importPgnMainLine(pgn);if(record.fen!==game.status().fen||record.moves.join(' ')!=='e4 e5 Nf3'||!record.historical)throw Error('PGN roundtrip failed');});
 check('invalid and null-move PGN refused',()=>{rejects(()=>importPgnMainLine('1. e4 e5 2. e5 *'));rejects(()=>importPgnMainLine('1. -- *'));rejects(()=>importPgnMainLine(' '.repeat(65537)));});
 check('PGN tag quotes remain data',()=>{const game=new ChessRecord();game.commit('e4');const record=importPgnMainLine(game.pgn({White:'A"lice',Black:'<b>Bob</b>'}));if(record.headers.White!=='A"lice'||record.headers.Black!=='<b>Bob</b>')throw Error('PGN escaped tag mismatch');});
 check('PGN duplicate tags and incoherent setup/results refused',()=>{
   rejects(()=>importPgnMainLine(`[White "Alice"]
[White "Other"]

1. e4 *`));
   rejects(()=>importPgnMainLine(`[SetUp "1"]

*`));
   rejects(()=>importPgnMainLine(`[Result "1-0"]

1. e4 *`));
 });
 const {HistoricalPgnImports}=await import('./network/pgn-importer.mjs');
 await testAsync('historical PGN worker is single and state is read only',async()=>{
   const owner={},view={},imports=new HistoricalPgnImports(owner),bytes=new TextEncoder().encode('1. d4 d5 *');
   const first=imports.load(view,bytes);await rejectsAsync(()=>imports.load({},bytes));const record=await first;
   if(!Object.isFrozen(record)||!Object.isFrozen(record.moves)||record.moves.join(' ')!=='d4 d5')throw Error('Imported state not historical/read only');
   imports.close();if(sessionBudget(owner).snapshot().metadataBytes)throw Error('PGN worker/record leaked');
 });
 await testAsync('closing a PGN view cancels pending parse and reservations',async()=>{
   const owner={},view={},imports=new HistoricalPgnImports(owner),job=imports.load(view,new TextEncoder().encode('1. e4 e5 *'));imports.releaseView(view);await rejectsAsync(()=>job);imports.close();if(sessionBudget(owner).snapshot().metadataBytes)throw Error('Canceled PGN job leaked');
 });
 const {PeerPool}=await import('./network/peer-pool.mjs');
 await testAsync('pool reservations precede pending RTC construction',async()=>{
   const owner={},budget=sessionBudget(owner),hold=budget.metadata(NETWORK_LIMITS.metadataBytes-2097152-262144),pool=new PeerPool(owner,{identity:config.identity,rtc:{iceServers:[]}});
   const first=pool.offer(),second=pool.offer();pool.close();const settled=await Promise.allSettled([first,second]);hold();
   if(settled[1].status!=='rejected')throw Error('Over-budget pending peer allowed');const s=budget.snapshot();if(s.connections||s.metadataBytes||s.crypto)throw Error('Failed pending construction leaked');
 });
 await testAsync('pool close aborts pending ICE and clears reservations',async()=>{
   const owner=await identity.beginSession(config,'anonymous'),pool=new PeerPool(owner,{identity:config.identity,rtc:{iceServers:[]}}),start=Date.now();
   const pending=pool.offer();await new Promise(resolve=>setTimeout(resolve,0));pool.close();await Promise.allSettled([pending]);
   if(Date.now()-start>2000)throw Error('ICE cancellation waited for full timeout');const s=sessionBudget(owner).snapshot();if(s.connections||s.metadataBytes||s.crypto||s.queuedBytes)throw Error('Cancelled ICE leaked');
 });
 const {PublicRooms}=await import('./network/public-rooms.mjs');
 await testAsync('room control and sends stay bound to their accepted peer',async()=>{
   const owner=await identity.beginSession(config,'anonymous'),b=await identity.beginSession(config,'anonymous'),c=await identity.beginSession(config,'anonymous');
   const fake=participant=>({applicationReady:true,status:'ready',connectionId:mesh.newNodeId(),remote:{payload:{sender:participant.public}},remoteIdentity:participant.public,sent:[],async sendApplication(type,body){this.sent.push({type,body});}});
   const lb=fake(b),lc=fake(c),subscriptions=new RoomSubscriptions(owner),service=new PublicRooms(owner,config,subscriptions,()=>{}),view={};
   service.setLink(lb);const id=await service.create('bound room',view,lb),bundle=lb.sent[0].body.invitation,digest=await ns.namespaceContentId(bundle.node_token,ns.NODE_TYPE);
   const accept={type:'control',body:{operation:'accept',node_id:id,descriptor_hash:digest}};await service.receive(accept,lb);service.setLink(lc);await service.receive(accept,lc);
   if(service.snapshot(view).selected.state!=='active'||!service.snapshot(view).error.includes('scope'))throw Error('Another peer changed room admission');
   await service.send(view,'chat','bound to B');if(lc.sent.length||lb.sent.at(-1).type!=='event')throw Error('Room send followed new peer selection');
   service.removeLink(lc);if(service.snapshot(view).selected.state!=='active')throw Error('Other link removal retired room');service.close();subscriptions.close();await new Promise(resolve=>setTimeout(resolve,0));
   const budget=sessionBudget(owner).snapshot();if(budget.metadataBytes||budget.replayStreams||budget.subscriptions)throw Error('Bound room leaked');
 });
 await testAsync('room delivers verified reordered chat once and warns without changing chess safety',async()=>{
   const owner=await identity.beginSession(config,'anonymous'),other=await identity.beginSession(config,'anonymous');
   const link={applicationReady:true,status:'ready',connectionId:mesh.newNodeId(),remoteIdentity:other.public,sent:[],async sendApplication(type,body){this.sent.push({type,body});}};
   const subscriptions=new RoomSubscriptions(owner),service=new PublicRooms(owner,config,subscriptions,()=>{}),view={};
   try{
     service.setLink(link);const node=await service.create('reorder room',view,link),bundle=link.sent[0].body.invitation;
     const verified=await invitation.verifyRoomInvitation(bundle,owner.public,other,config.identity,link.connectionId);
     await service.receive({type:'control',body:{operation:'accept',node_id:node,descriptor_hash:verified.descriptorHash}},link);
     const lane=kind=>verified.lanes.find(a=>a.identity.sid===other.public.sid&&a.scope.kinds[0]===kind);
     const make=async(kind,sequence,payload)=>{const a=lane(kind),now=Math.floor(Date.now()/1000);return origin.signOrigin({version:'codi-mesh/1',room_id:a.scope.room_id,descriptor_hash:a.scope.descriptor_hash,membership_epoch:1,author_session_id:other.public.sid,stream_incarnation:a.incarnation,sequence,issued_at:now,expires_at:Math.min(now+60,a.expiresAt),kind,payload},other,config.identity,a.scope);};
     const forged=await c.signJws(c.inspectJws(await make('chat',8,{text:'forged'}),origin.ORIGIN_TYPE).payload,owner.privateKey,origin.ORIGIN_TYPE);
     await service.receive({type:'event',body:{origin:forged}},link);
     if(service.snapshot(view).selected.chatWarning||service.snapshot(view).selected.chat.length)throw Error('Invalid signature poisoned gap state');
     const third=await make('chat',3,{text:'third'});
     for(const token of [third,await make('chat',1,{text:'first'}),await make('chat',2,{text:'second'}),third])await service.receive({type:'event',body:{origin:token}},link);
     let selected=service.snapshot(view).selected;
     if(selected.chat.map(m=>m.text).join(',')!=='third,first,second')throw Error('Verified reordered chat lost or duplicated');
     if(!selected.chatWarning||!service.exportChat(view).includes('may be missing'))throw Error('Gap warning absent from view/export');
     service.releaseView(view);
     await service.receive({type:'event',body:{origin:await make('chat',4,{text:'while closed'})}},link);
     service.select(view,node);selected=service.snapshot(view).selected;
     if(selected.chat.length!==3||!selected.chatWarning.includes('no open view')||!service.exportChat(view).includes('discarded'))throw Error('Unsubscribed history not disclosed');
     await service.send(view,'chess.move','e4');
     await service.receive({type:'event',body:{origin:await make('chess.move',2,{match_id:node,ply:2,notation:'e5'})}},link);
     selected=service.snapshot(view).selected;
     if(!selected.conflict||selected.moves.length!==1||!service.exportPgn(view).includes('Incomplete stream'))throw Error('Chess gap did not freeze legal prefix');
     if(selected.chat.length!==3||!selected.chatWarning)throw Error('Move processing changed chat');
   }finally{service.close();subscriptions.close();}
   await new Promise(resolve=>setTimeout(resolve,0));const remaining=sessionBudget(owner).snapshot();if(remaining.metadataBytes||remaining.replayStreams||remaining.crypto||remaining.queuedBytes)throw Error('Reordered room leaked: '+JSON.stringify(remaining));
 });
 const {TrafficScheduler}=await import('./network/traffic-scheduler.mjs');
 await testAsync('scheduler reserves control bytes without queuing crypto work',async()=>{
   const session={},owner={},scheduler=new TrafficScheduler(session);scheduler.register(owner);const order=[];
   const bulk=Array.from({length:60},()=>scheduler.submit(owner,'bulk',32768,()=>order.push('bulk'))),excessBulk=scheduler.submit(owner,'bulk',32768,()=>{});
   const control=Array.from({length:4},()=>scheduler.submit(owner,'control',32768,()=>order.push('control'))),excessControl=scheduler.submit(owner,'control',32768,()=>{});
   if(sessionBudget(session).snapshot().crypto!==0||sessionBudget(session).snapshot().queuedBytes!==2097152)throw Error('Wrong queued accounting');
   const results=await Promise.allSettled([...bulk,excessBulk,...control,excessControl]);if(results[60].status!=='rejected'||results[65].status!=='rejected'||results.filter(r=>r.status==='fulfilled').length!==64)throw Error('Queue admission did not preserve reserve');
   if(order.indexOf('control')>order.indexOf('bulk'))throw Error('Control starved behind bulk');scheduler.unregister(owner);if(sessionBudget(session).snapshot().metadataBytes||sessionBudget(session).snapshot().queuedBytes)throw Error('Scheduler leaked');
 });
 await testAsync('scheduler weights bytes and permits progress in every class',async()=>{
   const session={},owner={},scheduler=new TrafficScheduler(session);scheduler.register(owner);const order=[];
   const tasks=[];for(let i=0;i<32;i++)tasks.push(scheduler.submit(owner,'bulk',32768,()=>order.push('bulk')));for(let i=0;i<32;i++)tasks.push(scheduler.submit(owner,'control',32768,()=>order.push('control')));
   await Promise.all(tasks);if(order.slice(0,10).filter(c=>c==='control').length!==8||order.filter(c=>c==='bulk').length!==32)throw Error('DRR byte weights incorrect');scheduler.unregister(owner);
 });
 await testAsync('scheduler cancellation retains active work charges until completion',async()=>{
   const session={},owner={},scheduler=new TrafficScheduler(session);scheduler.register(owner);let finish;
   const active=scheduler.submit(owner,'bulk',4000,()=>new Promise(resolve=>finish=resolve));await new Promise(resolve=>setTimeout(resolve,0));
   const queued=scheduler.submit(owner,'interactive',1000,()=>{});scheduler.unregister(owner);await rejectsAsync(()=>queued);
   if(sessionBudget(session).snapshot().queuedBytes!==4000||!sessionBudget(session).snapshot().metadataBytes)throw Error('Active work hidden');finish();await active;
   if(sessionBudget(session).snapshot().queuedBytes||sessionBudget(session).snapshot().metadataBytes)throw Error('Cancelled scheduler leaked');
 });
 await testAsync('tiny queued sends cannot bypass global job/control limits',async()=>{
   const session={},owner={},scheduler=new TrafficScheduler(session);scheduler.register(owner);const tasks=Array.from({length:120},()=>scheduler.submit(owner,'bulk',1,()=>{})),extraApp=scheduler.submit(owner,'bulk',1,()=>{});
   const control=Array.from({length:8},()=>scheduler.submit(owner,'control',1,()=>{})),extraControl=scheduler.submit(owner,'control',1,()=>{});
   const results=await Promise.allSettled([...tasks,extraApp,...control,extraControl]);if(results[120].status!=='rejected'||results[129].status!=='rejected'||results.filter(r=>r.status==='fulfilled').length!==128)throw Error('Tiny-job bound bypassed');scheduler.unregister(owner);if(sessionBudget(session).snapshot().metadataBytes)throw Error('Tiny jobs leaked');
 });
 await testAsync('native buffer guard preserves space for control sends',async()=>{
   const owner=await identity.beginSession(config,'anonymous'),remote=await identity.beginSession(config,'anonymous'),link=new PeerLink(owner,{identity:config.identity,rtc:{iceServers:[]}}),wires=[];
   link.remote={payload:{sender:remote.public}};link.connectionId=mesh.newNodeId();link.channel={readyState:'open',bufferedAmount:229376,send:wire=>wires.push(wire),close(){this.readyState='closed';}};
   await rejectsAsync(()=>link.sendPacket('chat','interactive','interactive'));await link.sendPacket('hello','','control');if(wires.length!==1)throw Error('Native control reserve failed');link.close();
   if(sessionBudget(owner).snapshot().metadataBytes||sessionBudget(owner).snapshot().queuedBytes)throw Error('Buffer reserve fixture leaked');
 });
 await testAsync('queued expired application work is rejected before transmission',async()=>{
   const owner=await identity.beginSession(config,'anonymous'),remote=await identity.beginSession(config,'anonymous'),link=new PeerLink(owner,{identity:config.identity,rtc:{iceServers:[]}}),wires=[];let finish;
   link.remote={payload:{sender:remote.public}};link.connectionId=mesh.newNodeId();link.channel={readyState:'open',bufferedAmount:0,send:wire=>wires.push(wire),close(){this.readyState='closed';}};
   const active=link.scheduler.submit(link,'control',1000,()=>new Promise(resolve=>finish=resolve));await new Promise(resolve=>setTimeout(resolve,0));
   const queued=link.sendPacket('chat','expires','interactive',Math.floor(Date.now()/1000)+1);await new Promise(resolve=>setTimeout(resolve,1100));finish();await active;let error;try{await queued;}catch(e){error=e;}
   if(!error?.message.includes('expired')||wires.length||link.tx)throw Error('Expired message transmitted');link.close();if(sessionBudget(owner).snapshot().metadataBytes||sessionBudget(owner).snapshot().queuedBytes)throw Error('Expired queue leaked');
 });
 await testAsync('control floods are rate bounded without blocking interactive admission',async()=>{
   let clock=0;const session={},a={},b={},c={},scheduler=new TrafficScheduler(session,{clock:()=>clock});for(const owner of [a,b,c])scheduler.register(owner);
   const tasks=[];for(const owner of [a,b])for(let i=0;i<32;i++)tasks.push(scheduler.submit(owner,'control',1,()=>{}));
   const peerExcess=scheduler.submit(a,'control',1,()=>{}),globalExcess=scheduler.submit(c,'control',1,()=>{}),interactive=scheduler.submit(c,'interactive',1,()=>{});
   const results=await Promise.allSettled([...tasks,peerExcess,globalExcess,interactive]);if(results[64].status!=='rejected'||results[65].status!=='rejected'||results[66].status!=='fulfilled')throw Error('Control rate bound failed');clock=1000;await scheduler.submit(c,'control',1,()=>{});for(const owner of [a,b,c])scheduler.unregister(owner);
 });
 {
 const {bootstrapDescriptors}=await import('./network/bootstrap-source.mjs');
 check('bootstrap bundle retains single-descriptor compatibility',()=>{if(bootstrapDescriptors({version:'codi-bootstrap-bundle/1',seed:'seed',descriptor:'leaf'})[0]!=='leaf')throw Error('Legacy bundle changed');});
 check('bootstrap bundle allows root-only revocation metadata',()=>{if(bootstrapDescriptors({version:'codi-bootstrap-bundle/2',seed:'seed',descriptors:[]}).length)throw Error('Root-only bundle changed');});
 check('bootstrap bundle bounds and exact schema',()=>{for(const bundle of [{version:'codi-bootstrap-bundle/2',seed:'seed',descriptors:['leaf','leaf']},{version:'codi-bootstrap-bundle/2',seed:'seed',descriptors:Array.from({length:9},(_,i)=>'leaf'+i)},{version:'codi-bootstrap-bundle/2',seed:'seed',descriptor:'leaf'},{version:'codi-bootstrap-bundle/2',seed:'seed',descriptors:[],admin:true},{version:'codi-bootstrap-bundle/3',seed:'seed',descriptors:[]}])rejects(()=>bootstrapDescriptors(bundle));});
 const {BootstrapDirectory,SEED_TYPE,STEWARD_TYPE}=await import('./network/bootstrap.mjs');
 const root=await c.makeKey(),steward=await c.makeKey(),keyId=await c.thumbprint(steward.publicKey),realm=mesh.newNodeId(),discoveryScope=mesh.newNodeId();
 const endpoint='wss://ksu.codes/rendezvous';let discoveryTime=t;
 const grant={key_id:keyId,public_key:steward.publicKey,endpoints:[endpoint],scopes:[discoveryScope],limits:{lease_seconds:120,sample_size:8,signal_bytes:32768},exp:t+600,failure_domain:'loopback-test'};
 const seed={version:SEED_TYPE,realm,revision:1,iat:t,exp:t+600,stewards:[grant]};
 const record={version:STEWARD_TYPE,realm,key_id:keyId,revision:1,iat:t,exp:t+120,endpoint,scopes:[discoveryScope],limits:{...grant.limits}};
 const ds={},directory=new BootstrapDirectory(ds,{realm,rootKey:root.publicKey,endpoints:[endpoint],clock:()=>discoveryTime});
 const seedToken=await c.signJws(seed,root.privateKey,SEED_TYPE),recordToken=await c.signJws(record,steward.privateKey,STEWARD_TYPE);
 await testAsync('bootstrap requires release-pinned authority',async()=>{await rejectsAsync(()=>directory.acceptSeed('not-a-jws'));const bad=await c.signJws(seed,steward.privateKey,SEED_TYPE);await rejectsAsync(()=>directory.acceptSeed(bad));});
 await testAsync('steward requires fresh explicit delegation',()=>rejectsAsync(()=>directory.acceptSteward(recordToken)));
 await testAsync('signed bootstrap and scoped steward verified',async()=>{await directory.acceptSeed(seedToken);await directory.acceptSteward(recordToken);if(directory.snapshot(discoveryScope).contacts.length!==1||directory.snapshot().contacts[0].failure_domain!=='loopback-test'||!c.sameKey(directory.snapshot().contacts[0].public_key,steward.publicKey)||directory.snapshot(mesh.newNodeId()).contacts.length)throw Error('Scope filtering failed');});
 for(const [label,patch] of [['endpoint',{endpoint:'wss://other.example/rendezvous'}],['scope',{scopes:[mesh.newNodeId()]}],['capacity',{limits:{...grant.limits,sample_size:16}}],['lifetime',{exp:t+301}],['realm',{realm:mesh.newNodeId()}],['extra field',{admin:true}]])await testAsync('steward rejects unauthorized '+label,async()=>{const bad=await c.signJws({...record,...patch,revision:2},steward.privateKey,STEWARD_TYPE);await rejectsAsync(()=>directory.acceptSteward(bad));if(directory.snapshot().contacts.length!==1)throw Error('Invalid input poisoned valid contact');});
 await testAsync('bootstrap endpoints remain release-pinned',async()=>{const bad=await c.signJws({...seed,revision:2,stewards:[{...grant,endpoints:['wss://other.example/']}]},root.privateKey,SEED_TYPE);await rejectsAsync(()=>directory.acceptSeed(bad));});
 await testAsync('bootstrap revision rollback rejected without losing contacts',async()=>{await directory.acceptSeed(await c.signJws({...seed,revision:2},root.privateKey,SEED_TYPE));await rejectsAsync(()=>directory.acceptSeed(seedToken));if(directory.snapshot().revision!==2||directory.snapshot().contacts.length!==1)throw Error('Seed rollback mutated state');});
 await testAsync('delegation revocation hides previously valid contact',async()=>{await directory.acceptSeed(await c.signJws({...seed,revision:3,stewards:[{...grant,scopes:[mesh.newNodeId()]}]},root.privateKey,SEED_TYPE));if(directory.snapshot().contacts.length)throw Error('Revoked scope still visible');await directory.acceptSeed(await c.signJws({...seed,revision:4},root.privateKey,SEED_TYPE));});
 await testAsync('expired records disappear without forgetting rollback floor',async()=>{discoveryTime=t+121;if(directory.snapshot().contacts.length)throw Error('Expired contact returned');const next=await c.signJws({...record,revision:2,iat:discoveryTime,exp:discoveryTime+120},steward.privateKey,STEWARD_TYPE);await directory.acceptSteward(next);await rejectsAsync(()=>directory.acceptSteward(recordToken));if(directory.snapshot().contacts.length!==1)throw Error('Rollback mutated state');});
 await testAsync('authenticated steward fork freezes contact',async()=>{const fork=await c.signJws({...record,revision:2,iat:discoveryTime,exp:discoveryTime+119},steward.privateKey,STEWARD_TYPE);await rejectsAsync(()=>directory.acceptSteward(fork));if(directory.snapshot().contacts.length)throw Error('Fork still usable');});
 await testAsync('authenticated bootstrap fork freezes directory',async()=>{const fork=await c.signJws({...seed,revision:4,exp:t+601},root.privateKey,SEED_TYPE);await rejectsAsync(()=>directory.acceptSeed(fork));if(!directory.snapshot().frozen)throw Error('Seed fork not frozen');});
 await testAsync('discovery disposal releases shared accounting',async()=>{directory.close();directory.close();if(sessionBudget(ds).snapshot().metadataBytes||sessionBudget(ds).snapshot().crypto)throw Error('Discovery accounting leak');await rejectsAsync(()=>directory.acceptSeed(seedToken));});
 }
 return results;
})().then(done).catch(e=>done([{status:'FAIL',error:e.message}]));'''
 result=req('/session/'+s+'/execute/async',{'script':code,'args':[]})
 Path('.build/checks/protocol-result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));assert all(r['status']=='PASS' for r in result)
finally:req('/session/'+s,method='DELETE')
