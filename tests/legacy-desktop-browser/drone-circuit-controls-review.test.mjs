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
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(p,true,username+(phone?'b':'a'));await launch(p);await click(p,'Run');
  await p.$eval('.drone-phone-controls',e=>e.scrollIntoView({block:'center'}));const forward=await p.$('.drone-phone-controls [aria-label=Forward]'),back=await p.$('.drone-phone-controls [aria-label=Back]'),a=await forward.boundingBox(),b=await back.boundingBox(),point=(r,id)=>({x:r.x+r.width/2,y:r.y+r.height/2,id}),f=point(a,1),g=point(b,2),cdp=await p.createCDPSession();
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[f]});await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[f,g]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[f]});await new Promise(r=>setTimeout(r,550));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('syncing with the server'));let saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Drone Circuit.game.json')).data)));assert.ok(saved.payload.velocity.x<-.2,'back touch remains active when forward touch ends: '+saved.payload.velocity.x);
  await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());await p.evaluate(()=>document.querySelector('.drone-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.drone-view'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Drone Circuit.game.json'));await p.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('Flight loaded and paused'));
  await click(p,'Run');const canvas=await p.$('.drone-stage-wrap canvas');await canvas.focus();await p.keyboard.down('w');await new Promise(r=>setTimeout(r,200));await p.focus('[aria-label="Drone save path"]');await p.keyboard.up('w');await new Promise(r=>setTimeout(r,300));await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('syncing with the server'));
  saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Drone Circuit.game.json')).data)));const velocity=saved.payload.velocity.x;await click(p,'Run');await new Promise(r=>setTimeout(r,350));await p.$eval('.drone-status',e=>e.textContent='Saving');await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('syncing with the server'));const after=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Drone Circuit.game.json')).data)));assert.ok(Math.abs(after.payload.velocity.x-velocity)<.05,`canvas blur releases keyboard throttle: ${velocity} -> ${after.payload.velocity.x}`);
 }
 assert.deepEqual(errors,[]);console.log('PASS overlapping touch, keyboard focus loss and account save/sync/reopen on desktop and phone');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
