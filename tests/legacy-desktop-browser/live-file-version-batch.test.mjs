import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const name=process.env.CODI_TEST_USER;if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Provide a disposable browserprobe account name.');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
try{
 await p.goto('https://ksu.codes/');await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',name);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await p.evaluate(async()=>{const c=await serverFileContext();for(let i=0;i<20;i++){const name='batch-probe-'+String(i).padStart(2,'0')+'.txt';await c.files.write(name,'batch fixture '+String(i).padStart(2,'0'))}});
 await p.evaluate(()=>{const original=window.fetch;window.__batchOps=[];window.fetch=(u,...a)=>{if(String(u).endsWith('/gateway/use')){try{window.__batchOps.push(JSON.parse(a[0].body).operation)}catch{}}return original(u,...a)}});
 const result=await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();return {entries:(await c.files.list('/')).entries.length,ops:window.__batchOps}});
 assert.equal(result.entries,20);assert.ok(result.ops.filter(x=>x==='versions').length>=2);assert.equal(result.ops.filter(x=>x==='version').length,0);assert.deepEqual(errors,[]);console.log('PASS live signed 20-file mirror scan:',result.ops.filter(x=>x==='versions').length,'batch operations');
}finally{await context.close();await browser.disconnect()}
