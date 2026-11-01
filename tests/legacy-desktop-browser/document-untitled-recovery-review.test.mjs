import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage();
const user='docunt'+Date.now().toString().slice(-9),errors=[];
page.on('pageerror',error=>errors.push(error.message));
const action=label=>page.evaluate(label=>[...document.querySelectorAll('.document-filebar button')].find(button=>button.textContent===label).click(),label);
try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18887/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
 console.log('TEST ACCOUNT',user,await page.evaluate(()=>signedInSubject()));
 await page.evaluate(async()=>{const c=await mirrorFileContext(),f=c.files;await f.write('/Untitled.doc',JSON.stringify({format:'codi-document/1',document:{type:'doc',content:[{type:'paragraph',content:[{type:'text',text:'Original report'}]}]}}),null);await f.sync();const read=f.read.bind(f);f.read=async path=>{if(path==='/Untitled.doc'){f.read=read;throw Error('Injected temporary read failure')}return read(path)};openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Untitled.doc')});
 await page.waitForFunction(()=>document.querySelector('.document-editor-content .app-status')?.textContent.includes('Injected temporary read failure'),{timeout:30000});
 assert.equal(await page.$eval('[aria-label="Document file path"]',e=>e.value),'/Untitled-recovery.doc');
 await page.click('.document-editable .tiptap');await page.keyboard.type('Scratch report');await action('Save');await page.waitForFunction(()=>document.querySelector('.document-editor-content .app-status')?.textContent.includes('Saved on this device'),{timeout:30000});
 const saved=await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();const server=await serverFileContext();return Promise.all(['Untitled.doc','Untitled-recovery.doc'].map(async p=>new TextDecoder().decode((await server.files.read(p)).data))) });assert.match(saved[0],/Original report/);assert.doesNotMatch(saved[0],/Scratch report/);assert.match(saved[1],/Scratch report/);
 await page.evaluate(()=>document.querySelector('.document-editor-content').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.document-editor-content'));
 await page.evaluate(async()=>{const c=await mirrorFileContext(),read=c.files.read.bind(c.files);c.files.read=async path=>{if(path==='/Untitled.doc'){c.files.read=read;throw Error('Injected second failure')}return read(path)};openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Untitled.doc')});await page.waitForFunction(()=>document.querySelector('.document-editor-content .app-status')?.textContent.includes('Injected second failure'),{timeout:30000});await action('Retry opening document');await page.waitForFunction(()=>document.querySelector('.document-editable .tiptap')?.textContent.includes('Original report'),{timeout:30000});assert.deepEqual(errors,[]);console.log('PASS separate scratch save, sync, original preservation and retry');
}finally{await context.close();await browser.disconnect()}
