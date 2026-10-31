import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import path from 'node:path';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18161/';
const accountDir=process.env.CODI_TEST_ACCOUNT_DIR||'active-system/.build/simplified-local-test-18161/account-data';
const marker='Account test '+Date.now();
async function walk(dir){let results=[];for(const e of await readdir(dir,{withFileTypes:true})){const f=path.join(dir,e.name);if(e.isDirectory())results.push(...await walk(f));else if(e.isFile()&&e.name==='logic-circuit.json')results.push(f)}return results}
async function launch(){await page.click('[aria-label=Applications]');await page.waitForSelector('[aria-label=Electronics]',{visible:true});await page.click('[aria-label=Electronics]');await page.waitForSelector('[aria-label="Digital Logic"]',{visible:true});await page.click('[aria-label="Digital Logic"]');await page.waitForSelector('.digital-logic');await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));}
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]','logic'+Date.now().toString().slice(-9));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await launch();await page.waitForSelector('[model-id="a"] .btnface');
 await page.evaluate(marker=>{const e=document.querySelector('[aria-label="Circuit JSON"]');const d=JSON.parse(e.value);d.devices.gate.label=marker;e.value=JSON.stringify(d,null,2)},marker);
 await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Save to My files').click());await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Saved /logic-circuit.json'),{timeout:30000});
 await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync()});await page.waitForFunction(async()=>{let c=await mirrorFileContext();return (await c.files.read('/logic-circuit.json')).status==='synced'},{timeout:30000});
 const files=await walk(accountDir);let matched=false;for(const file of files)if((await readFile(file,'utf8')).includes(marker))matched=true;assert.ok(matched,'saved circuit reached registered account server disk');
 await page.evaluate(()=>document.querySelector('.digital-logic').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.digital-logic'));
 await launch();await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Open from My files').click());await page.waitForSelector('[aria-label="Choose file logic-circuit.json"]',{visible:true});await page.click('[aria-label="Choose file logic-circuit.json"]');await page.waitForFunction(marker=>document.querySelector('[aria-label="Circuit JSON"]')?.value.includes(marker),{},marker);await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
 assert.deepEqual(errors,[]);console.log('PASS registered menu launch, save, server sync and disk content, close and reopen from My files');
}finally{await context.close();await browser.disconnect()}
