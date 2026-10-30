import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage();
const user='sizetest'+Date.now().toString().slice(-8),errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('error',error=>{console.error('Browser renderer failed:',error.message);process.exitCode=1;});
try {
  await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args);});
  await page.goto('http://127.0.0.1:18139/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');
  await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  const rejected=await page.evaluate(async()=>{try{const c=await serverFileContext();await c.files.write('too-large.bin',new Uint8Array(128*1024*1024+1));return false;}catch{return true;}});
  assert.equal(rejected,true,'A file larger than 128 MiB must be rejected');
  console.log('Logged in; writing exactly 128 MiB.');
  const written=await page.evaluate(async()=>{const c=await serverFileContext();const data=new Uint8Array(128*1024*1024);data.fill(0x5a);data[0]=1;data[data.length-1]=2;return c.files.write('file-128m.bin',data);});
  console.log('Write accepted',JSON.stringify(written));
  const result=await page.evaluate(async()=>{const c=await serverFileContext(),r=await c.files.read('file-128m.bin');return {length:r.data.length,first:r.data[0],last:r.data.at(-1),middle:r.data[1000],sha256:r.sha256};});
  assert.equal(result.length,128*1024*1024);assert.equal(result.first,1);assert.equal(result.last,2);assert.equal(result.middle,0x5a);assert.equal(result.sha256,written.sha256);assert.deepEqual(errors,[]);
  console.log('PASS: 128 MiB authenticated server write/read with matching SHA-256',JSON.stringify(result));
} finally {await context.close();await browser.disconnect();}
