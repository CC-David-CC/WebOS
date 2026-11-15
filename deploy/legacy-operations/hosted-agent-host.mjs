// Supervisor sends commands/room IDs, never checkpoint/chat data, between agents.
const agents=new Map(),run=new URL(location.href).searchParams.get('run');
if(!/^[a-f0-9]{32}$/.test(run))throw Error('Invalid load run');
async function until(fn,seconds=60){const stop=performance.now()+seconds*1000;while(true){const value=fn();if(value)return value;if(performance.now()>stop)throw Error('Agent readiness timeout');await new Promise(r=>setTimeout(r,25));}}
const actor=i=>{const a=agents.get(i);if(!a)throw Error('Unknown owned agent');return a.contentWindow;};
let pump=null,sampler=null,identityMaintenance=null,lastSample=0;
const telemetry={samples:0,maxSampleGapMs:0,peaks:{}};
function sample(){
  const now=performance.now();if(lastSample)telemetry.maxSampleGapMs=Math.max(telemetry.maxSampleGapMs,now-lastSample);lastSample=now;telemetry.samples++;
  for(const frame of agents.values()){
    const w=frame.contentWindow,r=w.client.snapshot().delivery.readers,b=w.agentBudget.snapshot();
    const values={neighbors:r.members.length,automatic:r.automaticConnections,pending:r.pending,jobs:r.jobs,...b};
    for(const [k,v] of Object.entries(values))if(k!=='closed')telemetry.peaks[k]=Math.max(telemetry.peaks[k]||0,v);
  }
}
window.agentLab={
  async start(i,owner=false){
    if(agents.has(i))throw Error('Agent already exists');
    const frame=document.createElement('iframe');frame.width='2';frame.height='2';frame.title='Owned SDK load agent '+i;
    agents.set(i,frame);frame.src='/agent.html?run='+run+'&agent='+i+'&directory=1'+(owner?'&owner=1':'')+(new URL(location.href).searchParams.has('sync')?'&sync=1':'')+(new URL(location.href).searchParams.has('recover')?'&recover=1':'')+(new URL(location.href).searchParams.has('coordinator')?'&coordinator=1':'');document.body.append(frame);
    await until(()=>{const w=actor(i);if(w.agentFatal||w.fixtureFatal)throw Error(w.agentFatal||w.fixtureFatal);return w.agentReady;});
    if(!identityMaintenance)identityMaintenance=setInterval(()=>{for(const f of agents.values())f.contentWindow.agentMaintainIdentity?.();},10000);
    return {index:i,sid:actor(i).currentSession.public.sid,prefix:actor(i).agentDatabasePrefix};
  },
  async create(i,label){return actor(i).client.create(label);},
  async open(i,node){await actor(i).client.open(node);return true;},
  async send(i,node,text){const w=actor(i);await until(()=>!w.client.snapshot(node).selected?.busy);return w.client.send(node,text);},
  setFallback(i,value){actor(i).agentReadFallback=value;},
  setReaderFallback(value){let changed=0;for(const [i] of agents)if(i!==0){actor(i).agentReadFallback=value;changed++;}return changed;},
  setDirectory(i,value){actor(i).agentDirectoryEnabled=value;},
  startPump(){if(pump)return;pump=setInterval(()=>{for(const frame of agents.values())frame.contentWindow.client.tick();},1000);sampler=setInterval(sample,1000);sample();for(const f of agents.values())f.contentWindow.client.tick();},
  stopPump(){clearInterval(pump);clearInterval(sampler);pump=null;sampler=null;},
  telemetry(){return structuredClone(telemetry);},
  recoveryPolicy(){return [...agents].map(([i])=>actor(i).client.snapshot().delivery.proposalRecovery);},
  directoryPolicy(){return [...agents].map(([i])=>actor(i).client.snapshot().delivery.directory?.mode??null);},
  partition(groups=null){
    // Fault injection only: reject cross-island signed signaling and close
    // existing crossing links. No offer/answer/checkpoint is manufactured.
    const assignment=groups===null?null:new Map(groups);
    const sender=token=>{const part=token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/');return JSON.parse(atob(part)).sender.sid;};
    for(const [i] of agents){
      const w=actor(i);w.agentPartition=assignment;
      if(!w.agentPartitionInstalled){
        const answer=w.pool.answer.bind(w.pool),accept=w.pool.accept.bind(w.pool);
        const allowed=token=>!w.agentPartition||w.agentPartition.get(sender(token))===w.agentPartition.get(w.currentSession.public.sid);
        w.pool.answer=(token,options)=>{if(!allowed(token))throw Error('Owned cross-island signaling partition');return answer(token,options);};
        w.pool.accept=(id,token)=>{if(!allowed(token))throw Error('Owned cross-island signaling partition');return accept(id,token);};
        w.agentPartitionInstalled=true;
      }
      if(assignment)for(const e of w.pool.list())if(e.peerId&&assignment.get(e.peerId)!==assignment.get(w.currentSession.public.sid))w.pool.closeEntry(e.id,'Owned cross-island link partition');
    }
  },
  closePeer(i,sid){const w=actor(i),e=w.pool.list().find(e=>e.state==='ready'&&e.peerId===sid);if(!e)throw Error('Owned ready link missing');w.pool.closeEntry(e.id,'Owned redundant bridge failure');return e.id;},
  httpStats(){return [...agents].map(([index])=>({index,...structuredClone(actor(index).agentHTTP)}));},
  snapshots(node){return [...agents].map(([i])=>{const w=actor(i);return {index:i,sid:w.currentSession.public.sid,state:w.client.snapshot(node),peers:w.pool.list(),wireBytes:w.agentWireBytes,blockedReads:w.agentBlockedReads,renewals:w.agentRenewals,renewalError:w.agentRenewalError};});},
  summaries(node){return [...agents].map(([i])=>{const w=actor(i),s=w.client.snapshot(node);return {index:i,sid:w.currentSession.public.sid,state:{busy:s.busy,selected:s.selected?{count:s.selected.count,source:s.selected.source}:null},peers:w.pool.list().map(e=>({peerId:e.peerId,state:e.state})),wireBytes:w.agentWireBytes};});},
  async saved(i){
    return (await this.savedAll([i]))[0];
  },
  async savedAll(selected=[...agents.keys()]){
    if(selected.length>32||new Set(selected).size!==selected.length)throw Error('Bounded distinct agent inspection required');
    const databases=await indexedDB.databases();
    // Inspect actual native storage in this browser. Only the test supervisor
    // receives results; no checkpoint is passed to another client or SDK.
    return Promise.all(selected.map(i=>{
      const prefix=actor(i).agentDatabasePrefix,owned=databases.filter(d=>d.name.startsWith(prefix));
      if(owned.length!==1)throw Error('Agent does not own exactly one position database');
      return new Promise((resolve,reject)=>{const req=indexedDB.open(owned[0].name);req.onerror=()=>reject(req.error);req.onsuccess=()=>{
        const db=req.result;let rows;
        try{const tx=db.transaction('positions','readonly'),q=tx.objectStore('positions').getAll();q.onsuccess=()=>{rows=q.result;};
          tx.oncomplete=()=>{db.close();resolve({index:i,database:owned[0].name,rows});};tx.onabort=()=>{db.close();reject(tx.error||Error('Storage inspection aborted'));};
        }catch(error){db.close();reject(error);}
      };});
    }));
  },
  async close(){
    this.stopPump();clearInterval(identityMaintenance);identityMaintenance=null;const out=[];
    for(const [i,frame] of agents){const w=actor(i);await w.client.close();w.pool.close();const budget=w.agentBudget;
      await until(()=>Object.entries(budget.snapshot()).every(([k,v])=>k==='closed'||!v),15);out.push({index:i,budget:budget.snapshot()});frame.remove();}
    agents.clear();
    for(const db of await indexedDB.databases())if(db.name.startsWith('codi-agent-'+run+'-'))await new Promise((resolve,reject)=>{const r=indexedDB.deleteDatabase(db.name);r.onsuccess=resolve;r.onerror=()=>reject(r.error);r.onblocked=()=>reject(Error('Agent database still open'));});
    return out;
  }
};
const graph=await(await fetch('/network-release.json')).json();window.agentNetworkBase='/'+graph.directory;window.agentHostReady=true;
