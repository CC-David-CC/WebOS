import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18131/',dataRoot=process.env.CODI_TEST_DATA_ROOT;
if(!dataRoot)throw Error('Set CODI_TEST_DATA_ROOT to an isolated test server account-data directory.');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),page=await browser.newPage(),errors=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url())&&!r.url().startsWith(new URL(base).origin+'/'))external.push(r.url());});
try{
 await page.setViewport({width:1366,height:900});await page.goto(base);await page.waitForSelector('.login-gate');await page.click('.login-toggle');
 await page.type('[aria-label="Username"]','imagetest'+Date.now().toString().slice(-9));await page.type('[aria-label="Password"]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>!document.documentElement.classList.contains('login-required'),{timeout:20000});await page.waitForFunction(()=>document.querySelector('.codi-files-create button')&&!document.querySelector('.codi-files-create button').disabled,{timeout:20000});
 const name='image'+Date.now()+'.png';await page.evaluate(async name=>{const c=await mirrorFileContext(),canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;canvas.getContext('2d').fillRect(0,0,64,64);const blob=await new Promise(r=>canvas.toBlob(r,'image/png'));await c.files.write('/'+name,new Uint8Array(await blob.arrayBuffer()));await c.files.sync();},name);
 await page.waitForFunction(name=>[...document.querySelectorAll('[role=listitem]')].some(x=>x.getAttribute('aria-label')===name),{timeout:15000},name);
 const item=await page.evaluateHandle(name=>[...document.querySelectorAll('[role=listitem]')].find(x=>x.getAttribute('aria-label')===name),name);await item.asElement().click();await page.keyboard.press('Enter');
 await page.waitForSelector('.image-editor-content canvas',{timeout:20000});await page.evaluate(()=>[...document.querySelectorAll('.image-editor-content *')].find(x=>x.children.length===0&&x.textContent.trim()==='Resize').click());
 await page.waitForSelector('.image-editor-content input[type=number]',{timeout:10000});const width=await page.$('.image-editor-content input[type=number]');await width.click({clickCount:3});await width.type('32');await width.press('Tab');await page.waitForFunction(()=>document.querySelector('.image-editor-content').innerText.includes('32 × 32'),{timeout:10000});
 const before=await page.evaluate(async f=>(await (await mirrorFileContext()).files.read('/'+f)).sha256,name);await page.evaluate(()=>[...document.querySelectorAll('.image-editor-content button')].find(x=>x.textContent.trim()==='Save').click());
 await page.waitForFunction(()=>document.querySelector('.image-editor-content .app-status')?.textContent.includes('Saved on this device'),{timeout:30000});await page.evaluate(async()=>{await (await mirrorFileContext()).files.sync();});
 const after=await page.evaluate(async f=>({...(await (await mirrorFileContext()).files.read('/'+f)),subject:signedInSubject()}),name);assert.equal(after.status,'synced');assert.notEqual(after.sha256,before);
 const disk=await readFile(path.join(dataRoot,'users',after.subject.slice(5).replaceAll('-',''),name));assert.equal(disk.readUInt32BE(16),32);assert.equal(disk.readUInt32BE(20),32);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 await page.evaluate(()=>document.querySelector('.image-editor-content').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.image-editor-content'));
 const again=await page.evaluateHandle(name=>[...document.querySelectorAll('[role=listitem]')].find(x=>x.getAttribute('aria-label')===name),name);await again.asElement().click();await page.keyboard.press('Enter');await page.waitForSelector('.image-editor-content canvas',{timeout:20000});await page.waitForFunction(()=>document.querySelector('.image-editor-content').innerText.includes('32 × 32'),{timeout:10000});
 console.log('PASS Files → Image Editor → resize → saved browser and server PNG, no external requests');
}finally{await page.close();await browser.disconnect();}
