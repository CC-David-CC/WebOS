import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18376/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19276',protocolTimeout:120000});
const user=process.env.CODI_TEST_USER||'sling'+Date.now().toString().slice(-9);
const contexts=[],errors=[];
async function login(page,register,name=user){
 page.on('pageerror',error=>errors.push(error.message));
 page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);
 await page.waitForSelector('.login-toggle');
 if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',name);
 await page.type('[aria-label=Password]','test1234');
 if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){
 await page.evaluate(()=>surfaces.get('Desktop').launch('sling-targets'));
 await page.waitForSelector('.sling-stage canvas',{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Paused'));
}
try{
 const first=await browser.createBrowserContext();contexts.push(first);
 const page=await first.newPage();await page.setViewport({width:1366,height:900});
 await login(page,true);await launch(page);
 await page.click('.sling-app [aria-label="Launch shot"]');
 await page.waitForFunction(()=>document.querySelector('.sling-card:last-child')?.textContent.includes('2 shots'));
 await page.click('.sling-save summary');
 await page.click('.sling-app [aria-label="Save to My files"]');
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Saved on this device'),{timeout:30000});
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Sling-targets.game.json')).data)));
 assert.equal(saved.appId,'sling-targets');
 assert.equal(saved.payload.remainingShots,2);
 await page.evaluate(()=>document.querySelector('.sling-app').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.sling-app'));
 await launch(page);
 await page.click('.sling-save summary');
 await page.click('.sling-app [aria-label="Open from My files"]');
 await page.waitForSelector('[aria-label="Choose file Sling-targets.game.json"]',{visible:true});
 await page.click('[aria-label="Choose file Sling-targets.game.json"]');
 await page.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('loaded and paused'),{timeout:30000});

 const fresh=await browser.createBrowserContext();contexts.push(fresh);
 const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.click('.sling-save summary');
 await phone.click('.sling-app [aria-label="Open from My files"]');
 await phone.waitForSelector('[aria-label="Choose file Sling-targets.game.json"]',{visible:true});
 await phone.click('[aria-label="Choose file Sling-targets.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('loaded and paused'),{timeout:30000});
 assert.match(await phone.$eval('.sling-card:last-child',node=>node.textContent),/2 shots/);

 const isolation=await browser.createBrowserContext();contexts.push(isolation);
 const other=await isolation.newPage();await login(other,true,user+'b');
 assert.equal(await other.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Sling-targets.game.json');return true}catch{return false}}),false);
 assert.deepEqual(errors,[]);
 console.log('PASS real account save, server sync, Files reopen, phone restore and account isolation');
}finally{
 for(const context of contexts)await context.close();
 await browser.disconnect();
}
