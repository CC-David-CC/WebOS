/** Repeat actual hosted editor startup with three concurrent clean browser contexts. */
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {randomBytes} from 'node:crypto';
import puppeteer from 'puppeteer-core';
const origin=process.env.WEBOS_TEST_ORIGIN, output=process.env.WEBOS_TEST_OUTPUT && path.resolve(process.env.WEBOS_TEST_OUTPUT);
assert.equal(origin,'https://ksu.codes','Only the user-designated test site is allowed.');
assert(output && output!==process.cwd() && !output.startsWith(process.cwd()+path.sep));await mkdir(output,{mode:0o700});
const tracing=process.env.WEBOS_TEST_STARTUP_TRACE==='1', rounds=tracing?1:2;
const report={tracing,status:'FAIL',origin,scope:'Repeated three-concurrent-editor startup; unchanged product120s timeout; disposable test account',rounds:[],diagnostics:[]};
let browser;const username='startup'+randomBytes(6).toString('hex'),password=randomBytes(18).toString('base64url');
try {
 browser=await puppeteer.launch({executablePath:'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],userDataDir:path.join(output,'browser-profile')});
 for(let round=0;round<rounds;round++){
  const contexts=[],checks=[];
  try {
   for(let index=0;index<3;index++){
    const context=await browser.createBrowserContext();contexts.push(context);const page=await context.newPage();await page.setViewport({width:1440,height:1000});page.setDefaultTimeout(130000);
    const entry={index,ready:false};checks.push(entry);
    if(tracing)await page.evaluateOnNewDocument(()=>{
      const trace=(stage,detail)=>console.debug('WEBOS_STARTUP_TRACE '+JSON.stringify({stage,detail,time:performance.now()}));
      trace('environment',{secure:isSecureContext,webgpu:!!navigator.gpu});
      function wrap(object,key,label){if(!object||typeof object[key]!=='function')return;const original=object[key];object[key]=function(...args){trace(label+':start',key==='getContext'?args[0]:undefined);let value;try{value=Reflect.apply(original,this,args);}catch(error){trace(label+':throw',error.name);throw error;}if(value&&typeof value.then==='function')value.then(()=>trace(label+':resolved'),error=>trace(label+':rejected',String(error)));else trace(label+':returned',value!==null);return value;};}
      try{for(const name of ['instantiateStreaming','instantiate','compileStreaming','compile'])wrap(WebAssembly,name,'wasm.'+name);wrap(HTMLCanvasElement.prototype,'getContext','canvas.context');if(navigator.gpu)wrap(Object.getPrototypeOf(navigator.gpu),'requestAdapter','gpu.adapter');if(globalThis.GPUAdapter)wrap(GPUAdapter.prototype,'requestDevice','gpu.device');}catch(error){trace('instrumentation-error',error.name);}
    });
    page.on('console',message=>{if(message.text().startsWith('WEBOS_STARTUP_TRACE ')){const event=JSON.parse(message.text().slice('WEBOS_STARTUP_TRACE '.length));report.diagnostics.push({round,index,type:'startup-trace',...event});console.log(JSON.stringify({round,index,...event}));}});
    page.on('pageerror',error=>report.diagnostics.push({round,index,type:'pageerror',message:error.message}));
    page.on('console',message=>{if(['warn','error'].includes(message.type())&&/WebGL|WebAssembly|GPU|memory|CompileError|RuntimeError/i.test(message.text()))report.diagnostics.push({round,index,type:message.type(),message:message.text().slice(0,1000)});});
    page.on('requestfailed',request=>report.diagnostics.push({round,index,type:'requestfailed',path:new URL(request.url()).pathname,error:request.failure()?.errorText}));
    page.on('requestfinished',request=>{if(new URL(request.url()).pathname.endsWith('.wasm'))entry.wasmFinishedAt=Date.now();});
    await page.goto(origin,{waitUntil:'networkidle0'});await page.waitForSelector('.login-gate[data-phase=ready]');
    const register=round===0&&index===0;if(register)await page.click('.login-toggle');await page.type('[name=username]',username);await page.type('[name=password]',password);if(register)await page.type('[name=confirmation]',password);await page.click('[type=submit]');await page.waitForSelector('.webos-desktop');
    await page.bringToFront();entry.startedAt=Date.now();await page.click('[aria-label=Applications]');await page.click('[data-app-id=wordcraft]');
    await page.waitForFunction(()=>['ready','failed'].includes(document.querySelector('.webos-window[aria-label=WordCraft]')?.dataset.phase));
    entry.elapsedMs=Date.now()-entry.startedAt;entry.phase=await page.$eval('.webos-window[aria-label=WordCraft]',el=>el.dataset.phase);entry.status=await page.$eval('.webos-wordcraft-status',el=>el.textContent).catch(()=>null);entry.ready=entry.phase==='ready';
    if(!entry.ready){await page.screenshot({path:path.join(output,`failure-round-${round}-editor-${index}.png`)});throw Error('Editor reported startup failure');}
    const handle=await page.$('.webos-wordcraft iframe'),frame=await handle.contentFrame();entry.initializedNativeAPI=await frame.evaluate(()=>!!window.wordcraft?.request);assert(entry.initializedNativeAPI);
    await frame.evaluate(async()=>{const state=await window.wordcraft.uiInspect();await window.wordcraft.request('engine.execute',{command:'text.insert',params:{text:'Concurrent startup test document.'},doc:state.document});});
    console.log(JSON.stringify({round,index,phase:entry.phase,elapsedMs:entry.elapsedMs}));
   }
   report.rounds.push({round,status:'PASS',editors:checks});
  }catch(error){report.rounds.push({round,status:'FAIL',error:{name:error.name,message:error.message},editors:checks});}
  finally{for(const context of contexts)await context.close();await writeFile(path.join(output,'result.json'),JSON.stringify(report,null,2)+'\n');}
 }
 report.status=report.rounds.length===rounds&&report.rounds.every(r=>r.status==='PASS')?'PASS':'FAIL';
 assert.equal(report.status,'PASS','At least one startup round failed; inspect retained report.');
}finally{await browser?.close();await writeFile(path.join(output,'result.json'),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({status:report.status,rounds:report.rounds.length,successfulStarts:report.rounds.flatMap(r=>r.editors).filter(e=>e.ready).length,origin}));
