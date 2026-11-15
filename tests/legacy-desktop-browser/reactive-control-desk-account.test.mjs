import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18348/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'desk'+Date.now().toString().slice(-9),contexts=[],errors=[];
async function login(page,register,user=username){
 page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('reactive-control-desk'));await page.waitForSelector('.control-desk-visual canvas',{timeout:30000})}
const click=(page,label)=>page.evaluate(label=>{const button=[...document.querySelectorAll('.control-desk-app button')].find(node=>node.textContent===label||node.getAttribute('aria-label')===label);if(!button)throw Error('Missing button: '+label);button.click()},label);
try{
 const first=await browser.createBrowserContext();contexts.push(first);const page=await first.newPage();await page.setViewport({width:1366,height:900});await login(page,true);await launch(page);
 await page.$eval('[aria-label=Power]',element=>{element.value='0.3';element.dispatchEvent(new Event('input',{bubbles:true}))});
 await page.$eval('[aria-label=Frequency]',element=>{element.value='0.4';element.dispatchEvent(new Event('input',{bubbles:true}))});
 await page.$eval('[aria-label=Route]',element=>{element.value='1';element.dispatchEvent(new Event('input',{bubbles:true}))});
 await click(page,'Resume');await page.waitForFunction(()=>document.querySelector('.control-desk-progress i')?.style.width==='100%',{timeout:5000});await click(page,'Submit order');
 await page.waitForFunction(()=>document.querySelector('.control-desk-summary')?.textContent.includes('Order 2'));
 await page.evaluate(()=>document.querySelector('.control-desk-save').open=true);await page.$eval('[aria-label="Control desk save path"]',element=>element.value='/Reactive Control Desk.game.json');
 await click(page,'Save to My files');await page.waitForFunction(()=>document.querySelector('.control-desk-view .app-status')?.textContent.includes('saved to My files'));
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Reactive Control Desk.game.json')).data)));
 assert.equal(saved.appId,'reactive-control-desk');assert.deepEqual(saved.payload.completed,[0]);
 await page.evaluate(()=>document.querySelector('.control-desk-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.control-desk-app'));
 if(process.env.CODI_TEST_FILES_ROUTE!=='0'){
  await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Reactive Control Desk.game.json'));await page.waitForFunction(()=>document.querySelector('.control-desk-view .app-status')?.textContent.includes('Control state loaded and paused'),{timeout:30000});
  assert.equal(await page.$eval('[aria-label="Control desk save path"]',element=>element.value),'/Reactive Control Desk.game.json');
  await page.evaluate(()=>document.querySelector('.control-desk-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.control-desk-app'));
 }
 const fresh=await browser.createBrowserContext();contexts.push(fresh);const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.control-desk-save').open=true);await click(phone,'Open from My files');await phone.waitForSelector('[aria-label="Choose file Reactive Control Desk.game.json"]',{visible:true});await phone.click('[aria-label="Choose file Reactive Control Desk.game.json"]');await phone.waitForFunction(()=>document.querySelector('.control-desk-view .app-status')?.textContent.includes('Control state loaded and paused'),{timeout:30000});
 assert.ok((await phone.$eval('.control-desk-summary',node=>node.textContent)).includes('Order 2'));
 const isolation=await browser.createBrowserContext();contexts.push(isolation);const other=await isolation.newPage();await login(other,true,username+'b');assert.equal(await other.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Reactive Control Desk.game.json');return true}catch{return false}}),false);
 await phone.evaluate(async()=>{const context=await mirrorFileContext(),file=await context.files.read('/Reactive Control Desk.game.json');await context.files.remove('/Reactive Control Desk.game.json',file.version);await context.files.sync()});
 assert.deepEqual(errors,[]);console.log(`PASS real account save, sync, ${process.env.CODI_TEST_FILES_ROUTE==='0'?'registration-pending Files route':'Files route'}, phone reload, paused restore and isolation`);
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
