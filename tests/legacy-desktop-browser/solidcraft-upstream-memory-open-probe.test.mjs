import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

// Investigates an integration route only. Interception simulates a same-origin
// response; it does not implement or secure a desktop service worker bridge.
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'});
const origin=process.env.SOLIDCRAFT_TEST_ORIGIN||'http://127.0.0.1:19670';
const context=await browser.createBrowserContext();
try{
  const source=await context.newPage();await source.goto(origin+'/?webgl',{waitUntil:'domcontentloaded'});
  await source.waitForFunction('window.solidcraft && typeof window.solidcraft.commands === "function"',{timeout:120000});
  const bytes=await source.evaluate(async()=>{
    const a=window.solidcraft;await a.request('ui.home',{open:false});await a.execute('solid.box',{length:30,width:20,height:10,body_name:'Memory source'});
    await a.execute('file.save_as',{path:'/opfs/memory-source.sc'});
    for(let i=0;i<100;i++){try{const root=await navigator.storage.getDirectory(),file=await(await root.getFileHandle('memory-source.sc')).getFile();return Array.from(new Uint8Array(await file.arrayBuffer()))}catch{await new Promise(r=>setTimeout(r,100))}}
    throw Error('fixture file unavailable');
  });
  const p=await context.newPage(),target=origin+'/codi-memory-fixture.sc',requests=[];
  await p.setBypassServiceWorker(true);
  await p.setRequestInterception(true);
  p.on('request',r=>{if(r.url()===target){requests.push(r.url());void r.respond({status:200,contentType:'application/octet-stream',body:Buffer.from(bytes)})}else void r.continue()});
  await p.goto(origin+'/?webgl&embed&open='+encodeURIComponent('/codi-memory-fixture.sc'),{waitUntil:'domcontentloaded'});
  await p.waitForFunction('window.solidcraft && typeof window.solidcraft.commands === "function"',{timeout:120000});
  try{await p.waitForFunction(async()=>{try{return (await window.solidcraft.inspect({measure:true})).bodies.some(b=>b.volume_mm3===6000)}catch{return false}},{timeout:20000})}catch(e){console.error('Probe diagnostics',JSON.stringify({requests,inspection:await p.evaluate(()=>window.solidcraft.inspect({measure:true}))}));throw e;}
  assert.equal(requests.length,1);
  const volume=await p.evaluate(async()=>(await window.solidcraft.inspect({measure:true})).bodies.map(b=>b.volume_mm3));
  assert.deepEqual(volume,[6000]);
  console.log('PASS embedded SolidCraft loads intercepted same-origin native design and measures 6000 mm³');
}finally{await context.close();await browser.disconnect()}
