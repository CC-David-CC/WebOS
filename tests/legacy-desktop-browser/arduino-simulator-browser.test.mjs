import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm,readFile} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18144/',username=process.env.CODI_TEST_USERNAME||'avrsim'+Date.now().toString().slice(-9);let fresh;
try{
  if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true});
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');
  await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
  await page.evaluate(()=>document.querySelector('[aria-label=Applications]').click());await page.waitForSelector('[aria-label=Electronics]');await page.evaluate(()=>document.querySelector('[aria-label=Electronics]').click());
  await page.waitForSelector('[aria-label="Arduino Simulator"]');await page.evaluate(()=>[...surfaces.values()][0].launch('arduino-simulator'));await page.waitForSelector('.arduino-simulator');
  await page.evaluate(()=>[...document.querySelectorAll('.arduino-toolbar button')].find(b=>b.textContent==='Run Blink example').click());
  await page.waitForFunction(()=>document.querySelector('.arduino-status')?.textContent.startsWith('Running'),{timeout:30000});
  await page.waitForFunction(()=>document.querySelector('.arduino-stage wokwi-led')?.value===true,{timeout:30000});
  await page.waitForFunction(()=>document.querySelector('.arduino-stage wokwi-led')?.value===false,{timeout:30000});
  const fixture=await mkdtemp(path.join(os.tmpdir(),'codi-avr-'));try{await writeFile(path.join(fixture,'test-firmware.hex'),await readFile('apps/system/arduino-simulator/examples/blink.hex'));await page.evaluate(()=>[...surfaces.values()][0].launch('files'));await page.waitForSelector('input[aria-label="Upload files"]');await(await page.$('input[aria-label="Upload files"]')).uploadFile(path.join(fixture,'test-firmware.hex'));await page.waitForFunction(async()=>{try{return !!await(await mirrorFileContext()).files.read('/test-firmware.hex')}catch{return false}},{timeout:30000});await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/bad.hex','not hex',null);await c.files.sync();document.querySelector('.files-content').closest('.window').querySelector('[aria-label=Close]').click();});}finally{await rm(fixture,{recursive:true,force:true});}
  await page.evaluate(()=>[...document.querySelectorAll('.arduino-toolbar button')].find(b=>b.textContent==='Open HEX from My files').click());
  await page.waitForSelector('[aria-label="Choose file test-firmware.hex"]');await page.click('[aria-label="Choose file test-firmware.hex"]');
  await page.waitForFunction(()=>document.querySelector('.arduino-status')?.textContent.includes('test-firmware.hex'),{timeout:30000});
  await page.evaluate(()=>[...document.querySelectorAll('.arduino-toolbar button')].find(b=>b.textContent==='Open HEX from My files').click());await page.waitForSelector('[aria-label="Choose file bad.hex"]');await page.click('[aria-label="Choose file bad.hex"]');await page.waitForFunction(()=>document.querySelector('.arduino-status')?.textContent.startsWith('Could not open firmware'));await page.waitForFunction(()=>document.querySelector('.arduino-stage wokwi-led')?.value===true,{timeout:30000});
  await page.$eval('[aria-label="Firmware save path"]',e=>e.value='/saved.hex');await page.click('[aria-label="Save firmware"]');await page.waitForFunction(()=>document.querySelector('.arduino-status')?.textContent.startsWith('Saved firmware'));const sync=await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();const a=await c.files.read('/saved.hex'),b=await(await serverFileContext()).files.read('saved.hex');return [a.status,a.sha256,b.sha256]});assert.equal(sync[0],'synced');assert.equal(sync[1],sync[2]);
  await page.evaluate(()=>[...surfaces.values()][0].launch('arduino-simulator'));
  await page.waitForFunction(()=>document.querySelectorAll('.arduino-simulator').length===2);
  await page.evaluate(()=>[...document.querySelectorAll('.arduino-simulator')][1].querySelector('[aria-label="Run Blink example"]').click());
  await page.waitForFunction(()=>[...document.querySelectorAll('.arduino-status')][1]?.textContent.startsWith('Running'),{timeout:30000});
  await page.evaluate(()=>document.querySelector('.arduino-simulator').closest('.window').querySelector('[aria-label=Close]').click());
  assert.equal(await page.$$eval('.arduino-simulator',items=>items.length),1);
  await page.waitForFunction(()=>document.querySelector('.arduino-stage wokwi-led')?.value===true,{timeout:30000});
  fresh=await browser.createBrowserContext();const q=await fresh.newPage();await q.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await q.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});await q.goto(base);await q.waitForSelector('.login-toggle');await q.type('[aria-label=Username]',username);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');await q.evaluate(async()=>{await(await mirrorFileContext()).files.sync();openMirrorDocument([...surfaces.values()][0],signedInSubject(),'/saved.hex')});await q.waitForFunction(()=>document.querySelector('.arduino-status')?.textContent.includes('Running saved.hex'),{timeout:30000});await q.waitForFunction(()=>document.querySelector('.arduino-stage wokwi-led')?.value===true,{timeout:30000});await q.waitForFunction(()=>document.querySelector('.arduino-stage wokwi-led')?.value===false,{timeout:30000});
  if(process.env.CODI_TEST_CLEAN_FILES==='1')await page.evaluate(async()=>{const c=await mirrorFileContext();for(const p of ['/test-firmware.hex','/saved.hex','/bad.hex']){const f=await c.files.read(p);await c.files.remove(p,f.version)}await c.files.sync()});
  console.log('PASS Blink simulation, upload, bad HEX recovery, independent windows, save/sync and fresh-session Files open');
}finally{if(fresh)await fresh.close();await context.close();await browser.disconnect();}
