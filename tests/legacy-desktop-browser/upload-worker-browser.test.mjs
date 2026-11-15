import assert from 'node:assert/strict';import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL||'http://127.0.0.1:19879/');assert.ok(['127.0.0.1','localhost'].includes(base.hostname));const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),context=await browser.createBrowserContext();
try{
 const p=await context.newPage();await p.goto(base.href);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]','upload'+Date.now().toString().slice(-8));await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 const result=await p.evaluate(async()=>{
  const f=(await serverFileContext()).files,bytes=new Uint8Array(3*1024*1024);for(let i=0;i<bytes.length;i+=65536)crypto.getRandomValues(bytes.subarray(i,i+65536));const a=await f.write('up-a.bin',bytes,null),b=await f.write('up-b.bin',bytes,null);
  const Native=window.Worker,stats={created:0,terminated:0,active:0,maxActive:0,ticksDuringWorkers:0};let onCreate=null;
  window.Worker=class extends Native{constructor(...args){super(...args);this.done=false;stats.created++;stats.active++;stats.maxActive=Math.max(stats.maxActive,stats.active);onCreate?.()}terminate(){if(!this.done){this.done=true;stats.terminated++;stats.active--}return super.terminate()}};
  const timer=setInterval(()=>{if(stats.active)stats.ticksDuringWorkers++},10);
  try{
   const changed=bytes.slice();changed[987654]^=1;const controller=new AbortController();onCreate=()=>setTimeout(()=>controller.abort(),0);let aborted=false;
   try{await f.write('up-a.bin',changed,a.sha256,{signal:controller.signal})}catch(e){aborted=e.name==='AbortError'}onCreate=null;
   if(!aborted||(await f.version('up-a.bin')).sha256!==a.sha256||stats.active!==0)throw Error('cancelled upload changed the file');
   const old=f.valid;let live=true;f.valid=()=>live;onCreate=()=>setTimeout(()=>{live=false},0);let rejected=false;
   try{await f.write('up-a.bin',changed,a.sha256)}catch{rejected=true}finally{f.valid=old;onCreate=null}
   if(!rejected||(await f.version('up-a.bin')).sha256!==a.sha256||stats.active!==0)throw Error('stale session upload changed the file');
   const both=await Promise.all([f.write('up-a.bin',changed,a.sha256),f.write('up-b.bin',changed,b.sha256)]);
   if(both.some(x=>x.sha256!==both[0].sha256)||stats.active!==0||stats.created!==stats.terminated||stats.maxActive<2||stats.ticksDuringWorkers<2)throw Error('concurrent upload worker failure '+JSON.stringify(stats));return stats;
  }finally{clearInterval(timer);window.Worker=Native}
 });assert.equal(result.active,0);console.log('PASS concurrent upload workers, UI timers, abort and stale account',JSON.stringify(result));
}finally{await context.close();await browser.disconnect()}
