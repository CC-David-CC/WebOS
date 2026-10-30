// Load-only isolation: the published SDK bytes stay unchanged. Each logical
// agent uses a separate real IndexedDB namespace and its own window/keys/pool.
const query=new URL(location.href).searchParams,run=query.get('run'),index=query.get('agent');
if(!/^[a-f0-9]{32}$/.test(run)||!/^\d{1,5}$/.test(index))throw Error('Invalid owned agent namespace');
const native=indexedDB,prefix=`codi-agent-${run}-${index}-`;
const factory=new Proxy(native,{get(target,key){
  if(key==='open')return(name,version)=>target.open(prefix+name,version);
  if(key==='deleteDatabase')return name=>target.deleteDatabase(prefix+name);
  if(key==='databases')return async()=>(await target.databases()).filter(d=>d.name?.startsWith(prefix)).map(d=>({...d,name:d.name.slice(prefix.length)}));
  const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value;
}});
Object.defineProperty(globalThis,'indexedDB',{value:factory,configurable:false});
window.agentDatabasePrefix=prefix;
// Bounded test-only request accounting; no request bodies or credentials kept.
window.agentHTTP={startedAt:Date.now(),requests:0,byOperation:{},byStatus:{},transportErrors:0,byTransportError:{},buckets:[],refusals:[]};
const observedFetch=fetch;
window.fetch=async(url,options)=>{
  const path=new URL(typeof url==='string'?url:url.url,location.href).pathname;
  const reader=options?.headers?.['Codi-Reader']==='rendezvous/1'||path.includes('/rooms/readers/');let operation='';
  try{operation=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation||'';}catch{}
  const key=(reader?'directory:':'ordinary:')+path+':'+operation,h=agentHTTP;
  h.requests++;h.byOperation[key]=(h.byOperation[key]||0)+1;
  const at=Math.floor((Date.now()-h.startedAt)/10000)*10;
  let bucket=h.buckets.at(-1);if(!bucket||bucket.at!==at){bucket={at,ordinary:0,directory:0,other:0};h.buckets.push(bucket);if(h.buckets.length>360)h.buckets.shift();}
  bucket[reader?'directory':path.startsWith('/rooms/')?'ordinary':'other']++;
  try{
    const response=await observedFetch(url,options);h.byStatus[response.status]=(h.byStatus[response.status]||0)+1;
    if([429,503].includes(response.status)&&h.refusals.length<32){let reason='';try{reason=(await response.clone().json()).error||'';}catch{}h.refusals.push({at:Date.now()-h.startedAt,key,status:response.status,reason});}
    return response;
  }catch(error){h.transportErrors++;const name=['AbortError','TimeoutError','TypeError','NetworkError'].includes(error?.name)?error.name:'Other';h.byTransportError[name]=(h.byTransportError[name]||0)+1;throw error;}finally{if(window.httpOperations?.length>256)httpOperations.splice(0,httpOperations.length-256);}
};
try{
  await import('./fixture.mjs');
  if(window.fixtureFatal)throw Error(fixtureFatal);
  window.agentWireBytes=0;window.agentReadFallback=true;window.agentDirectoryEnabled=true;window.agentBlockedReads=0;
  const fetchNative=fetch;window.fetch=(url,options)=>{
    const path=typeof url==='string'?url:url.url,reader=options?.headers?.['Codi-Reader']==='rendezvous/1'||path.includes('/rooms/readers/');
    if(reader&&!agentDirectoryEnabled)return Promise.reject(new TypeError('Owned agent discovery outage'));
    if(!reader&&!agentReadFallback&&(path.includes('/rooms/')||path.includes('/api/v1/room-control/'))){agentBlockedReads++;return Promise.reject(new TypeError('Owned agent read fallback outage'));}
    return fetchNative(url,options);
  };
  const prior=client.peerState.bind(client);client.peerState=e=>{
    if(e.state==='ready'&&!e.agentWireObserved&&e.link.channel){e.agentWireObserved=true;const send=e.link.channel.send.bind(e.link.channel);
      e.link.channel.send=wire=>{agentWireBytes+=new TextEncoder().encode(wire).length;return send(wire);};}
    return prior(e);
  };
  const graph=await(await fetch('/network-release.json')).json();
  const {sessionBudget}=await import('/'+graph.directory+'/resource-budget.mjs');window.agentBudget=sessionBudget(currentSession);
  const {renewSession}=await import('/'+graph.directory+'/identity.mjs');let renewing=false;window.agentRenewals=0;window.agentRenewalError='';
  window.agentMaintainIdentity=async()=>{
    if(renewing||currentSession.trust.claims.exp-Date.now()/1000>180)return;
    renewing=true;try{await renewSession(config,currentSession);agentRenewals++;agentRenewalError='';}catch(error){agentRenewalError=error.message;}finally{renewing=false;}
  };
  window.agentReady=true;
}catch(error){window.agentFatal=error.stack;}
