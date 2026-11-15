import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18344/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'clockwork'+Date.now().toString().slice(-8);
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
 await page.evaluate(()=>surfaces.get('Desktop').launch('clockwork-room'));
 await page.waitForSelector('.clockwork-stage-wrap canvas',{timeout:30000});
 await page.waitForFunction(()=>!document.querySelector('.clockwork-loading'),{timeout:30000});
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.clockwork-view button')]
  .find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();debugPage=p;await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(p,true,username+(phone?'b':'a'));await launch(p);
  await p.evaluate(()=>{const node=document.querySelector('.clockwork-view');node.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,repeat:false}));node.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,repeat:true}))});assert.ok(await p.$('.clockwork-toolbar [aria-label=Pause]'),'repeated Escape must not undo Run');
  for(const label of ['Use Gear alignment','Use Chime sequence','Use Pendulum brake','Use Exit lock'])await click(p,label);await p.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('exit is open'));
  await click(p,'Save');await p.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('syncing with the server'));await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());
  await p.evaluate(()=>document.querySelector('.clockwork-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.clockwork-view'));
  await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/broken.game.json',new TextEncoder().encode(JSON.stringify({format:'ksu.game.save',schemaVersion:1,appId:'clockwork-room',kind:'logical-snapshot',payload:{}})),null)});await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/broken.game.json'));await p.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Could not open room'));
  assert.equal(await p.evaluate(()=>{const el=document.querySelector('.clockwork-view').closest('.window');return surfaces.get('Desktop').windows.find(w=>String(w.id)===el.dataset.window)?.launchContext??null}),null);assert.equal(await p.evaluate(async()=>!!(await(await mirrorFileContext()).files.read('/broken.game.json')).data),true);
  await p.evaluate(()=>document.querySelector('.clockwork-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.clockwork-view'));
  for(const mode of ['transient','abort','conflict','missing']){
   await p.evaluate(mode=>{window.realMirrorFileContext=mirrorFileContext;mirrorFileContext=async()=>{const original=await window.realMirrorFileContext();const files=Object.create(original.files);files.read=async path=>{if(mode==='transient')throw Error('Temporary network failure');if(mode==='abort')throw new DOMException('Cancelled','AbortError');if(mode==='missing')throw Error('File not found.');const result=await original.files.read(path);return {...result,status:'conflict'}};const context=Object.create(original);Object.defineProperty(context,'files',{value:files});return context};surfaces.get('Desktop').open('clockwork-room',{version:1,storage:'mirror',path:'/Clockwork Room.game.json',owner:signedInSubject()})},mode);
   await p.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Could not open room'));
   const ref=await p.evaluate(()=>{const el=document.querySelector('.clockwork-view').closest('.window');return surfaces.get('Desktop').windows.find(w=>String(w.id)===el.dataset.window)?.launchContext??null});
   if(mode==='missing')assert.equal(ref,null,'confirmed missing file clears restore reference');else assert.equal(ref?.path,'/Clockwork Room.game.json',mode+' preserves restore reference');
   await p.evaluate(()=>{mirrorFileContext=window.realMirrorFileContext;document.querySelector('.clockwork-view').closest('.window').querySelector('[aria-label=Close]').click()});await p.waitForFunction(()=>!document.querySelector('.clockwork-view'));
  }
  await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Clockwork Room.game.json'));await p.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room loaded and paused'));assert.deepEqual(await p.$$eval('.clockwork-objectives li',rows=>rows.map(row=>row.dataset.solved)),['true','true','true','true']);
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone complete room, keyboard repeat, sync, invalid/missing recovery, transient/conflict/abort retention and reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
