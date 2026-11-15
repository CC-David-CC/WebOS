import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19465',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
try{
 const phone=process.env.CODI_PHONE==='1';await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>{if(/^https?:/.test(request.url())&&!request.url().startsWith(process.env.CODI_GRAVITY_BASE||'http://127.0.0.1:18465/'))external.push(request.url())});
 const manifest=JSON.parse(await readFile(process.env.CODI_GRAVITY_MANIFEST||'.build/gravity-pinball/apps.json','utf8'));
 const record=manifest.apps.find(app=>app.id==='gravity-pinball');assert.ok(record);
 const entry='/'+record.path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_GRAVITY_BASE||'http://127.0.0.1:18465/')+'gravity-pinball-fixture.html?app='+encodeURIComponent(entry));
 await page.waitForSelector('.pinball-stage canvas',{timeout:60000});await page.waitForFunction(()=>document.querySelector('.pinball-marquee')?.textContent.includes('Balls 3'));
 const click=async label=>{const element=await page.$(`[aria-label="${label}"]`);assert.ok(element,label);if(phone){await element.scrollIntoView();await element.tap()}else await element.click()};
 await click('Start');await page.waitForFunction(()=>document.querySelector('[aria-label="Start"]')?.textContent==='Pause');
 const launch=await page.$('[aria-label="Hold to launch"]'),box=await launch.boundingBox();await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();await new Promise(resolve=>setTimeout(resolve,250));await page.mouse.up();await new Promise(resolve=>setTimeout(resolve,250));
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));await page.waitForFunction(()=>document.querySelector('[aria-label="Start"]')?.textContent==='Start / Resume');
 await click('Save to My files');await page.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('Checkpoint saved'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Gravity Pinball.game.json').data)));
 assert.equal(saved.appId,'gravity-pinball');assert.equal(saved.payload.paused,true);assert.ok(saved.payload.worldSnapshot.length>0);
 await page.evaluate(()=>{window.test.store.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});globalThis.target='/bad.game.json'});
 await click('Open from My files');await page.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('Could not open checkpoint'));
 await page.evaluate(()=>window.test.dispose());await page.waitForFunction(()=>!document.querySelector('.pinball-view'));
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log(`PASS ${phone?'phone':'desktop'} Gravity Pinball launch, focus pause, checkpoint save, invalid recovery and disposal`);
}finally{await context.close();await browser.disconnect()}
