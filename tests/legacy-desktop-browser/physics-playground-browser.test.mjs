import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',protocolTimeout:120000});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));

try{
 const phone=process.env.CODI_PHONE==='1';
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_PHYSICS_MANIFEST||'.build/physics-playground/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 const base=process.env.CODI_PHYSICS_URL||'http://127.0.0.1:18342/';
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForSelector('.physics-stage canvas',{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('.physics-info')?.textContent.includes('Paused'));
 const click=async label=>{
  const selector=`.physics-view [aria-label="${label}"]`;
  if(phone){const element=await page.$(selector);assert.ok(element,selector);await element.scrollIntoView();await element.tap()}
  else await page.click(selector);
 };
 await page.click('.physics-settings summary');
 assert.equal(await page.$eval('[aria-label="Sound effects"]',element=>element.checked),false,'sound starts muted');
 await click('Run');
 await page.waitForFunction(()=>/Running/.test(document.querySelector('.physics-info')?.textContent||''));
 await page.waitForFunction(()=>{const text=document.querySelector('.physics-info')?.textContent||'';const tick=Number(text.match(/tick (\d+)/)?.[1]||0);return tick>0});
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await page.waitForFunction(()=>/Paused/.test(document.querySelector('.physics-info')?.textContent||''));
 await click('Run');
 await click('Add object');
 await page.waitForFunction(()=>document.querySelector('.physics-info')?.textContent.includes('6/96'));
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.physics-view .app-status')?.textContent.includes('Checkpoint saved'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Physics Playground.game.json').data)));
 assert.equal(saved.appId,'physics-playground');
 assert.ok(saved.payload.worldSnapshot.length>0);
 assert.equal(saved.payload.records.length,6);
 await page.evaluate(()=>globalThis.confirmAnswer=true);
 await click('Reset');
 await page.waitForFunction(()=>document.querySelector('.physics-info')?.textContent.includes('5/96'));
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.physics-view .app-status')?.textContent.includes('Checkpoint loaded and paused'));
 assert.match(await page.$eval('.physics-info',element=>element.textContent),/6\/96 objects/);
 await page.evaluate(()=>{window.test.store.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});globalThis.target='/bad.game.json'});
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.physics-view .app-status')?.textContent.includes('Could not open checkpoint'));
 assert.match(await page.$eval('.physics-info',element=>element.textContent),/6\/96 objects/,'invalid checkpoint preserves the live bench');
 await page.evaluate(()=>window.test.dispose());
 await page.waitForFunction(()=>!document.querySelector('.physics-view'));
 assert.deepEqual(errors,[]);
 console.log(`PASS ${phone?'phone':'desktop'} Physics Playground render, run, spawn, Rapier save/reset/reopen, invalid recovery and disposal`);
}finally{
 await context.close();
 await browser.disconnect();
}
