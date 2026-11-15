import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18268/';
const username=process.env.CODI_TEST_USERNAME||'snapshot'+Date.now().toString().slice(-8);
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19267',protocolTimeout:240000});
const context=await browser.createBrowserContext(),page=await context.newPage();
const dir=await mkdtemp(path.join(os.tmpdir(),'codi-source-snapshot-')),file=path.join(dir,'source.txt');
try{
 const size=Number(process.env.CODI_SIZE_MIB||0);assert.ok(Number.isInteger(size)&&size>=0&&size<=128);const original=size?Buffer.alloc(size*1024*1024,0x51):Buffer.from('Browser copy survives source removal.\n');const expected=createHash('sha256').update(original).digest('hex');await writeFile(file,original);
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>{const input=document.createElement('input');input.type='file';input.id='snapshot-fixture';document.body.append(input)});
 await (await page.$('#snapshot-fixture')).uploadFile(file);await page.setOfflineMode(true);
 await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/snapshot.txt',document.querySelector('#snapshot-fixture').files[0],null)});
 await rm(file);const value=await page.evaluate(async()=>{const r=await(await mirrorFileContext()).files.read('/snapshot.txt'),hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',r.data))].map(x=>x.toString(16).padStart(2,'0')).join('');return {size:r.data.length,hash}});assert.equal(value.size,original.length);assert.equal(value.hash,expected);
 await page.setOfflineMode(false);await page.evaluate(async()=>{await(await mirrorFileContext()).files.sync()});const saved=await page.evaluate(async()=>{const r=await(await serverFileContext()).files.read('snapshot.txt');return {size:r.data.length,hash:r.sha256}});assert.deepEqual(saved,value);
 console.log('PASS uploaded File survives source deletion while offline and subsequently syncs');
}finally{await context.close();await browser.disconnect();await rm(dir,{recursive:true,force:true})}
