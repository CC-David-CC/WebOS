import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
const name=process.env.CODI_TEST_USER;
if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Set a disposable browserprobe username');
function guard(action){const p=spawnSync('ssh',['-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','/tmp/codi-live-browser-report-admin-guard.py',action,name],{encoding:'utf8',timeout:60000});if(p.status!==0)throw Error('Report admin guard '+action+': '+p.stderr);console.log(p.stdout.trim());}
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});const context=await browser.createBrowserContext(),page=await context.newPage();let attempted=false;
try{
 await page.setViewport({width:1366,height:950});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto('https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 attempted=true;guard('apply');
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 await page.waitForFunction(()=>!![...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.report-admin'),{timeout:30000});
 await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;const a=r.querySelector('[aria-label="Website address"]');a.value='https://example.com/';a.closest('form').requestSubmit();});
 await page.waitForFunction(async()=>{const db=await new Promise((ok,no)=>{const q=indexedDB.open('codi-browser-domain-usage');q.onsuccess=()=>ok(q.result);q.onerror=()=>no(q.error)});try{if(!db.objectStoreNames.contains('events'))return false;return await new Promise((ok,no)=>{const q=db.transaction('events').objectStore('events').getAll();q.onsuccess=()=>ok(q.result.some(e=>e.domain==='example.com'));q.onerror=()=>no(q.error)})}finally{db.close()}},{timeout:90000});
 await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;r.querySelector('details').open=true;[...r.querySelectorAll('.report-admin button')].find(x=>x.textContent==='Request reports for one hour').click()});
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.report-admin pre')?.textContent.includes('Report requested'),{timeout:30000});
 await page.waitForFunction(()=>!![...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.report-admin select')?.value,{timeout:30000});
 let seen=false;for(let n=0;n<18;n++){
  await new Promise(r=>setTimeout(r,5000));
  await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...r.querySelectorAll('.report-admin button')].find(x=>x.textContent==='Show totals').click()});
  await new Promise(r=>setTimeout(r,600));
  const output=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('.report-admin pre').textContent);
  if(output.includes('1 device(s)')&&output.includes('example.com')){seen=true;break;}
 }
 assert.ok(seen,'Requested report did not appear in administrator UI');console.log('PASS live administrator UI requested and displayed a signed device report');
}finally{
 await context.close();await browser.disconnect();
 if(attempted)guard('restore');
}
