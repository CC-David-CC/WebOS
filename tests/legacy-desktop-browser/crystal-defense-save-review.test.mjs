import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18348/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'crystal'+Date.now().toString().slice(-9);
const contexts=[],errors=[];let debugPage;

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
 await page.evaluate(()=>surfaces.get('Desktop').launch('crystal-defense'));
 await page.waitForSelector('.crystal-stage canvas',{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('.crystal-view .crystal-note')?.textContent.includes('Wave 0/8'));
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.crystal-view button')]
  .find(node=>node.textContent===label||node.getAttribute('aria-label')===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();debugPage=p;await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(p,true,username+(phone?'b':'a'));await p.evaluate(()=>{window.realMirror=mirrorFileContext;window.blocked=false;window.enableDelay=false;window.gate=new Promise(resolve=>window.releaseGate=resolve);mirrorFileContext=async()=>{const c=await window.realMirror();const f=new Proxy(c.files,{get(target,key){if(key==='stat')return async path=>{if(window.enableDelay){window.blocked=true;await window.gate}return target.stat?target.stat(path):target.read(path)};const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}});const wrapped=Object.create(c);Object.defineProperty(wrapped,'files',{value:f});return wrapped}});await launch(p);
  await click(p,'Socket 3');await click(p,'Build Spark');await click(p,'Resume');await p.waitForFunction(()=>document.querySelector('.crystal-note')?.textContent.includes('Wave 1/8'));
  await p.evaluate(()=>document.querySelector('.crystal-view').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,repeat:false,cancelable:true})));assert.ok(await p.$('.crystal-view [aria-label=Resume]'));
  await p.evaluate(()=>{window.enableDelay=true});
  await click(p,'Save to My files');await p.waitForFunction(()=>window.blocked);await p.evaluate(()=>{const el=document.querySelector('.crystal-view');el.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));el.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true,repeat:true}))});assert.ok(await p.$('.crystal-view [aria-label=Resume]'),'Escape cannot resume while saving');await p.evaluate(()=>window.releaseGate());await p.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('syncing with the server'),{timeout:5000});await p.evaluate(()=>{window.enableDelay=false;mirrorFileContext=window.realMirror});
  await p.evaluate(async()=>{const c=await mirrorFileContext(),file=await c.files.read('/Crystal Defense.game.json');await c.files.remove('/Crystal Defense.game.json',file.version);await c.files.sync()});await click(p,'Socket 4');await click(p,'Build Bloom');await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('saved defense was removed'));assert.equal(await p.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Crystal Defense.game.json');return true}catch{return false}}),false,'deleted file remains deleted');
  await p.evaluate(()=>document.querySelector('.crystal-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('.codi-confirm-danger');await p.waitForFunction(()=>!document.querySelector('.crystal-view'));
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone busy Escape, deleted save protection and dirty close');
}catch(error){console.error('diagnostic',await debugPage?.evaluate(()=>({status:document.querySelector('.crystal-view .app-status')?.textContent,blocked:window.blocked,body:document.querySelector('.crystal-view')?.innerText.slice(0,300)})));throw error}finally{for(const context of contexts)await context.close();await browser.disconnect()}
