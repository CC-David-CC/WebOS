import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import path from 'node:path';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18217/',root=process.env.CODI_TEST_DATA_ROOT;
if(!root)throw Error('Set CODI_TEST_DATA_ROOT to isolated account data');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
try{
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]','batch'+Date.now().toString().slice(-9));await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 // Write through the actual signed gateway, so the mirror discovers an existing account folder.
 const subject=await p.evaluate(async()=>{const c=await serverFileContext();for(let i=0;i<20;i++)await c.files.write('file'+String(i).padStart(2,'0')+'.txt','old '+String(i).padStart(2,'0'));return signedInSubject()});
 await p.evaluate(()=>{const original=window.fetch;window.__ops=[];window.fetch=(u,...a)=>{if(String(u).endsWith('/gateway/use')){try{window.__ops.push(JSON.parse(a[0].body).operation)}catch{}}return original(u,...a)}});
 const first=await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();return {entries:(await c.files.list('/')).entries.length,ops:window.__ops}});assert.equal(first.entries,20);assert.equal(first.ops.filter(x=>x==='versions').length,2);assert.equal(first.ops.filter(x=>x==='version').length,0);
 const userDir=path.join(root,'users',subject.slice(5).replaceAll('-',''));await writeFile(path.join(userDir,'file19.txt'),'new 19');
 const second=await p.evaluate(async()=>{window.__ops=[];const c=await mirrorFileContext();await c.files.sync();return {text:new TextDecoder().decode((await c.files.read('/file19.txt')).data),ops:window.__ops}});assert.equal(second.text,'new 19');assert.equal(second.ops.filter(x=>x==='versions').length,2);assert.equal(second.ops.filter(x=>x==='version').length,0);
 const fallback=await p.evaluate(async()=>{window.__ops=[];const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('/gateway/version-batch-capabilities')?Promise.resolve(new Response('',{status:404})):f(u,...a);try{const c=await mirrorFileContext();await c.files.sync();return window.__ops}finally{window.fetch=f}});assert.equal(fallback.filter(x=>x==='versions').length,0);assert.equal(fallback.filter(x=>x==='version').length,20);assert.deepEqual(errors,[]);
 console.log('PASS real signed gateway batch version checks, no individual version calls, same-size external disk edit');
}finally{await context.close();await browser.disconnect()}
