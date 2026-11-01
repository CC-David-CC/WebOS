import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
const click=label=>page.evaluate(label=>{const button=[...document.querySelectorAll('.pocket-rally-view button')].find(node=>node.getAttribute('aria-label')===label||node.textContent===label);if(!button)throw Error('Missing '+label);button.click()},label);
try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_RALLY_MANIFEST||'.build/pocket-rally-test/apps.json','utf8')),entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_RALLY_URL||'http://127.0.0.1:18351/')+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);await page.waitForFunction(()=>document.querySelectorAll('.rally-stage canvas').length===2,{timeout:30000});
 assert.match(await page.$eval('.rally-hud',node=>node.textContent),/Lap 1\/3/);
 await click('Resume');await page.waitForFunction(()=>document.querySelector('.rally-hud')?.textContent.includes('Speed'));
 await page.focus('.rally-stage');await page.keyboard.down('ArrowUp');await new Promise(resolve=>setTimeout(resolve,700));await page.keyboard.up('ArrowUp');
 const hud=await page.$eval('.rally-hud',node=>node.textContent);assert.match(hud,/Speed [1-9]/);
 await page.evaluate(()=>window.instances[0].win.classList.remove('focused'));await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('lost attention'));
 await page.evaluate(()=>window.instances[0].win.classList.add('focused'));await click('Resume');
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('lost attention'));
 await page.evaluate(()=>document.querySelector('.rally-save')?.setAttribute('open',''));await page.$eval('[aria-label="Rally save path"]',input=>input.value='/Rally Test.game.json');await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('saved to My files'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Rally Test.game.json').data)));assert.equal(saved.appId,'pocket-rally');assert.equal(saved.payload.trackId,0);
 await page.evaluate(()=>window.delayWriteOnce=true);await click('Save to My files');await page.waitForFunction(()=>window.writeStarted);assert.equal(await page.evaluate(()=>window.instances[0].w.pocketRally.dirty),true,'pending save protects close');await page.evaluate(()=>window.releaseWrite());await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('syncing with the server'));
 await page.evaluate(()=>window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{"bad":true}'),version:'bad',status:'synced'}));await page.evaluate(()=>window.targetPath='/Bad.game.json');await click('Open from My files');await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('Could not open rally'));
 await page.evaluate(()=>{const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove()});assert.equal(await page.$$('.rally-stage canvas').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);console.log(`PASS ${process.env.CODI_PHONE?'phone':'desktop'} Pocket Rally race controls, pause, save, invalid recovery and disposal`);
}finally{await context.close();await browser.disconnect()}
