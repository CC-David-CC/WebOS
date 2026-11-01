import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18347/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'drone'+Date.now().toString().slice(-9),contexts=[],errors=[];
async function login(page,register,user=username){
 page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('drone-circuit'));await page.waitForSelector('.drone-stage-wrap canvas',{timeout:30000})}
const click=(page,label)=>page.evaluate(label=>{const button=[...document.querySelectorAll('.drone-view button')].find(node=>node.textContent===label);if(!button)throw Error('Missing button: '+label);button.click()},label);
try{
 const first=await browser.createBrowserContext();contexts.push(first);const page=await first.newPage();await page.setViewport({width:1366,height:900});await login(page,true);await launch(page);
 await click(page,'Run');await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('Flight active'));await new Promise(resolve=>setTimeout(resolve,500));
 await page.evaluate(()=>{document.querySelector('.drone-save').open=true;document.querySelector('[aria-label="Drone save path"]').value='/Drone Circuit.game.json'});
 await click(page,'Save to My files');await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('syncing with the server'),{timeout:30000});
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Drone Circuit.game.json')).data)));
 assert.equal(saved.appId,'drone-circuit');
 await page.evaluate(()=>document.querySelector('.drone-view').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.drone-view'));
 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Drone Circuit.game.json'));
 await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('Flight loaded and paused'),{timeout:30000});
 assert.equal(await page.$eval('[aria-label="Drone save path"]',node=>node.value),'/Drone Circuit.game.json');
 await page.evaluate(()=>document.querySelector('.drone-view').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.drone-view'));
 const fresh=await browser.createBrowserContext();contexts.push(fresh);const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.drone-save').open=true);await click(phone,'Open from My files');await phone.waitForSelector('[aria-label="Choose file Drone Circuit.game.json"]',{visible:true});await phone.click('[aria-label="Choose file Drone Circuit.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('Flight loaded and paused'),{timeout:30000});
 const isolation=await browser.createBrowserContext();contexts.push(isolation);const other=await isolation.newPage();await login(other,true,username+'b');
 assert.equal(await other.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Drone Circuit.game.json');return true}catch{return false}}),false);
 await phone.evaluate(async()=>{const context=await mirrorFileContext(),file=await context.files.read('/Drone Circuit.game.json');await context.files.remove('/Drone Circuit.game.json',file.version);await context.files.sync()});
 assert.deepEqual(errors,[]);console.log('PASS real account flight save, sync, Files route, phone reload, paused restore and isolation');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
