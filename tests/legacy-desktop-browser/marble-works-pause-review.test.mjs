import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18348/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'marble'+Date.now().toString().slice(-9);
const contexts=[],errors=[];
async function login(page,register,user=username){
 page.on('pageerror',error=>errors.push(error.message));
 page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{
  const original=window.fetch;
  window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')
   ?Promise.resolve(new Response('',{status:404}))
   :original(url,...args);
 });
 await page.goto(base);await page.waitForSelector('.login-toggle');
 if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');
 if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){
 await page.evaluate(()=>surfaces.get('Desktop').launch('marble-works'));
 await page.waitForSelector('.marble-board',{timeout:30000});
}
const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.marble-view button')]
  .find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
 if(!button)throw Error('Missing button: '+label);button.click();
},label);
try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const page=await context.newPage();await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(page,true,username+(phone?'b':'a'));console.log('Test account',username+(phone?'b':'a'),await page.evaluate(()=>signedInSubject()));await launch(page);
  await click(page,'Run');await page.waitForSelector('.marble-view [aria-label=Pause]');await click(page,'Pause');
  const info=()=>page.$eval('.marble-info',e=>e.textContent);const paused=await info();assert.match(paused,/Paused · running/);await new Promise(r=>setTimeout(r,200));assert.equal(await info(),paused,'elapsed time stays fixed while paused');
  await page.evaluate(()=>{document.querySelector('.marble-view [aria-label=Resume]').click();window.dispatchEvent(new Event('blur'))});await page.waitForSelector('.marble-view [aria-label=Resume]');assert.match(await info(),/Paused · running/);
  await page.evaluate(()=>{document.querySelector('.marble-view [aria-label=Resume]').click();document.querySelector('.marble-view [aria-label=Pause]').click()});
  await click(page,'Save to My files');await page.waitForFunction(()=>document.querySelector('.marble-view .app-status')?.textContent.includes('syncing with the server'));await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
  await page.evaluate(()=>document.querySelector('.marble-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.marble-app'));
  await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Marble Works.game.json'));await page.waitForFunction(()=>document.querySelector('.marble-view .app-status')?.textContent.includes('Track loaded and paused'));assert.ok(await page.$('.marble-view [aria-label=Resume]'));
  await click(page,'Resume');await page.waitForSelector('.marble-view [aria-label=Pause]');
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone pause, focus-loss resume, account sync and running-save reopen');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
