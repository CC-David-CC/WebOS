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
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(p,!phone);await launch(p);
  const savePath=phone?'/Phone Bot.game.json':'/Desktop Bot.game.json';await p.evaluate(()=>document.querySelector('[aria-label="Start"]').click());await p.$eval('.arena-controls',e=>e.scrollIntoView({block:'center'}));const f=await(await p.$('[aria-label="Drive forward"]')).boundingBox(),b=await(await p.$('[aria-label="Drive backward"]')).boundingBox(),point=(r,id)=>({x:r.x+r.width/2,y:r.y+r.height/2,id}),a=point(f,1),z=point(b,2),cdp=await p.createCDPSession();await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a]});await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a,z]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[a]});await new Promise(r=>setTimeout(r,450));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await p.$eval('[aria-label="Tabletop Bot Arena save path"]',(e,v)=>e.value=v,savePath);await p.evaluate(()=>document.querySelector('[aria-label="Save match"]').click());await p.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Match saved'));await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async path=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read(path.slice(1))).data)),savePath);assert.ok(saved.payload.player.vy<-.1,'backwards touch continues after forward release: '+saved.payload.player.vy);
  await p.evaluate(()=>document.querySelector('[aria-label="Start"]').click());await p.evaluate(()=>document.querySelector('[aria-label="New match"]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('dialog.codi-confirm-dialog .codi-confirm-actions button:first-child');await p.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('kept and paused'));await p.evaluate(()=>document.querySelector('.tabletop-arena-app').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('.codi-confirm-danger');await p.waitForFunction(()=>!document.querySelector('.tabletop-arena-app'));
  await p.evaluate(path=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),path),savePath);await p.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Match loaded and paused'));assert.ok(await p.$('[aria-label="Start"]'));
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone overlapping touches, canceled new match, sync and reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
