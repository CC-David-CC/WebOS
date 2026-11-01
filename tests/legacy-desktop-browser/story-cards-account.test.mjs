import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18312/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'story'+Date.now().toString().slice(-9),contexts=[],errors=[];
async function login(page,register,user=username){
 page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('story-cards'));await page.waitForSelector('.story-app canvas',{timeout:30000})}
const click=(page,label)=>page.evaluate(label=>{const button=[...document.querySelectorAll('.story-app button')].find(node=>node.textContent===label);if(!button)throw Error('Missing button: '+label);button.click()},label);
try{
 const first=await browser.createBrowserContext();contexts.push(first);const page=await first.newPage();await page.setViewport({width:1366,height:900});await login(page,true);await launch(page);
 await click(page,'Resume');await page.waitForFunction(()=>[...document.querySelectorAll('.story-choices button')].length===2);await click(page,'Ask the owl for help');await click(page,'Climb at dusk');await click(page,'Return to the workshop');
 await page.waitForFunction(()=>document.querySelector('.story-prompt')?.textContent.includes('Ending reached'));
 await page.evaluate(()=>{document.querySelector('.story-save').open=true;document.querySelector('[aria-label="Story save path"]').value='/Story Cards.game.json'});
 await click(page,'Save to My files');await page.waitForFunction(()=>document.querySelector('.story-app .app-status')?.textContent.includes('syncing'));
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Story Cards.game.json')).data)));
 assert.equal(saved.appId,'story-cards');assert.equal(saved.payload.nodeId,'ending-light');assert.deepEqual(saved.payload.endings,['light']);
 await page.evaluate(()=>document.querySelector('.story-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.story-app'));
 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Story Cards.game.json'));
 await page.waitForFunction(()=>document.querySelector('.story-app .app-status')?.textContent.includes('Story loaded and paused'),{timeout:30000});
 assert.equal(await page.$eval('[aria-label="Story save path"]',node=>node.value),'/Story Cards.game.json');
 await page.evaluate(()=>document.querySelector('.story-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.story-app'));
 const fresh=await browser.createBrowserContext();contexts.push(fresh);const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.story-save').open=true);await click(phone,'Open from My files');await phone.waitForSelector('[aria-label="Choose file Story Cards.game.json"]',{visible:true});await phone.click('[aria-label="Choose file Story Cards.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.story-app .app-status')?.textContent.includes('Story loaded and paused'),{timeout:30000});assert.match(await phone.$eval('.story-prompt',node=>node.textContent),/Ending reached/);
 const isolation=await browser.createBrowserContext();contexts.push(isolation);const other=await isolation.newPage();await login(other,true,username+'b');assert.equal(await other.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Story Cards.game.json');return true}catch{return false}}),false);
 await phone.evaluate(async()=>{const context=await mirrorFileContext(),file=await context.files.read('/Story Cards.game.json');await context.files.remove('/Story Cards.game.json',file.version);await context.files.sync()});
 await phone.waitForFunction(()=>!document.querySelector('.story-warning').hidden&&document.querySelector('.story-warning').textContent.includes('unavailable'));
 await click(phone,'Save to My files');await phone.waitForFunction(()=>document.querySelector('.story-app .app-status')?.textContent.includes('saved story was removed'));
 assert.equal(await phone.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Story Cards.game.json');return true}catch{return false}}),false,'deleted story is not silently recreated');
 await phone.$eval('[aria-label="Story save path"]',node=>node.value='/Story Cards copy.game.json');await click(phone,'Save to My files');await phone.waitForFunction(()=>document.querySelector('.story-app .app-status')?.textContent.includes('syncing'));
 await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());const copy=await phone.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Story Cards copy.game.json')).data)));assert.equal(copy.payload.nodeId,'ending-light');
 await click(phone,'Restart');await click(phone,'Resume');await phone.waitForFunction(()=>[...document.querySelectorAll('.story-choices button')].length===2);await click(phone,'Ask the owl for help');assert.match(await phone.$eval('.story-transcript',e=>e.textContent),/choice/);
 await phone.evaluate(()=>document.querySelector('.story-app').closest('.window').querySelector('[aria-label=Close]').click());await phone.waitForSelector('dialog.codi-confirm-dialog[open]');await phone.click('.codi-confirm-danger');await phone.waitForFunction(()=>!document.querySelector('.story-app'));assert.deepEqual(errors,[]);console.log('PASS real account story save, sync, Files route, phone reload, paused restore and isolation');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
