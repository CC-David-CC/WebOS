// Disposable isolated loopback accounts only; checks overlapping signed transfers.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const url=new URL(process.env.CODI_TEST_URL||'http://127.0.0.1:19861/');
assert.ok(['127.0.0.1','localhost'].includes(url.hostname));
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),contexts=[];
const suffix=Date.now().toString().slice(-8);
async function createAccount(name){
 const context=await browser.createBrowserContext();contexts.push(context);const page=await context.newPage();
 await page.evaluateOnNewDocument(()=>{
  const original=window.fetch;window.uploads=[];window.abortNext=false;
  window.fetch=async(input,options={})=>{
   const path=String(input);if(path.endsWith('assets/terminal/v2/image.json'))return new Response('',{status:404});
   if(!path.endsWith('/gateway/upload'))return original(input,options);
   const metadata=JSON.parse(await options.body.slice(4,4+new DataView(await options.body.slice(0,4).arrayBuffer()).getUint32(0)).text());
   const record={operation:metadata.operation,start:Date.now(),end:null};window.uploads.push(record);
   let timer,opts=options;
   if(window.abortNext){window.abortNext=false;const controller=new AbortController();timer=setTimeout(()=>controller.abort(),40);opts={...options,signal:AbortSignal.any([options.signal,controller.signal])};}
   try{return await original(input,opts)}finally{clearTimeout(timer);record.end=Date.now();}
  };
 });
 await page.goto(url.href);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 for(const [selector,value] of [['[aria-label=Username]',name],['[aria-label=Password]','test1234'],['[aria-label="Confirm password"]','test1234']])await page.type(selector,value);
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});return page;
}
try{
 const pages=[await createAccount('parallela'+suffix),await createAccount('parallelb'+suffix)];
 await Promise.all(pages.map(page=>page.evaluate(()=>{window.bytes=new Uint8Array(8*1024*1024);for(let i=0;i<bytes.length;i+=65536)crypto.getRandomValues(bytes.subarray(i,i+65536));})));
 const created=await Promise.all(pages.map(page=>page.evaluate(async()=>{const f=(await serverFileContext()).files;return f.write('parallel.bin',window.bytes,null)})));
 const windows=await Promise.all(pages.map(page=>page.evaluate(()=>window.uploads.at(-1))));
 assert.ok(windows.every(x=>x.operation==='create'&&x.end>x.start),JSON.stringify(windows));
 assert.ok(Math.max(...windows.map(x=>x.start))<Math.min(...windows.map(x=>x.end)),'Signed full uploads did not overlap: '+JSON.stringify(windows));
 const edited=await Promise.all(pages.map((page,i)=>page.evaluate(async prior=>{window.bytes[1234]^=1;return (await serverFileContext()).files.write('parallel.bin',window.bytes,prior)},created.map(x=>x.sha256)[i])));
 const deltas=await Promise.all(pages.map(page=>page.evaluate(()=>window.uploads.at(-1))));
 assert.ok(deltas.every(x=>x.operation==='replace-delta'),JSON.stringify(deltas));
 // Force a full, slower upload by replacing all content, then abort the request
 // after it begins. A version read must see the last confirmed version.
 const interruption=await pages[0].evaluate(async previous=>{const f=(await serverFileContext()).files;const replacement=new Uint8Array(8*1024*1024);for(let i=0;i<replacement.length;i+=65536)crypto.getRandomValues(replacement.subarray(i,i+65536));const replacementHash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',replacement))].map(x=>x.toString(16).padStart(2,'0')).join('');window.abortNext=true;let failed=false;try{await f.write('parallel.bin',replacement,previous)}catch{failed=true}await new Promise(resolve=>setTimeout(resolve,3000));const after=await f.version('parallel.bin');if(after.sha256===previous)await f.write('parallel.bin',replacement,previous);return {failed,after,replacementHash,upload:window.uploads.find(x=>x.operation==='replace')}},edited[0].sha256);
 assert.ok(interruption.failed&&[edited[0].sha256,interruption.replacementHash].includes(interruption.after.sha256),JSON.stringify(interruption));
 assert.equal(interruption.upload.operation,'replace');
 const versions=await Promise.all(pages.map(page=>page.evaluate(async()=>await(await serverFileContext()).files.version('parallel.bin'))));
 assert.deepEqual(versions.map(x=>x.sha256),[interruption.replacementHash,edited[1].sha256]);
 console.log('PASS concurrent signed account uploads, simultaneous delta saves, in-flight abort and exact reconciliation',JSON.stringify({windows,deltas,interruption}));
}finally{for(const context of contexts)await context.close();await browser.disconnect();}
