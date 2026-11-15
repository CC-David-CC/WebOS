import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19345'});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
const clickFirst=label=>page.evaluate(label=>{
 const root=document.querySelectorAll('.sky-courier')[0];
 const button=[...root.querySelectorAll('button')].find(node=>node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 const manifest=JSON.parse(await readFile(process.env.CODI_SKY_MANIFEST||'.build/sky-courier-test/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_SKY_URL||'http://127.0.0.1:18345/')+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForSelector('.sky-stage canvas');
 await clickFirst('Resume');
 await page.waitForFunction(()=>document.querySelector('.sky-summary')?.textContent.includes('route 0%')===false);
 await page.evaluate(()=>{
  const files=window.fileContext.files,write=files.write.bind(files);
  window.releaseSkyWrite=null;
  files.write=async(...args)=>{
   window.skyWriteStarted=true;
   await new Promise(resolve=>{window.releaseSkyWrite=resolve});
   const result=await write(...args);
   files.write=write;
   return result;
  };
  document.querySelector('.sky-save').open=true;
  document.querySelector('[aria-label="Sky Courier save path"]').value='/Pending.game.json';
 });
 await clickFirst('Save checkpoint');
 await page.waitForFunction(()=>window.skyWriteStarted===true);
 assert.equal(await page.evaluate(()=>window.instances[0].w.skyCourier.dirty),true,'pending save blocks close');
 assert.equal(await page.$eval('.sky-toolbar button[aria-label="Save checkpoint"]',button=>button.disabled),true,'save controls lock');
 await page.evaluate(()=>window.releaseSkyWrite());
 await page.waitForFunction(()=>document.querySelector('.sky-status')?.textContent.includes('Checkpoint saved'));
 assert.equal(await page.evaluate(()=>window.instances[0].w.skyCourier.dirty),false);
 await page.evaluate(()=>{
  const first=window.instances[0];
  first.controller.abort();
  first.app.dispose();
  first.app.element.remove();
 });
 assert.equal(await page.$$('.sky-courier').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 console.log('PASS Sky Courier pending-save guard, locked controls, completion and cleanup');
}finally{
 await context.close();
 await browser.disconnect();
}
