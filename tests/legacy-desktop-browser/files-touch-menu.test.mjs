import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {writeFile,unlink} from 'node:fs/promises';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage(),file='/tmp/codi-files-touch-upload-fixture.txt';
try {
 await writeFile(file,'touch upload');
 await page.setViewport({width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 await page.goto('http://127.0.0.1:18205/fixture.html');
 const trigger='[aria-label="New or upload"]';await page.waitForSelector(trigger,{visible:true});await page.waitForFunction(s=>!document.querySelector(s).disabled,{},trigger);
 const size=await page.$eval(trigger,e=>e.getBoundingClientRect().height);assert.ok(size>=44,'Touch target should be at least 44px tall');
 await page.tap(trigger);await page.waitForSelector('[role=menu]');
 await page.tap(trigger);await page.waitForSelector('[role=menu]',{hidden:true});
 let answer='Notes';page.on('dialog',d=>d.accept(answer));
 await page.tap(trigger);await page.evaluate(()=>[...document.querySelectorAll('[role=menuitem]')].find(e=>e.textContent==='New folder').click());
 await page.waitForFunction(()=>window.testWrites.some(x=>x[0]==='mkdir'&&x[1]==='/Notes'));
 answer='notes.txt';await page.tap(trigger);await page.evaluate(()=>[...document.querySelectorAll('[role=menuitem]')].find(e=>e.textContent==='New file').click());
 await page.waitForFunction(()=>window.testWrites.some(x=>x[0]==='write'&&x[1]==='/notes.txt'));
 await page.tap(trigger);const chooserPromise=page.waitForFileChooser();await page.evaluate(()=>[...document.querySelectorAll('[role=menuitem]')].find(e=>e.textContent==='Upload').click());const chooser=await chooserPromise;await chooser.accept([file]);
 await page.waitForFunction(()=>window.testWrites.some(x=>x[0]==='write'&&x[1]==='/codi-files-touch-upload-fixture.txt'));
 await page.evaluate(()=>window.disposeFixture());assert.equal(await page.$('.codi-files-touch-menu'),null);
 await page.setViewport({width:1366,height:900,deviceScaleFactor:1,isMobile:false,hasTouch:false});await page.reload();await page.waitForSelector(trigger);const desktop=await page.evaluate(s=>({fine:matchMedia('(hover:hover) and (pointer:fine)').matches,display:getComputedStyle(document.querySelector(s)).display}),trigger);if(desktop.fine)assert.equal(desktop.display,'none','Fine-pointer desktop keeps right-click workflow');
 console.log('PASS touch create, folder, upload, toggle and cleanup; desktop fine-pointer rule checked');
} finally {await unlink(file).catch(()=>{});await context.close();await browser.disconnect()}
