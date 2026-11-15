// Research-only lifecycle manager. Does not expose the guest filesystem.
export function createSharedV86Compiler({valid,loadAssets,create,onIdle=()=>{}}){
 if(typeof valid!=='function'||typeof loadAssets!=='function'||typeof create!=='function')throw Error('Invalid compiler manager.');
 let service=null,setup=null,setupController=null,ready=false,closing=null;const leases=new Set();
 const check=()=>{if(closing)throw Error('Compiler is closing.');if(!valid())throw Error('Linux guest or account changed.');};
 const progress=text=>{for(const lease of leases)if(!lease.closed)try{lease.progress(text)}catch{}};
 function joinedSignal(a,b){const c=new AbortController(),abort=()=>c.abort();for(const s of [a,b])if(s){if(s.aborted)abort();else s.addEventListener('abort',abort,{once:true})}return {signal:c.signal,dispose(){for(const s of [a,b])s?.removeEventListener('abort',abort)}};}
 function waitFor(p,signal){if(signal.aborted)return Promise.reject(new DOMException('Build cancelled.','AbortError'));return new Promise((resolve,reject)=>{const abort=()=>finish(new DOMException('Build cancelled.','AbortError'));let done=false;const finish=(error,value)=>{if(done)return;done=true;signal.removeEventListener('abort',abort);error?reject(error):resolve(value)};signal.addEventListener('abort',abort,{once:true});p.then(value=>finish(null,value),error=>finish(error));});}
 function start(){
  setupController=new AbortController();const signal=setupController.signal;
  const run=(async()=>{try{progress('Loading compiler on this device…');const assets=await loadAssets(signal);check();if(signal.aborted)throw new DOMException('Build cancelled.','AbortError');service=await create({...assets,onProgress:progress});check();await service.install(signal);check();ready=true;}catch(e){if(service){await service.close().catch(()=>{});service=null}throw e}})();
  setup=run;run.finally(()=>{if(setup===run){setup=null;setupController=null}}).catch(()=>{});return run;
 }
 async function shutdown(){if(closing)return closing;closing=(async()=>{setupController?.abort();for(const lease of leases)lease.controller.abort();if(setup)await setup.catch(()=>{});await Promise.all([...leases].flatMap(lease=>[...lease.jobs].map(job=>job.catch(()=>{}))));if(service){await service.close();service=null}ready=false;onIdle()})();return closing;}
 function acquire(onProgress=()=>{}){
  check();if(typeof onProgress!=='function')throw Error('Invalid progress listener.');const lease={closed:false,controller:new AbortController(),jobs:new Set(),progress:onProgress,closePromise:null};leases.add(lease);
  return {
   async install(signal){if(lease.closed)throw Error('Compiler window closed.');check();if(ready)return;const link=joinedSignal(signal,lease.controller.signal);try{await waitFor(setup||start(),link.signal);check()}finally{link.dispose()}},
   async build(source,{signal}={}){if(lease.closed)throw Error('Compiler window closed.');check();if(!ready||!service)throw Error('Prepare the compiler first.');const link=joinedSignal(signal,lease.controller.signal),job=service.build(source,{signal:link.signal});lease.jobs.add(job);try{return await job}finally{lease.jobs.delete(job);link.dispose()}},
   close(){if(lease.closePromise)return lease.closePromise;lease.closed=true;lease.controller.abort();lease.closePromise=(async()=>{await Promise.all([...lease.jobs].map(job=>job.catch(()=>{})));leases.delete(lease);if(!leases.size)await shutdown()})();return lease.closePromise;}
  };
 }
 return {acquire,shutdown,isClosing:()=>!!closing,finished:()=>closing||Promise.resolve()};
}
