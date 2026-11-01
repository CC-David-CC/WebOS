import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262'});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
const click=label=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.marble-view button')]
  .find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);
try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_MARBLE_MANIFEST||'.build/marble-works/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_MARBLE_URL||'http://127.0.0.1:18346/')+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.marble-board').length===2,{timeout:30000});
 assert.match(await page.$eval('.marble-coach',node=>node.textContent),/Rive.*pending/i);
 await click('Straight 4');
 await click('Place ghost');
 await click('Run');
 await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('Marble released'));
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('window lost attention'));
 await page.evaluate(()=>{document.querySelector('.marble-save').open=true;document.querySelector('[aria-label="Marble save path"]').value='/Marble Works.game.json'});
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('syncing with the server'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Marble Works.game.json').data)));
 assert.equal(saved.appId,'marble-works');
 assert.equal(saved.payload.pieces.length,1);
 assert.equal(saved.payload.paused,true);
 await page.evaluate(()=>{window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});window.target='/Bad.game.json'});
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('Could not open track'));
 assert.equal(await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Marble Works.game.json').data)).payload.pieces.length),1);
 await page.evaluate(()=>{const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove()});
 assert.equal(await page.$$('.marble-board').then(nodes=>nodes.length),1);
 const direct=await page.evaluate(()=>{const item=window.makeMarble('/Marble Works.game.json');window.direct=item;return true});
 assert.equal(direct,true);
 await page.waitForFunction(()=>window.direct?.app.element.querySelector('.app-status')?.textContent.includes('Track loaded and paused'),{timeout:30000});
 assert.deepEqual(errors,[]);
 console.log(`PASS ${process.env.CODI_PHONE?'phone':'desktop'} Marble Works build, run, save, invalid recovery, direct launch and disposal`);
}catch(error){
 console.error(await page.evaluate(()=>({
  direct:window.direct?.app.element.querySelector('.app-status')?.textContent,
  statuses:[...document.querySelectorAll('.app-status')].map(node=>node.textContent),
  body:document.body.innerText.slice(0,1000),
 })).catch(()=>null));
 throw error;
}finally{
 await context.close();
 await browser.disconnect();
}
