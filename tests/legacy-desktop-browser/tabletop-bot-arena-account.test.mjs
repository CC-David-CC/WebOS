import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18466/';
const username=process.env.CODI_TEST_USER||'arena'+Date.now().toString().slice(-9);
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19466',protocolTimeout:120000});
const contexts=[],errors=[];
async function login(page,register){
  page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
  await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
  await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');
  await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');
  if(register)await page.type('[aria-label="Confirm password"]','test1234');
  await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('tabletop-bot-arena'));await page.waitForSelector('.arena-stage canvas',{timeout:30000});await page.waitForFunction(()=>document.querySelector('.arena-score-output')?.textContent.includes('s'))}
try{
  const first=await browser.createBrowserContext();contexts.push(first);const page=await first.newPage();await page.setViewport({width:1366,height:900});await login(page,true);await launch(page);
  await page.evaluate(()=>{const field=document.createElement('input');field.id='arena-focus-review';document.querySelector('.arena-view').append(field);field.focus()});await page.keyboard.type('wasd r');assert.equal(await page.$eval('#arena-focus-review',e=>e.value),'wasd r');
  await page.evaluate(()=>{document.querySelector('#arena-focus-review').remove();document.querySelector('.arena-view').closest('.window').classList.remove('focused')});
  const prevented=await page.evaluate(()=>{const e=new KeyboardEvent('keydown',{key:'w',bubbles:true,cancelable:true});window.dispatchEvent(e);return e.defaultPrevented});assert.equal(prevented,false);await page.evaluate(()=>document.querySelector('.arena-view').closest('.window').classList.add('focused'));
  await page.evaluate(()=>document.querySelector('[aria-label="Start"]').click());await page.click('[aria-label="Save match"]');
  await page.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Match saved'),{timeout:30000});
  await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
  const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Tabletop Bot Arena.game.json')).data)));
  assert.equal(saved.appId,'tabletop-bot-arena');assert.equal(saved.payload.paused,true);
  await page.evaluate(()=>document.querySelector('.tabletop-arena-app').closest('.window').querySelector('[aria-label=Close]').click());
  await page.waitForFunction(()=>!document.querySelector('.tabletop-arena-app'));
  await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Tabletop Bot Arena.game.json'));
  await page.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Match loaded and paused'),{timeout:30000});
  const fresh=await browser.createBrowserContext();contexts.push(fresh);const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(phone,false);
  await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
  await phone.evaluate(()=>document.querySelector('[aria-label="Open from My files"]').click());
  await phone.waitForSelector('[aria-label="Choose file Tabletop Bot Arena.game.json"]');await phone.click('[aria-label="Choose file Tabletop Bot Arena.game.json"]');
  await phone.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Match loaded and paused'),{timeout:30000});
  assert.deepEqual(errors,[]);
  console.log('PASS account match save, sync, Files route, close and phone paused reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
