import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19661/';
try{
  await page.goto(base);
  await page.waitForSelector('.login-toggle');
  await page.click('.login-toggle');
  await page.type('[aria-label=Username]','occt'+Date.now().toString().slice(-9));
  await page.type('[aria-label=Password]','test1234');
  await page.type('[aria-label="Confirm password"]','test1234');
  await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  assert.equal(await page.evaluate(()=>performance.getEntriesByType('resource').some(e=>e.name.includes('/apps/opencascade/'))),false,'kernel is not loaded during startup');
  await page.click('[aria-label=Applications]');
  await page.click('[aria-label="System Tools"]');
  await page.waitForSelector('[aria-label="OpenCascade.js"]');
  assert.equal(await page.$eval('[aria-label="OpenCascade.js"]',e=>e.disabled),true);
  const result=await page.evaluate(async()=>{
    const {workerModuleURL}=await publicAppHost(surfaces.get('Desktop'),{},'text').tools.loadOpenCascade();
    const code=`import {createOpenCascade} from ${JSON.stringify(workerModuleURL)}; try {const oc=await createOpenCascade(); const box=new oc.BRepPrimAPI_MakeBox_1(10,20,30); const shape=box.Shape(); const props=new oc.GProp_GProps_1(); try {oc.BRepGProp.VolumeProperties_1(shape,props,false,false,false); postMessage({nullShape:shape.IsNull(),volume:props.Mass()})} finally {props.delete(); shape.delete(); box.delete()}}catch(e){postMessage({error:String(e?.stack||e)})}`;
    const url=URL.createObjectURL(new Blob([code],{type:'text/javascript'}));
    const worker=new Worker(url,{type:'module'});
    try{return await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('kernel timed out')),90000);worker.onmessage=e=>{clearTimeout(timeout);resolve(e.data)};worker.onerror=e=>{clearTimeout(timeout);reject(Error(e.message))}})}finally{worker.terminate();URL.revokeObjectURL(url)}
  });
  assert.deepEqual(result,{nullShape:false,volume:6000});
  console.log('PASS: disabled lazy system tool, worker kernel, solid and volume');
}finally{await context.close();await browser.disconnect()}
