import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const names=[process.env.CODI_TEST_USER_A,process.env.CODI_TEST_USER_B];
if(names.some(x=>!/^browserprobe[0-9a-f]{10}$/.test(x||''))||names[0]===names[1])throw Error('Two distinct disposable accounts required');
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const contexts=[],pages=[];const path='/browser-isolation-test.html';
const documents=['<!doctype html><html><body style="margin:0;background:rgb(22,173,91)"><h1>Account A</h1></body></html>','<!doctype html><html><body style="margin:0;background:rgb(173,22,91)"><h1>Account B</h1></body></html>'];
async function login(page,name,register){
 await page.goto('https://ksu.codes/');await page.waitForSelector('.login-form');if(register)await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function makePage(phone=false){const c=await browser.createBrowserContext();contexts.push(c);const p=await c.newPage();pages.push(p);await p.setViewport(phone?{width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true}:{width:1366,height:950});await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});return p;}
try{
 for(let i=0;i<2;i++){
  const p=await makePage();await login(p,names[i],true);
  if(i===1){const exists=await p.evaluate(async path=>{const c=await mirrorFileContext();await c.files.sync();try{await c.files.read(path);return true}catch(error){if(!String(error.message).includes('File not found'))throw error;return false}},path);assert.equal(exists,false,'Account B must not see Account A file');}
  await p.evaluate(async({path,text})=>{const c=await mirrorFileContext();await c.files.write(path,text);await c.files.sync()},{path,text:documents[i]});
  const content=await p.evaluate(async path=>{const f=await(await serverFileContext()).files.read(path.slice(1));return new TextDecoder().decode(f.data)},path);assert.equal(content,documents[i]);
 }
 for(let i=0;i<2;i++){
  const content=await pages[i].evaluate(async path=>{const f=await(await serverFileContext()).files.read(path.slice(1));return new TextDecoder().decode(f.data)},path);assert.equal(content,documents[i],'Same path must resolve inside each account');
 }
 console.log('PASS same-named files stay isolated and synchronized for two accounts');
 const q=await makePage(true);await login(q,names[0],false);await q.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 await q.evaluate(()=>[...surfaces.values()][0].launch('browser'));await q.waitForFunction(()=>[...([...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled),{timeout:180000});
 await q.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...r.querySelectorAll('button')].find(b=>b.textContent==='Open from My files').click()});
 await q.waitForSelector('[aria-label="Choose file browser-isolation-test.html"]',{timeout:30000});await q.click('[aria-label="Choose file browser-isolation-test.html"]');
 await q.waitForFunction(()=>{const c=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('canvas');if(!c)return false;const d=c.getContext('2d').getImageData(10,10,1,1).data;return d[0]===22&&d[1]===173&&d[2]===91},{timeout:90000});
 const after=await q.evaluate(async path=>{const c=await mirrorFileContext(),f=await c.files.read(path),remote=await(await serverFileContext()).files.read(path.slice(1));return {text:new TextDecoder().decode(f.data),same:f.sha256===remote.sha256}},path);assert.equal(after.text,documents[0]);assert.equal(after.same,true);
 console.log('PASS fresh phone-sized session opens Account A HTML without changing its browser or server copy');
} finally {
 for(let i=0;i<2;i++)if(pages[i])await pages[i].evaluate(async path=>{try{const c=await mirrorFileContext(),f=await c.files.read(path);await c.files.remove(path,f.version);await c.files.sync()}catch{}},path).catch(()=>{});
 for(const c of contexts)await c.close();await browser.disconnect();
}
