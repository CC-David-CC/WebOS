import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18346/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'sky'+Date.now().toString().slice(-9);
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
 await page.evaluate(()=>surfaces.get('Desktop').launch('sky-courier'));
 await page.waitForSelector('.sky-stage canvas',{timeout:30000});
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.sky-courier button')].find(node=>node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 const c=await browser.createBrowserContext();contexts.push(c);const p=await c.newPage();await p.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(p,true);console.log('Test account',username,await p.evaluate(()=>signedInSubject()));await launch(p);await click(p,'Resume');
 const pixels=()=>p.evaluate(()=>{const c=document.querySelector('.sky-stage canvas'),ctx=c.getContext('2d'),{data}=ctx.getImageData(0,0,c.width,c.height);let xsum=0,n=0,cyan=0;for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){const i=(y*c.width+x)*4;if(data[i]===112&&data[i+1]===217&&data[i+2]===154){xsum+=x;n++}if(data[i]===93&&data[i+1]===224&&data[i+2]===242)cyan++}return {x:xsum/n,n,cyan}});
 await new Promise(r=>setTimeout(r,250));const before=await pixels();const right=await p.$('.sky-controls [aria-label="Right ▶"]');await right.evaluate(e=>e.scrollIntoView({block:'center'}));const box=await right.boundingBox(),cdp=await p.createCDPSession(),point={x:box.x+box.width/2,y:box.y+box.height/2,id:1};await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point]});await new Promise(r=>setTimeout(r,500));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await new Promise(r=>setTimeout(r,100));const after=await pixels();assert.ok(before.n&&after.n&&after.x-before.x>30,`held steering moves continuously: ${JSON.stringify({before,after})}`);
 await p.focus('.sky-stage');await p.keyboard.down('Space');let firing;const fireDeadline=Date.now()+5000;do{await new Promise(r=>setTimeout(r,45));firing=await pixels()}while(!firing.cyan&&Date.now()<fireDeadline);assert.ok(firing.cyan>0,'Space produces visible projectiles within five seconds');await p.keyboard.up('Space');await new Promise(r=>setTimeout(r,1700));const stopped=await pixels();assert.equal(stopped.cyan,0,'Space release stops firing after existing shots leave');
 await p.evaluate(()=>document.querySelector('.sky-courier').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('.codi-confirm-danger');await p.waitForFunction(()=>!document.querySelector('.sky-courier'));
 assert.deepEqual(errors,[]);console.log('PASS held emulated touch steering, keyboard fire release, and dirty close');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
