import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262'});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
const base=process.env.CODI_SOLITAIRE_URL||'http://127.0.0.1:18341/';
page.on('request',request=>{if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==new URL(base).origin)external.push(request.url())});

try{
 const phone=process.env.CODI_PHONE==='1';
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_SOLITAIRE_MANIFEST||'.build/solitaire-test/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.solitaire-board').length===2,{timeout:30000});
 assert.match(await page.$$eval('.solitaire-rive-pending',nodes=>nodes[0].textContent),/final Rive artwork pending/);
 const click=async label=>{
  const element=await page.$(`.solitaire-view [aria-label="${label}"]`);
  assert.ok(element,label);await element.evaluate(target=>target.click());
 };
 await click('Start game');
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Playing'));
 await page.evaluate(()=>document.querySelector('.window')?.classList.remove('focused'));
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Paused'));
 await page.evaluate(()=>document.querySelector('.window')?.classList.add('focused'));
 await click('Start game');
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Playing'));
 await click('Draw');
 await click('Undo');
 await click('Hint');
 await page.evaluate(()=>document.querySelector('.solitaire-save').open=true);
 await page.$eval('[aria-label="Solitaire save path"]',input=>input.value='/Solitaire.game.json');
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('syncing with the server'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Solitaire.game.json').data)));
 assert.equal(saved.appId,'solitaire');
 assert.equal(saved.payload.stock.length+saved.payload.waste.length+saved.payload.tableau.flatMap(pile=>pile.cards).length+saved.payload.foundations.flat().length,52);
 await page.$eval('[aria-label="Solitaire save path"]',input=>input.value='/Delayed.game.json');
 await page.evaluate(()=>{window.delayWrite=true});await click('Save to My files');
 await page.waitForFunction(()=>window.writeWaiting===true);
 assert.equal(await page.$$eval('.solitaire-view [aria-label="Save to My files"]',buttons=>buttons[0].disabled),true,'save controls lock at the captured boundary');
 await page.evaluate(()=>{window.delayWrite=false;window.releaseWrite()});
 await page.waitForFunction(()=>window.fileStore.has('/Delayed.game.json'));
 await page.evaluate(()=>{window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{"format":"wrong"}'),version:'bad',status:'synced'});window.targetPath='/Bad.game.json'});
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Could not open game'));
 await page.evaluate(()=>{const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove()});
 assert.equal(await page.$$('.solitaire-board').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log(`PASS ${phone?'phone':'desktop'} Solitaire draw/undo/hint/save/invalid-open and independent disposal`);
}finally{
 await context.close();await browser.disconnect();
}
