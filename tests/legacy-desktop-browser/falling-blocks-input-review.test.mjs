import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18234/',root=process.env.CODI_TEST_DATA_ROOT;if(!root||!['127.0.0.1','localhost','[::1]'].includes(new URL(base).hostname))throw Error('Isolated loopback account data required');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),name='blocktest'+Date.now().toString().slice(-8),pass='test1234',errors=[];
async function login(page,user,register){page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>{if(page.dismissNextDialog){page.dismissNextDialog=false;return d.dismiss();}return d.accept();});await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]',pass);if(register)await page.type('[aria-label="Confirm password"]',pass);await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});}
async function launch(page){const count=await page.$$eval('.blocks-stage canvas',els=>els.length);await page.click('[aria-label=Applications]');await page.waitForSelector('[aria-label="Games"]',{visible:true});await page.click('[aria-label="Games"]');await page.waitForSelector('[aria-label="Arcade games"]',{visible:true});await page.click('[aria-label="Arcade games"]');await page.waitForSelector('button[aria-label="Falling Blocks (preview)"]',{visible:true});await page.click('button[aria-label="Falling Blocks (preview)"]');await page.waitForFunction(n=>document.querySelectorAll('.blocks-stage canvas').length===n,{timeout:30000},count+1);}
const contexts=[];
try{
 const c=await browser.createBrowserContext();contexts.push(c);const p=await c.newPage();await p.setViewport({width:390,height:844,isMobile:true,hasTouch:true});await login(p,name,true);await launch(p);
 await p.click('.blocks-app [aria-label=Resume]');
 await p.$eval('.blocks-controls',e=>e.scrollIntoView({block:'center'}));
 const left=await (await p.$('.blocks-app [aria-label="◀ Left"]')).boundingBox(),right=await (await p.$('.blocks-app [aria-label="Right ▶"]')).boundingBox();
 const point=(b,id)=>({x:b.x+b.width/2,y:b.y+b.height/2,id}),a=point(left,1),b=point(right,2),cdp=await p.createCDPSession();
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a]});
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[a,b]});
 await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[a]});
 await new Promise(resolve=>setTimeout(resolve,500));await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await p.evaluate(()=>document.querySelector('.blocks-app [aria-label=Save]').click());await p.waitForFunction(()=>document.querySelector('.blocks-app .app-status').textContent.includes('Saved on this device'));
 const result=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Falling Blocks.game.json')).data)));
 assert.ok(result.payload.active.x>=5,'releasing older finger must not stop newer right hold: '+result.payload.active.x);
 await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 await p.evaluate(()=>document.querySelector('.blocks-app').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.blocks-app'));
 await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/broken.game.json',new TextEncoder().encode(JSON.stringify({format:'ksu.game.save',schemaVersion:1,appId:'falling-blocks',kind:'logical-snapshot',gameBuild:'rules-1',contentVersion:'1',payload:{}})),null);});
 await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/broken.game.json'));await p.waitForFunction(()=>document.querySelector('.blocks-app .app-status')?.textContent.includes('Could not open game'));
 const launchRef=await p.evaluate(()=>{const el=document.querySelector('.blocks-app').closest('.window'),desktop=surfaces.get('Desktop');return desktop.windows.find(w=>String(w.id)===el.dataset.window)?.launchContext??null});
 assert.equal(launchRef,null,'invalid launch must not persist an unusable session reference');
 assert.equal(await p.evaluate(async()=>!!(await(await mirrorFileContext()).files.read('/broken.game.json')).data),true);
 assert.deepEqual(errors,[]);console.log('PASS emulated overlapping touch, invalid launch recovery and account storage');
}finally{for(const c of contexts)await c.close();await browser.disconnect();}
