// Negative control for the currently pinned bootstrap and restrictive signed
// fixture CSP. Once the bootstrap is repaired, invert this expected outcome.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL),cdp=new URL(process.env.CODI_TEST_CDP),asset=process.env.CODI_CAD_STATIC;
if(!asset||![base,cdp].every(u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Loopback fixture and CAD asset path required');
const browser=await puppeteer.connect({browserURL:cdp.href}),context=await browser.createBrowserContext();
try{
 const page=await context.newPage();await page.goto(base.href);
 const result=await page.evaluate(async d=>{
  const worker=new Worker(d+'oci-verified-worker.js');
  return await new Promise(resolve=>{const finish=value=>{clearTimeout(timer);worker.terminate();resolve(value)},timer=setTimeout(()=>finish({timeout:true}),45000);
   worker.onerror=e=>finish({event:e.message});worker.onmessage=e=>finish(e.data);
   worker.postMessage({kind:'init',manifest:{version:1,js:{path:d+'occ-portable.js',sha256:'4a53dec0dceb5715d070fa7293f6515ab681f6d3de979099526e616dbd052ddc'},wasm:{path:d+'a2b2f7daf6a4eb98b975.wasm',sha256:'a2b2f7daf6a4eb98b975f8aec136f6cbaf2720295ea32e71edb13ff4c5ceaecb'}}});
  });
 },asset);
 assert.equal(result.kind,'error');assert.match(result.error,/importScripts.*blob:/);console.log('PASS retained negative: restrictive signed CSP rejects blob importScripts');
}finally{await context.close();browser.disconnect()}
