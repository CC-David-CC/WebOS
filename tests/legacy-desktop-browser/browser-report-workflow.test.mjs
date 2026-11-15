import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18148/';
async function signin(name){
  const page=await context.newPage();
  page.on('response',response=>{if(response.url().includes('/reports/'))console.log(name,'report HTTP',response.status(),new URL(response.url()).pathname.split('/').pop());});
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(base);await page.waitForSelector('.login-form');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});return page;
}
async function launch(page){
  await page.click('[aria-label=Applications]');await page.waitForSelector('[aria-label=Browser]');await page.click('[aria-label=Browser]');
  await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].some(e=>e.shadowRoot?.querySelector('.status')?.textContent==='Ready'),{timeout:180000});
}
try{
  const user=await signin('reportuserfixture');await launch(user);
  await user.evaluate(()=>{const root=[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot)?.shadowRoot;const input=root.querySelector('[aria-label="Website address"]');input.value='https://example.com/';input.closest('form').requestSubmit();});
  await user.waitForFunction(async()=>{const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('codi-browser-domain-usage');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});try{if(!db.objectStoreNames.contains('events'))return false;return await new Promise((resolve,reject)=>{const r=db.transaction('events').objectStore('events').getAll();r.onsuccess=()=>resolve(r.result.some(e=>e.domain==='example.com'));r.onerror=()=>reject(r.error);});}finally{db.close();}},{timeout:90000,polling:1000});
  const admin=await signin('reportadminfixture');await launch(admin);
  await admin.waitForFunction(()=>[...document.querySelectorAll('.window-content')].some(e=>e.shadowRoot?.querySelector('.report-admin')),{timeout:30000});
  assert.equal(await user.evaluate(()=>!![...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot)?.shadowRoot.querySelector('.report-admin')),false);
  const initial=await admin.evaluate(()=>[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot)?.shadowRoot.querySelector('.report-admin select').options.length);assert.equal(initial,0);
  await admin.evaluate(()=>[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot).shadowRoot.querySelector('.report-admin button').click());
  await admin.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot)?.shadowRoot.querySelector('.report-admin select')?.options.length===1,{timeout:30000});
  const deadline=Date.now()+75000;let text='';
  while(Date.now()<deadline){
    await admin.evaluate(()=>{const panel=[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot).shadowRoot.querySelector('.report-admin');[...panel.querySelectorAll('button')].find(b=>b.textContent==='Show totals').click();});
    await new Promise(resolve=>setTimeout(resolve,1500));
    text=await admin.evaluate(()=>[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot).shadowRoot.querySelector('.report-admin pre').textContent);
    if(text.includes('example.com'))break;
  }
  assert.match(text,/1 device\(s\)/);assert.match(text,/example\.com\s+\d+/);
  console.log('PASS signed account reports stay local until requested; only administrator can request and view real device totals');
}finally{await context.close();await browser.disconnect();}
