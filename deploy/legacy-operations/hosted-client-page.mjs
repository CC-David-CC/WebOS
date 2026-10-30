import {HostedRooms} from './network/hosted-room-client.mjs';
import {HostedPositionStore,HostedPositionConflict} from './network/hosted-room-store.mjs';
import {makeKey,b64,verifyJws} from './network/crypto.mjs';
import {authenticatedRequest,verifyIdentity} from './network/identity.mjs';
import {sessionBudget} from './network/resource-budget.mjs';
import {verifyHostedRoom,verifyHostedLeaseBridge,verifyHostedLookup} from './network/hosted-room-authority.mjs';

const config=await(await fetch('/fixture-config.json')).json(),catalog=await(await fetch('/assets/desktop/apps.json')).json(),app=catalog.apps[0];
for(const style of app.styles){const link=document.createElement('link');link.rel='stylesheet';link.href='/'+app.path.slice(0,app.path.lastIndexOf('/')+1)+style;document.head.append(link);}
const {mount}=await import('/'+app.path);
let currentSession=null,client=null;const checks=window.hostedClientChecks=[];
const check=(name,ok)=>{if(!ok)throw Error(name);checks.push(name);};
const until=async fn=>{const end=performance.now()+20000;while(performance.now()<end){if(fn())return;await new Promise(r=>setTimeout(r,10));}throw Error('Hosted readiness timeout');};
async function session(operation,password){
  const pair=await makeKey(),s={privateKey:pair.privateKey,public:{sid:crypto.randomUUID(),key:pair.publicKey}};
  const data=operation==='anonymous'?{}:{operation,username:'client_owner',password};
  const result=await authenticatedRequest(config.identity,s,config.identity.apiBase+(operation==='anonymous'?'/anonymous':'/auth'),data);
  s.public=result.identity;s.token=result.session_token;s.trust=await verifyIdentity(s.public,config.identity);return s;
}
async function activate(s){client?.close();currentSession=s;client=new HostedRooms(s,config,{sessionValid:()=>currentSession===s});await client.start();return client;}
const network={get config(){return config;},get hostedRooms(){return client;},get hostedMode(){return true;},hostedError:'',observeHosted(w,changed,retired){return client.observe(changed,retired);}};
function view(){
  const lifetime=new AbortController(),cleanup=[],w={},host={version:2,w,network,signal:lifetime.signal,onDispose(fn){cleanup.push(fn);},storage:{downloadGuestFile(){}},ui:{
    make(tag,classes='',text=''){const el=document.createElement(tag);el.className=classes;el.textContent=text;return el;},
    textButton(label,handler){const el=document.createElement('button');el.type='button';el.textContent=label;el.addEventListener('click',handler,{signal:lifetime.signal});return el;}
  }};
  const mounted=mount(host);document.body.append(mounted.element);const v={w,el:mounted.element,destroy(){lifetime.abort();for(const fn of cleanup)fn();mounted.dispose();mounted.element.remove();}};return v;
}
function input(v,selector,text){const el=v.el.querySelector(selector);el.value=text;el.dispatchEvent(new Event('input',{bubbles:true}));}
const click=(v,key)=>{const el=v.el.querySelector('[data-hosted-'+key+']');if(el.disabled)throw Error('Disabled hosted action: '+key);el.click();};
const idle=()=>until(()=>client.snapshot().busy===0);

window.phaseOne=async password=>{
  const s=await session('register',password);await activate(s);const a=view(),b=view();await until(()=>a.el.querySelector('[data-hosted-create]').disabled===false);
  check('desktop-owned client uses a nonexportable browser signing key',s.privateKey.extractable===false&&client.snapshot().views===2);
  click(a,'create');await idle();const node=a.w.hostedRoomId;
  check('actual bundled app creates a verified saved chat and browser position',typeof node==='string'&&client.snapshot(node).selected.count===0);
  b.w.hostedRoomId=node;input(b,'[data-hosted-id]',node);click(b,'open');await idle();
  input(b,'[data-hosted-draft]','Independent second-window draft');input(a,'[data-hosted-draft]','First shared saved message');click(a,'send');await idle();
  check('two real app views share accepted history while retaining separate drafts',client.snapshot(node).selected.count===1&&b.el.querySelector('[data-hosted-history]').textContent.includes('First shared saved message')&&b.el.querySelector('[data-hosted-draft]').value==='Independent second-window draft'&&a.el.querySelector('[data-hosted-draft]').value==='');
  const baseline=sessionBudget(s).snapshot().metadataBytes;
  for(let n=0;n<12;n++){const v=view();await Promise.resolve();v.destroy();}
  check('twelve bundled view reopen cycles release listeners and observer accounting',client.snapshot().views===2&&sessionBudget(s).snapshot().metadataBytes===baseline);
  const nativeFetch=window.fetch;let lose=true,accepts=0;
  window.fetch=async(url,options)=>{let operation;try{operation=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
    const response=await nativeFetch(url,options);if(operation==='accept'){accepts++;if(lose){lose=false;await response.arrayBuffer();throw TypeError('Fixture discarded the real committed response');}}return response;};
  input(a,'[data-hosted-draft]','Recovered original operation');click(a,'send');await idle();
  check('lost committed response remains visibly unconfirmed and preserves the draft',client.snapshot(node).selected.pending&&a.el.querySelector('[data-hosted-draft]').value==='Recovered original operation');
  click(a,'retry');await idle();window.fetch=nativeFetch;
  check('signed lookup resolves the original operation without sending it twice',accepts===1&&!client.snapshot(node).selected.pending&&client.snapshot(node).selected.count===2&&a.el.querySelector('[data-hosted-draft]').value==='');
  let cancel=true;window.fetch=async(url,options)=>{let operation;try{operation=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
    const response=await nativeFetch(url,options);if(operation==='create'&&cancel){cancel=false;b.el.querySelector('[data-hosted-cancel]').click();}return response;};
  click(b,'create');await idle();window.fetch=nativeFetch;
  check('cancel after actual room creation keeps a persistent recoverable creation ID',client.snapshot().intents.length===1&&client.snapshot().rooms.length===1);
  const pending=client.snapshot().intents[0].id;a.destroy();b.destroy();let retired=0,escaped=false;
  client.observe(()=>{},()=>{throw Error('Fixture retire callback failure');});client.observe(()=>{},()=>retired++);
  try{client.close();}catch{escaped=true;}
  check('throwing retire callback cannot prevent other observers or shared resources from draining',!escaped&&retired===1&&sessionBudget(s).snapshot().metadataBytes===0);
  const resources=sessionBudget(s).snapshot();check('client close releases database views workers requests and shared accounting',resources.metadataBytes===0&&resources.crypto===0&&resources.repairJobs===0&&resources.admissionWork===0&&resources.queuedBytes===0);
  return {status:'PASS',checks:[...checks],node,pending,subject:s.public.sub};
};

window.phaseTwo=async(password,prior)=>{
  const s=await session('signin',password);await activate(s);
  check('actual page reload restores only this account bookmarks and pending intent',s.public.sub===prior.subject&&client.snapshot().rooms.some(r=>r.id===prior.node)&&client.snapshot().intents.some(r=>r.id===prior.pending));
  const v=view();await until(()=>v.el.querySelector('[data-hosted-recover-create]').disabled===false);click(v,'recover-create');await idle();
  check('creation recovery after reload reuses the same server operation ID',client.snapshot().rooms.length===2&&client.snapshot().intents.length===0);
  const other=v.w.hostedRoomId;input(v,'[data-hosted-id]',prior.node);click(v,'open');await idle();
  check('reloaded account verifies saved history with fresh session and signing key',client.snapshot(prior.node).selected.count===2&&client.snapshot(prior.node).selected.records.every(r=>r.historical)&&client.snapshot(prior.node).selected.records[0].author.sid!==s.public.sid);
  click(v,'join');await idle();input(v,'[data-hosted-draft]','Fresh returned account message');click(v,'send');await idle();
  check('fresh session continues with a distinct author stream and preserved prior history',client.snapshot(prior.node).selected.count===3&&client.snapshot(prior.node).selected.records.at(-1).sequence===1);
  v.destroy();client.close();await authenticatedRequest(config.identity,s,config.identity.apiBase+'/logout',{});
  const anonymous=await session('anonymous');await activate(anonymous);check('anonymous browser has an independent bookmark scope',client.snapshot().rooms.length===0);
  await client.open(prior.node);let refused=false;try{await client.create('Forbidden anonymous ownership');}catch{refused=true;}
  check('anonymous identity reads public history without gaining durable room ownership',client.snapshot(prior.node).selected.count===3&&refused);
  const NativeWorker=window.Worker;let workers=0;window.Worker=class extends NativeWorker{constructor(...args){super(...args);workers++;}};
  await client.join(prior.node);await client.send(prior.node,'Anonymous admitted message');await client.join(prior.node);window.Worker=NativeWorker;
  check('anonymous consent uses one bounded worker and membership refresh reuses admission',workers===1&&client.snapshot(prior.node).selected.count===4&&sessionBudget(anonymous).snapshot().admissionWork===0);
  const oldClient=client,oldView=view(),nativeFetch=window.fetch;let release,held=false;
  window.fetch=async(url,options)=>{let operation;try{operation=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
    if(operation==='describe'){held=true;await new Promise(r=>release=r);}return nativeFetch(url,options);};
  const inFlight=oldClient.open(prior.node).then(()=>false,()=>true);await until(()=>held);
  const returned=await session('signin',password);await activate(returned);release();check('account switch aborts an old in-flight request and retires its app view',(await inFlight)&&oldView.el.querySelector('[data-hosted-open]').disabled&&!oldClient.snapshot().ready&&sessionBudget(anonymous).snapshot().metadataBytes===0);
  oldView.destroy();window.fetch=nativeFetch;await client.open(prior.node);
  const floorStore=new HostedPositionStore();await floorStore.open();
  const scope=(await (async()=>{const {thumbprint}=await import('./network/crypto.mjs');return JSON.stringify([location.origin,config.hostedRooms.basePath,await thumbprint(config.hostedRooms.controllerKey),returned.public.sub]);})());
  const saved=await floorStore.get(scope,prior.node);let conflict=false;
  try{await floorStore.save(scope,prior.node,saved.label,{...saved.floor,count:saved.floor.count-1});}catch(e){conflict=e instanceof HostedPositionConflict;}
  check('atomic browser storage refuses a stale tab overwriting a newer position',conflict&&(await floorStore.get(scope,prior.node)).floor.count===4);
  const af=await(await fetch('/authority-fixture.json')).json(),oldRoom=await verifyHostedRoom(af.oldBootstrap,config.hostedRooms.controllerKey,config.identity,{now:af.oldNow});
  await floorStore.save(scope,af.node,oldRoom.policy.label,oldRoom.floor);let bridges=0;
  window.fetch=async(url,options)=>{try{if(JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation==='lease_bridge')bridges++;}catch{}return nativeFetch(url,options);};
  await client.open(af.node);window.fetch=nativeFetch;
  check('shared client fast-forwards a simulated15day authority gap with one bounded bridge',bridges===1&&client.snapshot(af.node).selected.count===2&&client.snapshot(af.node).selected.records.every(r=>r.acceptedAt<Date.now()/1000-14*86400));
  const freshRoom=await verifyHostedRoom(af.bootstrap,config.hostedRooms.controllerKey,config.identity,{now:af.now});
  const bridge=await verifyHostedLeaseBridge(af.bridge,freshRoom,{floor:oldRoom.floor,now:af.now});
  await verifyHostedRoom(af.bootstrap,config.hostedRooms.controllerKey,config.identity,{floor:oldRoom.floor,continuity:bridge,now:af.now});
  let badBridge=false;try{await verifyHostedLeaseBridge(af.badBridge,freshRoom,{floor:oldRoom.floor,now:af.now});}catch{badBridge=true;}
  check('fresh chosen-authority bridge verifies its exact old lease hash and rejects a signed substitution',badBridge);
  const found=await verifyHostedLookup(af.lookup,freshRoom,af.eventId,{now:af.now});let badLookup=false;
  try{await verifyHostedLookup(af.badLookup,freshRoom,af.eventId,{now:af.now});}catch{badLookup=true;}
  check('signed receipt lookup verifies old accepted data and rejects a substituted receipt',found.found&&found.record.text==='Old accepted note1'&&badLookup);
  const forged={...saved.floor,count:1000,hash:b64(crypto.getRandomValues(new Uint8Array(32)))};await floorStore.save(scope,prior.node,saved.label,forged);
  let rollback=false;try{await client.open(prior.node);}catch{rollback=true;}
  check('a higher retained local floor makes a rolled-back server state fail closed',rollback&&client.snapshot(prior.node).selected.count===4&&(await floorStore.get(scope,prior.node)).floor.count===1000);
  await client.open(other);check('position refusal leaves another stored chat usable',client.snapshot(other).selected.count===0);
  floorStore.close();client.close();const resources=sessionBudget(returned).snapshot();check('all current identity resources are released after account and storage tests',resources.metadataBytes===0&&resources.crypto===0&&resources.queuedBytes===0&&resources.repairJobs===0);
  return {status:'PASS',checks:[...checks],subject:returned.public.sub,acceptedMessages:4,other};
};
let expiryView,expiryNode;
window.prepareExpiry=async(password,node)=>{
  const s=await session('signin',password);await activate(s);expiryNode=node;expiryView=view();input(expiryView,'[data-hosted-id]',node);click(expiryView,'open');await idle();click(expiryView,'join');await idle();
  const nativeFetch=window.fetch;let held=false,release;
  window.fetch=async(url,options)=>{let operation;try{operation=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
    if(operation==='accept'){held=true;await new Promise(r=>release=r);}return nativeFetch(url,options);};
  input(expiryView,'[data-hosted-draft]','Cancelled before submission');click(expiryView,'send');await until(()=>held);click(expiryView,'cancel');release();await idle();window.fetch=nativeFetch;
  check('cancel before dispatch keeps the exact pending operation and unsaved draft',client.snapshot(node).selected.pending&&expiryView.el.querySelector('[data-hosted-draft]').value==='Cancelled before submission');
  return {status:'PASS',checks:[...checks]};
};
window.finishExpiry=async()=>{
  const originalNow=Date.now;Date.now=()=>originalNow()+120000;
  click(expiryView,'retry');await idle();
  check('later signed missing observation releases an expired submission without sending or deleting its draft',!client.snapshot(expiryNode).selected.pending&&client.snapshot(expiryNode).selected.count===0&&expiryView.el.querySelector('[data-hosted-draft]').value==='Cancelled before submission'&&!expiryView.el.querySelector('[data-hosted-send]').disabled);
  expiryView.destroy();client.close();return {status:'PASS',checks:[...checks]};
};
window.hostedClientReady=true;
