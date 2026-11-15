import puppeteer from 'puppeteer-core';
import path from 'node:path';
const {CODI_TEST_USER:user,CODI_TEST_PASSWORD:password,CODI_TEST_FILE_ROOT:root}=process.env;
if(!user||!password||!root)throw Error('Set CODI_TEST_USER, CODI_TEST_PASSWORD and CODI_TEST_FILE_ROOT for a disposable test account.');
import {writeFile} from 'node:fs/promises';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18130/');await page.waitForSelector('.login-gate');await page.type('[aria-label="Username"]',user);await page.type('[aria-label="Password"]',password);await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>!document.documentElement.classList.contains('login-required'),{timeout:20000});
 await page.waitForFunction(()=>document.querySelector('.codi-files-create button')&&!document.querySelector('.codi-files-create button').disabled,{timeout:20000});
 const name='integration'+Date.now()+'.txt';await page.click('[aria-label="New item name"]');await page.type('[aria-label="New item name"]',name);await page.waitForFunction(n=>document.querySelector('[aria-label="New item name"]')?.value===n,{},name);
 await page.evaluate(()=>[...document.querySelectorAll('.codi-files-create button')].find(x=>x.textContent==='New text file').click());await page.waitForSelector('[aria-label="Text document"]',{timeout:20000});await page.waitForFunction(()=>!document.querySelector('[aria-label="Text document"]').disabled,{timeout:10000});await page.click('[aria-label="Text document"]');await page.type('[aria-label="Text document"]','Browser content');await page.evaluate(()=>[...document.querySelectorAll('.editor-content button')].find(x=>x.textContent==='Save').click());
 await page.waitForFunction(async n=>{try{const c=await mirrorFileContext();return (await c.files.read('/'+n)).status==='synced';}catch{return false;}},{timeout:30000},name);
 const file=path.join(root,name);await writeFile(file,'Changed directly on disk');
 await page.evaluate(()=>[...document.querySelectorAll('.editor-content button')].find(x=>x.textContent==='Reload').click());await page.waitForFunction(()=>document.querySelector('[aria-label="Text document"]')?.value==='Changed directly on disk',{timeout:30000});console.log('PASS Chonky create → Text save → server disk edit → Reload');
 await writeFile(file,'Changed a second time');await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();});await page.waitForFunction(()=>[...document.querySelectorAll('.editor-content .app-status')].some(x=>x.textContent.includes('saved file changed')),{timeout:10000});console.log('PASS open editor notices a changed disk file');
 console.log('Chonky visible:',await page.evaluate(()=>!!document.querySelector('.codi-chonky [role="list"]')),'Errors:',JSON.stringify(errors));
}finally{await page.close();await browser.disconnect();}
