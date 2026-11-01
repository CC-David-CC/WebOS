import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18464/',username=process.env.CODI_TEST_USER||'pinball'+Date.now().toString().slice(-9);
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19465',protocolTimeout:120000}),contexts=[],errors=[];
async function login(page,register){
 page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('gravity-pinball'));await page.waitForSelector('.pinball-stage canvas',{timeout:30000});await page.waitForFunction(()=>document.querySelector('.pinball-marquee')?.textContent.includes('Balls 3'))}
try{
 const first=await browser.createBrowserContext();contexts.push(first);const page=await first.newPage();await page.setViewport({width:1366,height:900});await login(page,true);await launch(page);
 await page.click('[aria-label=Start]');await page.click('[aria-label="Save to My files"]');await page.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('syncing with the server'),{timeout:30000});await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Gravity Pinball.game.json')).data)));assert.equal(saved.appId,'gravity-pinball');
 await page.evaluate(()=>document.querySelector('.gravity-pinball-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.gravity-pinball-app'));
 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Gravity Pinball.game.json'));await page.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('Checkpoint loaded and paused'),{timeout:30000});
 const fresh=await browser.createBrowserContext();contexts.push(fresh);const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);await phone.evaluate(()=>document.querySelector('[aria-label="Open from My files"]').click());await phone.waitForSelector('[aria-label="Choose file Gravity Pinball.game.json"]');await phone.click('[aria-label="Choose file Gravity Pinball.game.json"]');await phone.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('Checkpoint loaded and paused'),{timeout:30000});
 assert.deepEqual(errors,[]);console.log('PASS account save, sync, Files route, close and phone-sized paused reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
