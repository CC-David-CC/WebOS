import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18312/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'lantern'+Date.now().toString().slice(-9);
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
 await page.evaluate(()=>surfaces.get('Desktop').launch('lantern-leap'));
 await page.waitForSelector('.lantern-stage canvas',{timeout:30000});
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.lantern-view button')].find(node=>node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(p,true,username+(phone?'b':'a'));await launch(p);await click(p,'Resume');
  const hero=()=>p.evaluate(()=>{const c=document.querySelector('.lantern-stage canvas'),{data}=c.getContext('2d').getImageData(0,0,c.width,c.height);let sum=0,n=0;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;if(data[i]===87&&data[i+1]===203&&data[i+2]===226){sum+=x;n++}}return {x:sum/n,n}});
  await new Promise(r=>setTimeout(r,100));const before=await hero();await p.$eval('.lantern-controls',e=>e.scrollIntoView({block:'center'}));const left=await(await p.$('.lantern-controls [aria-label="◀ Left"]')).boundingBox(),right=await(await p.$('.lantern-controls [aria-label="Right ▶"]')).boundingBox(),point=(b,id)=>({x:b.x+b.width/2,y:b.y+b.height/2,id}),a=point(left,1),b=point(right,2),cdp=await p.createCDPSession();await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a]});await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a,b]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[a]});await new Promise(r=>setTimeout(r,450));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});const after=await hero();assert.ok(before.n&&after.n&&after.x>before.x+5,`right remains held after left releases: ${JSON.stringify({before,after})}`);
  await p.focus('.lantern-stage');await p.keyboard.down('ArrowRight');await new Promise(r=>setTimeout(r,150));await p.focus('[aria-label=Room]');await p.keyboard.up('ArrowRight');await new Promise(r=>setTimeout(r,80));const stopped=await hero();await new Promise(r=>setTimeout(r,200));const later=await hero();assert.ok(Math.abs(stopped.x-later.x)<1,`board blur releases movement: ${JSON.stringify({stopped,later})}`);
  await p.evaluate(()=>document.querySelector('.lantern-save').open=true);await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent.includes('syncing with the server'));await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Lantern Leap.game.json')).data)));assert.equal(saved.appId,'lantern-leap');
  await p.evaluate(()=>document.querySelector('.lantern-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.lantern-view'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Lantern Leap.game.json'));await p.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent.includes('Checkpoint loaded and paused'));assert.ok(await p.$('.lantern-toolbar [aria-label=Resume]'));
 }
 assert.deepEqual(errors,[]);console.log('PASS overlapping touch, keyboard focus loss, save/sync/reopen on desktop and emulated phone');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
