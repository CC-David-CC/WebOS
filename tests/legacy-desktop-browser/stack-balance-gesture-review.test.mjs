import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18346/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'stack'+Date.now().toString().slice(-9);
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
 await page.goto(base);
 await page.waitForSelector('.login-toggle');
 if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);
 await page.type('[aria-label=Password]','test1234');
 if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}

async function launch(page){
 await page.evaluate(()=>surfaces.get('Desktop').launch('stack-balance'));
 await page.waitForSelector('.stack-stage canvas',{timeout:30000});
 await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('build'),{timeout:30000});
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.stack-view button')]
  .find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const page=await context.newPage();await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(page,true,username+(phone?'b':'a'));await launch(page);await click(page,'Run');
  const canvas=await page.$('.stack-stage canvas');await canvas.evaluate(e=>e.scrollIntoView({block:'center'}));const box=await canvas.boundingBox(),point={x:box.x+box.width/2,y:box.y+box.height/2,id:1},cdp=await page.createCDPSession();
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point]});await cdp.send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});
  await click(page,'Save to My files');await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('Tower saved to My files'));
  let saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Stack Balance.game.json')).data)));assert.equal(saved.payload.blocks.length,0,'cancelled gesture must not release a block');
  await click(page,'Run');await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await page.evaluate(()=>{const e=document.querySelector('.stack-view');e.dispatchEvent(new KeyboardEvent('keydown',{key:' ',bubbles:true,cancelable:true,repeat:true}))});await page.$eval('.stack-view .app-status',e=>e.textContent='Saving');await click(page,'Save to My files');await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('Tower saved to My files'));await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Stack Balance.game.json')).data)));assert.equal(saved.payload.blocks.length,1,'normal drop releases once and repeated Space does not add another');
  const infoBefore=await page.$eval('.stack-info',e=>e.textContent);await page.evaluate(()=>document.querySelector('.stack-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.stack-app'));await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Stack Balance.game.json'));await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('Tower loaded and paused'));assert.equal(await page.$eval('.stack-info',e=>e.textContent),infoBefore);
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone cancelled gesture, normal drop, key-repeat guard and account save/sync/reopen');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
