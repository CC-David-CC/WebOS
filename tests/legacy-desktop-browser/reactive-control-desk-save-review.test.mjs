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
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(p,true,username+(phone?'b':'a'));
  await p.evaluate(()=>{window.realMirror=mirrorFileContext;window.blocked=false;window.enableDelay=true;window.gate=new Promise(resolve=>window.releaseGate=resolve);mirrorFileContext=async()=>{const c=await window.realMirror(),f=new Proxy(c.files,{get(target,key){if(key==='stat')return async path=>{if(window.enableDelay){window.blocked=true;await window.gate}return target.stat?target.stat(path):target.read(path)};const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}}),wrapped=Object.create(c);Object.defineProperty(wrapped,'files',{value:f});return wrapped}});await launch(p);
  for(const [label,value] of [['Power','0.3'],['Frequency','0.4'],['Route','1']])await p.$eval(`[aria-label="${label}"]`,(e,value)=>{e.value=value;e.dispatchEvent(new Event('input',{bubbles:true}))},value);
  await p.evaluate(()=>document.querySelector('.control-desk-save').open=true);await click(p,'Save to My files');await p.waitForFunction(()=>window.blocked);await click(p,'Resume');await p.waitForFunction(()=>parseFloat(document.querySelector('.control-desk-progress i')?.style.width)>10,{timeout:10000});await p.evaluate(()=>window.releaseGate());await p.waitForFunction(()=>document.querySelector('.control-desk-status')?.textContent.includes('earlier control state'),{timeout:10000});
  await p.evaluate(()=>{window.enableDelay=false;mirrorFileContext=window.realMirror});await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Reactive Control Desk.game.json')).data)));assert.equal(saved.payload.stableMs,0,'saved snapshot precedes resumed stability');
  await p.evaluate(()=>document.querySelector('.control-desk-app').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('.codi-confirm-danger');await p.waitForFunction(()=>!document.querySelector('.control-desk-app'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Reactive Control Desk.game.json'));await p.waitForFunction(()=>document.querySelector('.control-desk-status')?.textContent.includes('Control state loaded and paused'));assert.equal(await p.$eval('.control-desk-progress i',e=>e.style.width),'0%');
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone pending-save stability, dirty close, sync and reopen');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
