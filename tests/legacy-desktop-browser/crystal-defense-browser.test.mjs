import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262'});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
const click=label=>page.evaluate(label=>{
 const root=document.querySelectorAll('.crystal-view')[0];
 const button=[...root.querySelectorAll('button')].find(node=>node.textContent===label||node.getAttribute('aria-label')===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_CRYSTAL_MANIFEST||'.build/crystal-defense/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_CRYSTAL_URL||'http://127.0.0.1:18348/')+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.crystal-stage canvas').length===2,{timeout:60000});
 assert.match(await page.$eval('.crystal-rive-pending',node=>node.textContent),/pending/i);
 await click('Socket 2');
 await click('Build Bloom');
 await click('Resume');
 await page.waitForFunction(()=>document.querySelector('.crystal-status')?.textContent.includes('Wave 1 started'),{timeout:30000});
 await page.waitForFunction(()=>document.querySelector('.crystal-view .crystal-note')?.textContent.includes('Wave 1/8'));
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await page.waitForFunction(()=>document.querySelector('.crystal-view button[aria-label="Resume"]'));
 await click('Resume');
 await page.evaluate(()=>document.querySelector('.crystal-save').open=true);
 await page.$eval('[aria-label="Crystal Defense save path"]',input=>input.value='/Crystal Defense.game.json');
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('syncing with the server'));
 const saved=JSON.parse(await page.evaluate(()=>new TextDecoder().decode(window.fileStore.get('/Crystal Defense.game.json').data)));
 assert.equal(saved.appId,'crystal-defense');
 assert.ok(saved.payload.towers.length===1);
 await click('Restart');
 await page.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('New defense ready'));
 await page.evaluate(()=>window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'}));
 await page.evaluate(()=>window.targetPath='/Bad.game.json');
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('Could not open defense'));
 await page.evaluate(()=>{const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove()});
 assert.equal(await page.$$('.crystal-view').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 console.log(`PASS ${process.env.CODI_PHONE?'phone':'desktop'} Crystal Defense Babylon build, wave, pause, save/reopen recovery and disposal`);
}finally{
 await context.close();
 await browser.disconnect();
}
