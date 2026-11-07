// Passive Puppeteer/CDP-backed lifecycle events on ONE owned page. No pause,
// Worker replacement, message interception or model/product writes.
export async function observeReplay(page,{label,frameURL,work}){
 const start=performance.now(),created=[],destroyed=[],samples=[],sampleErrors=[],rows=new Map(),ids=new WeakMap();let sequence=0,busy=false,stopped=false;
 const clock=()=>performance.now()-start,id=w=>{if(!ids.has(w))ids.set(w,++sequence);return ids.get(w);};
 const before=page.workers().map(w=>({id:id(w),url:w.url()}));
 const onCreate=w=>{const row={id:id(w),url:w.url(),startedMS:clock(),destroyedMS:null,lifetimeMS:null};rows.set(w,row);created.push(row);};
 const onDestroy=w=>{const row=rows.get(w);destroyed.push({id:id(w),url:w.url(),atMS:clock(),createdDuringPhase:!!row});if(row){row.destroyedMS=clock();row.lifetimeMS=row.destroyedMS-row.startedMS;}};
 page.on('workercreated',onCreate);page.on('workerdestroyed',onDestroy);
 async function sample(){if(busy||stopped)return;busy=true;try{const own=page.frames().filter(f=>f.url()===frameURL);for(const f of own){try{const state=await f.evaluate(()=>{const c=globalThis.__CAD_APP,craft=c?.craftService;return !craft?null:{resources:{...craft.engineResourceUsage},processing:craft.isProcessing,epoch:craft.evaluationEpoch,modelCount:craft.models$?.value?.length,historyLength:craft.modifications$?.value?.history?.length,pointer:craft.modifications$?.value?.pointer};});if(state)samples.push({atMS:clock(),frameId:f._id,state});}catch(e){sampleErrors.push({atMS:clock(),reason:'Owned staging frame may be removed on normal publication',message:e.message});}}}finally{busy=false;}}
 await sample();const interval=setInterval(sample,500);let result,error,commandWallMS;
 try{const t=performance.now();try{result=await work();}finally{commandWallMS=performance.now()-t;}await new Promise(r=>setTimeout(r,250));await sample();}catch(e){error={name:e.name,code:e.code??null,message:e.message,committed:e.committed===true,possiblyCommitted:e.possiblyCommitted===true};}
 finally{stopped=true;clearInterval(interval);while(busy)await new Promise(r=>setTimeout(r,5));page.off('workercreated',onCreate);page.off('workerdestroyed',onDestroy);}
 const after=page.workers().map(w=>({id:id(w),url:w.url()})),byURL={};for(const r of created){const group=byURL[r.url]??={started:0,destroyed:0,observedLifetimesMS:[]};group.started++;if(r.destroyedMS!==null){group.destroyed++;group.observedLifetimesMS.push(r.lifetimeMS);}}
 const row={label,quality:'passive-owned-page-worker-lifecycle-and500ms-resource-sampling',commandWallMS,before,after,created,destroyed,byURL,resourceSamples:samples,sampleErrors,error,result,limits:['Worker lifecycle counts are actual CDP-backed page events, not message interception','Single-purpose operation/client source corroborates task kinds; request bodies are not captured','500ms resource samples can miss short-lived states and do not measure WASM memory/native shape count','Sampling changes latency; no uninstrumented performance or cold-cache claim','Only this owned page; other browser contexts/services unchanged']};
 return row; // Caller records raw lifecycle data before validating it.
}
