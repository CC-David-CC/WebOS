import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19275',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
page.on('request',request=>{const url=new URL(request.url());if(/^https?:/.test(url.protocol)&&url.origin!=='http://127.0.0.1:18375')external.push(url.href)})
try{
 const phone=process.env.CODI_PHONE==='1';
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_SLING_MANIFEST||'.build/sling-targets/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 const base=process.env.CODI_SLING_URL||'http://127.0.0.1:18375/';
 await page.goto(base+'sling-targets-fixture.html?app='+encodeURIComponent(entry));
 await page.waitForSelector('.sling-stage canvas',{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Paused'));
 await page.click('.sling-settings summary');
 assert.equal(await page.$eval('[aria-label="Sound effects"]',node=>node.checked),false,'sound starts muted');
 await page.click('.sling-app [aria-label="Aim right"]');
 await page.click('.sling-app [aria-label="Cancel aim"]');
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Aim cancelled'));
 assert.match(await page.$eval('.sling-card:last-child',node=>node.textContent),/3 shots/);
 await page.click('.sling-app [aria-label="Launch shot"]');
 await page.waitForFunction(()=>document.querySelector('.sling-card:last-child')?.textContent.includes('2 shots'));
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await page.waitForFunction(()=>document.querySelector('.sling-card:last-child')?.textContent.includes('Paused'));
 await page.click('.sling-save summary');
 await page.click('.sling-app [aria-label="Save to My files"]');
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Saved on this device'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Sling-targets.game.json').data)));
 assert.equal(saved.appId,'sling-targets');
 assert.equal(saved.payload.remainingShots,2);
 await page.click('.sling-app [aria-label="Restart level"]');
 await page.waitForFunction(()=>document.querySelector('.sling-card:last-child')?.textContent.includes('3 shots'));
 await page.click('.sling-app [aria-label="Open from My files"]');
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('loaded and paused'));
 await page.waitForFunction(()=>document.querySelector('.sling-card:last-child')?.textContent.includes('2 shots'));
 await page.evaluate(()=>{window.test.store.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});globalThis.target='/bad.game.json'});
 await page.click('.sling-app [aria-label="Open from My files"]');
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Could not open target round'));
 assert.match(await page.$eval('.sling-card:last-child',node=>node.textContent),/2 shots/,'invalid file preserves the current round');
 assert.equal(await page.evaluate(()=>document.querySelector('.sling-stage').scrollWidth>document.querySelector('.sling-stage').clientWidth),false);
 await page.evaluate(()=>window.test.dispose());
 await page.waitForFunction(()=>!document.querySelector('.sling-view'));
 assert.deepEqual(errors,[]);
 assert.deepEqual(external,[]);
 console.log(`PASS ${phone?'phone':'desktop'} Sling Targets Rapier launch, cancel, save/open, invalid recovery, focus pause, cleanup and no external requests`);
}finally{
 await context.close();
 await browser.disconnect();
}
