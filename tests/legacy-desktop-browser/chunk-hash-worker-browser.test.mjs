import assert from 'node:assert/strict';import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL||'http://127.0.0.1:19879/');assert.ok(['127.0.0.1','localhost'].includes(base.hostname));const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),context=await browser.createBrowserContext();
try{
 const p=await context.newPage();await p.goto(base.href);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]','worker'+Date.now().toString().slice(-8));await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 const result=await p.evaluate(async()=>{
  const f=(await serverFileContext()).files,bytes=new Uint8Array(2*1024*1024);for(let i=0;i<bytes.length;i+=65536)crypto.getRandomValues(bytes.subarray(i,i+65536));const saved=await f.write('worker.bin',bytes,null);
  const Original=window.Worker,counts={created:0,terminated:0,active:0,maxActive:0,ticksDuringWorkers:0};let onCreate=null;
  window.Worker=class extends Original{constructor(...args){super(...args);this._done=false;counts.created++;counts.active++;counts.maxActive=Math.max(counts.maxActive,counts.active);onCreate?.()}terminate(){if(!this._done){this._done=true;counts.terminated++;counts.active--}return super.terminate()}};
  const timer=setInterval(()=>{if(counts.active)counts.ticksDuringWorkers++},10),old=new Blob([new Uint8Array(16*1024*1024)]);
  try{
   const results=await Promise.all([f.readChunked('worker.bin',saved.sha256,old),f.readChunked('worker.bin',saved.sha256,old)]);
   if(results.some(x=>x.sha256!==saved.sha256)||counts.active!==0||counts.maxActive<2||counts.ticksDuringWorkers<2)throw Error('worker isolation or responsiveness failed '+JSON.stringify(counts));
   const controller=new AbortController();onCreate=()=>setTimeout(()=>controller.abort(),0);let aborted=false;
   try{await f.readChunked('worker.bin',saved.sha256,old,{signal:controller.signal})}catch(e){aborted=e.name==='AbortError'}onCreate=null;if(!aborted||counts.active!==0)throw Error('abort did not terminate worker');
   const valid=f.valid;let live=true;f.valid=()=>live;onCreate=()=>setTimeout(()=>{live=false},0);let rejected=false;
   try{await f.readChunked('worker.bin',saved.sha256,old)}catch{rejected=true}finally{f.valid=valid;onCreate=null}
   if(!rejected||counts.active!==0||counts.created!==counts.terminated)throw Error('session disposal did not terminate worker '+JSON.stringify(counts));return counts;
  }finally{clearInterval(timer);window.Worker=Original}
 });assert.equal(result.active,0);console.log('PASS concurrent per-operation workers, UI timers, abort and session disposal',JSON.stringify(result));
}finally{await context.close();await browser.disconnect()}
