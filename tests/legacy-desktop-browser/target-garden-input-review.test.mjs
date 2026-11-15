import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18363/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'targetgarden'+Date.now().toString().slice(-8),contexts=[],errors=[];
async function login(page,register,user=username){
 page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
const click=(page,label)=>page.evaluate(label=>{const button=[...document.querySelectorAll('.target-garden-view button')].find(node=>node.textContent===label);if(!button)throw Error('Missing button: '+label);button.click()},label);
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('target-garden'));await page.waitForSelector('.target-garden-canvas',{timeout:30000});await page.waitForFunction(()=>document.querySelector('.target-garden-status')?.textContent.length)}
try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(p,true,username+(phone?'b':'a'));await launch(p);await click(p,'Start round');
  const ammo=async()=>Number((await p.$eval('.target-garden-view',e=>e.textContent)).match(/Ammo (\d+)\//)[1]);const initial=await ammo(),pad=await p.$('.target-garden-aim');await pad.evaluate(e=>e.scrollIntoView({block:'center'}));const rect=await pad.boundingBox(),a={x:rect.x+rect.width*.35,y:rect.y+rect.height*.5,id:1},b={x:rect.x+rect.width*.65,y:rect.y+rect.height*.5,id:2},cdp=await p.createCDPSession();
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a]});await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a,b]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[b]});assert.equal(await ammo(),initial,'other finger must not fire');await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await ammo(),initial-1,'aim owner fires exactly once');
  await p.evaluate(()=>document.querySelector('.target-garden-aim').dispatchEvent(new KeyboardEvent('keydown',{key:' ',bubbles:true,cancelable:true,repeat:true})));assert.equal(await ammo(),initial-1,'Space repeat must not fire');
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a]});await p.evaluate(()=>window.dispatchEvent(new Event('blur')));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await ammo(),initial-1,'interrupted aim must not fire');
  await p.evaluate(()=>document.querySelector('.target-garden-save').open=true);await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.target-garden-status')?.textContent.includes('syncing with the server'));await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Target Garden.game.json')).data)));assert.equal(saved.payload.ammo,initial-1);
  await p.evaluate(()=>document.querySelector('.target-garden-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.target-garden-view'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Target Garden.game.json'));await p.waitForFunction(()=>document.querySelector('.target-garden-status')?.textContent.includes('Checkpoint loaded and paused'));assert.equal(await ammo(),initial-1);
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone pointer ownership, repeat guard, interrupted aim and save/sync/reopen');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
