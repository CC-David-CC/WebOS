import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {appendFile,open,unlink} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
const id=randomBytes(5).toString('hex'),fixture='/tmp/codi-browser-html-'+id+'.html',username=process.env.CODI_TEST_USER||'browserprobe'+id;
if(!/^browserprobe[0-9a-f]{10}$/.test(username))throw Error('Expected a disposable test account');
const head=Buffer.from('<!doctype html><html><body style="background:rgb(11,211,111)"><h1>Large HTML works</h1><!--'),tail=Buffer.from('--></body></html>'),chunk=Buffer.alloc(1048576,32);
const file=await open(fixture,'wx');try{await file.write(head);for(let remaining=128*1024*1024-head.length-tail.length;remaining>0;){const size=Math.min(remaining,chunk.length);await file.write(chunk,0,size);remaining-=size;}await file.write(tail);}finally{await file.close();}
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.setViewport({width:1366,height:950});await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18192/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 const picker=await page.evaluateHandle(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('input[type=file]'));await picker.asElement().uploadFile(fixture);
 await page.waitForFunction(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot;const c=r?.querySelector('canvas');if(!c)return false;const x=c.getContext('2d').getImageData(10,10,1,1).data;return x[0]===11&&x[1]===211&&x[2]===111},{timeout:180000});
 const status=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('.status').textContent);assert.doesNotMatch(status,/error|limit|failed|timed out/i);console.log('PASS exactly 128 MiB HTML rendered by real Gecko worker');
 await appendFile(fixture,'x');await picker.asElement().uploadFile(fixture);
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent.includes('HTML file too large'),{timeout:30000});console.log('PASS HTML over 128 MiB rejected');
 await page.evaluate(async()=>{const head=new TextEncoder().encode('<html><body style="background:rgb(211,22,177)"><h1>Account HTML</h1><!--'),tail=new TextEncoder().encode('--></body></html>'),data=new Uint8Array(3*1024*1024);data.fill(32);data.set(head);data.set(tail,data.length-tail.length);const c=await mirrorFileContext();await c.files.write('/browser-large.html',data)});
 await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...r.querySelectorAll('button')].find(x=>x.textContent==='Open from My files').click()});
 await page.waitForSelector('[aria-label="Choose file browser-large.html"]',{timeout:30000});await page.click('[aria-label="Choose file browser-large.html"]');
 await page.waitForFunction(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot,c=r?.querySelector('canvas');if(!c)return false;const x=c.getContext('2d').getImageData(10,10,1,1).data;return x[0]===211&&x[1]===22&&x[2]===177},{timeout:90000});
 const readable=await page.evaluate(async()=>{const c=await mirrorFileContext();return (await c.files.read('/browser-large.html')).data.byteLength});assert.equal(readable,3*1024*1024);console.log('PASS My files opens HTML above the old limit without detaching saved bytes');
 await page.evaluate(async()=>{const c=await mirrorFileContext(),f=await c.files.read('/browser-large.html');await c.files.remove('/browser-large.html',f.version);await c.files.sync()});
}finally{await context.close();await browser.disconnect();await unlink(fixture).catch(()=>{})}
