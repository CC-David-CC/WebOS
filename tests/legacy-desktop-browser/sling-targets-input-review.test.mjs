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
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(p,true,user+(phone?'b':'a'));await p.evaluate(()=>{window.realMirror=mirrorFileContext;window.delay=false;window.blocked=false;window.gate=new Promise(resolve=>window.releaseGate=resolve);mirrorFileContext=async()=>{if(window.delay){window.blocked=true;await window.gate}return window.realMirror()}});await launch(p);
  await p.select('[aria-label="Ball type"]','dense');await p.evaluate(()=>document.querySelector('[aria-label="Show approximate aim guide"]').click());await p.evaluate(()=>document.querySelector('.sling-app').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('dialog.codi-confirm-dialog .codi-confirm-actions button:first-child');assert.ok(await p.$('.sling-app'),'cancel close keeps changed settings');
  const canvas=await p.$('.sling-stage canvas');await canvas.evaluate(e=>e.scrollIntoView({block:'center'}));const b=await canvas.boundingBox(),point={x:b.x+b.width*.5,y:b.y+b.height*.5,id:1},cdp=await p.createCDPSession();await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point]});await p.evaluate(()=>window.dispatchEvent(new Event('blur')));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await new Promise(r=>setTimeout(r,100));assert.match(await p.$eval('.sling-card:last-child',e=>e.textContent),/3 shots/,'focus loss cancels aimed shot');
  await p.click('.sling-save summary');await p.evaluate(()=>window.delay=true);await p.click('.sling-app [aria-label="Save to My files"]');await p.waitForFunction(()=>window.blocked);await p.$eval('[aria-label="Ball type"]',e=>{e.value='soft';e.dispatchEvent(new Event('change',{bubbles:true}))});assert.equal(await p.$eval('[aria-label="Ball type"]',e=>e.value),'dense','settings cannot change while saving');await p.$eval('[aria-label="Sling save path"]',e=>e.value='/Later.game.json');await p.evaluate(()=>window.releaseGate());await p.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Saved on this device'));assert.equal(await p.$eval('[aria-label="Sling save path"]',e=>e.value),'/Later.game.json','pending save preserves newer destination');await p.evaluate(()=>{window.delay=false;mirrorFileContext=window.realMirror});await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Sling-targets.game.json')).data)));assert.equal(saved.payload.ballType,'dense');assert.equal(saved.payload.aimAssist,false);assert.equal(saved.payload.remainingShots,3);
  await p.evaluate(()=>document.querySelector('.sling-app').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.sling-app'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Sling-targets.game.json'));await p.waitForFunction(()=>document.querySelector('.sling-app .app-status')?.textContent.includes('Target round loaded and paused'));assert.equal(await p.$eval('[aria-label="Ball type"]',e=>e.value),'dense');assert.equal(await p.$eval('[aria-label="Show approximate aim guide"]',e=>e.checked),false);
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone dirty settings, interrupted aim, pending save and account sync/reopen');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
