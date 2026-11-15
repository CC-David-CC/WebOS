import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));
try{
 await page.emulateMediaFeatures([{name:'prefers-reduced-motion',value:'reduce'}]);
 const manifest=JSON.parse(await readFile(process.env.CODI_BLOCKS_MANIFEST||'.build/blocks-motion/apps.json','utf8'));const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');await page.goto('http://127.0.0.1:18334/?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>{const c=document.querySelector('.blocks-coach canvas');if(!c)return false;const p=c.getContext('2d').getImageData(90,13,1,1).data;return p[0]>220&&p[1]>170},{timeout:30000});
 const sample=()=>page.evaluate(async()=>{const c=document.querySelector('.blocks-coach canvas').getContext('2d'),values=[];for(let i=0;i<36;i++){const p=c.getImageData(68,72,1,1).data;values.push(p[0]);await new Promise(r=>setTimeout(r,100));}return values;});
 const still=await sample();assert.ok(still.every(v=>v<50),'device reduced-motion preference must suppress blinking: '+still);
 await page.click('.blocks-settings summary');await page.select('[aria-label="Coach motion"]','full');const moving=await sample();assert.ok(moving.some(v=>v>70),'explicit full-motion override should permit blinking: '+moving);
 await page.select('[aria-label="Coach motion"]','system');const again=await sample();assert.ok(again.every(v=>v<50),'system setting should suppress blinking again: '+again);
 await page.evaluate(()=>document.querySelector('.blocks-app [aria-label=Resume]').click());await page.waitForFunction(()=>{const p=document.querySelector('.blocks-coach canvas').getContext('2d').getImageData(90,13,1,1).data;return p[0]<100&&p[1]>190},{timeout:10000});
 await page.evaluate(()=>{for(const x of window.instances){x.controller.abort();x.app.dispose();x.app.element.remove();}});assert.deepEqual(errors,[]);console.log('PASS reduced-motion device default, user override, restored preference, live state indicator and cleanup');
}catch(e){console.error('FAIL',e.message,'errors:',errors);process.exitCode=1;}finally{await context.close();await browser.disconnect();}
