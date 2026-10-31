import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'});
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18211/';
async function run(phone){
 const context=await browser.createBrowserContext(),p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 const user=(phone?'docphone':'docdesk')+Date.now().toString().slice(-9);
 const click=async label=>p.evaluate(label=>{const b=[...document.querySelectorAll('.document-file-actions button')].find(x=>x.textContent===label);if(!b)throw Error('Missing '+label);b.click()},label);
 try{
  await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:1}:{width:1920,height:1080});
  await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.mkdir('/Notes');await c.files.write('/broken.doc','not a document',null);await c.files.sync();surfaces.get('Desktop').launch('document-editor')});
  await p.waitForSelector('.document-editable .tiptap',{visible:true,timeout:30000});await p.click('.document-editable .tiptap');await p.keyboard.type('My report');
  await click('Choose save folder');await p.waitForSelector('[aria-label="Open folder Notes"]');await p.click('[aria-label="Open folder Notes"]');await p.waitForFunction(()=>document.querySelector('.codi-picker-location')?.textContent==='My files: /Notes');await p.waitForFunction(()=>[...document.querySelectorAll('.codi-picker-bar button')].some(b=>b.textContent==='Use this folder'&&!b.disabled));await p.evaluate(()=>[...document.querySelectorAll('.codi-picker-bar button')].find(b=>b.textContent==='Use this folder').click());
  await p.waitForFunction(()=>document.querySelector('[aria-label="Document file path"]')?.value==='/Notes/Untitled.doc');await click('Save');await p.waitForFunction(async()=>{try{return (await(await mirrorFileContext()).files.read('/Notes/Untitled.doc')).status==='synced'}catch{return false}},{timeout:45000});
  await p.click('.document-editable .tiptap');await p.keyboard.press('End');await p.keyboard.type(' draft');p.once('dialog',d=>d.accept());await click('Open from My files');await p.waitForSelector('[aria-label="Choose file broken.doc"]');await p.click('[aria-label="Choose file broken.doc"]');await p.waitForFunction(()=>document.querySelector('.document-editor-content .app-status')?.textContent.includes('Could not open document:'));
  assert.match(await p.$eval('.document-editable .tiptap',e=>e.innerText),/My report draft/);assert.equal(await p.$eval('[aria-label="Document file path"]',e=>e.value),'/Notes/Untitled.doc');assert.equal(await p.$eval('.document-editable .tiptap',e=>e.getAttribute('contenteditable')),'true');
  await click('Save');await p.waitForFunction(async()=>{try{const f=await(await mirrorFileContext()).files.read('/Notes/Untitled.doc');return f.status==='synced'&&new TextDecoder().decode(f.data).includes('My report draft')}catch{return false}},{timeout:45000});
  const fresh=await browser.createBrowserContext(),q=await fresh.newPage();try{await q.goto(base);await q.waitForSelector('.login-gate');await q.type('[aria-label=Username]',user);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});await q.waitForFunction(async()=>{try{return new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Notes/Untitled.doc')).data).includes('My report draft')}catch{return false}},{timeout:30000});}finally{await fresh.close()}
  assert.deepEqual(errors,[]);console.log('PASS',phone?'phone':'desktop','save folder, failed open preserves draft, and fresh session recovery');
 }finally{await context.close()}
}
try{await run(false);await run(true)}finally{await browser.disconnect()}
