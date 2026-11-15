import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {writeFile,unlink} from 'node:fs/promises';
import os from 'node:os';import path from 'node:path';
import {installDesktopDialogAutoAnswer,setDesktopDialogAutoAnswer,setDesktopDialogPromptValue} from './helpers/desktop-dialogs.mjs';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18180/';
const fixture=path.join(os.homedir(),`.codi-browser-download-${process.pid}.html`);
const payload='authenticated-cookie-download-'+'x'.repeat(65566-'authenticated-cookie-download-'.length);
const html=`<!doctype html><meta charset="utf-8"><a href="data:application/octet-stream,${encodeURIComponent(payload)}" download="cookie-result.bin">Download test</a>`;
const nativeDialogs=[];
page.on('dialog',async dialog=>{nativeDialogs.push(dialog.type());await dialog.dismiss();});
if(!['127.0.0.1','localhost','[::1]'].includes(new URL(base).hostname))throw Error('This fixture requires an isolated loopback desktop.');
async function clickLink(index){await new Promise(r=>setTimeout(r,500));const r=await page.evaluate(()=>{const e=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas').getBoundingClientRect();return {x:e.x,y:e.y}});await (process.env.CODI_PHONE==='1'?page.touchscreen.tap(r.x+80,r.y+index*80+15):page.mouse.click(r.x+80,r.y+index*80+15))}
async function rows(count){await page.waitForFunction(n=>[...[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelectorAll('.download-row')||[]].filter(r=>[...r.querySelectorAll('button')].some(b=>b.textContent==='Save to My files')).length===n,{timeout:30000},count)}
async function rowButton(index,label){await page.evaluate((i,text)=>{const row=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelectorAll('.download-row')[i];[...row.querySelectorAll('button')].find(b=>b.textContent===text).click()},index,label)}
async function folder(name=null){await page.waitForSelector('.codi-file-picker');if(name){await page.waitForSelector('[aria-label="Open folder '+name+'"]');await page.click('[aria-label="Open folder '+name+'"]');await page.waitForFunction(n=>document.querySelector('.codi-picker-location')?.textContent==='My files: /'+n,{},name)}await page.waitForFunction(()=>[...document.querySelectorAll('.codi-picker-bar button')].some(b=>b.textContent==='Use this folder'&&!b.disabled));await page.evaluate(()=>[...document.querySelectorAll('.codi-picker-bar button')].find(b=>b.textContent==='Use this folder').click())}
async function ready(){await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.info')?.hidden===true,{timeout:180000})}
async function failure(text){await page.waitForFunction(expected=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent.toLowerCase().includes(expected.toLowerCase()),{timeout:30000},text)}
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true});else if(process.env.CODI_TEST_4K==='1')await page.setViewport({width:3840,height:2160});else await page.setViewport({width:1366,height:900});
 await installDesktopDialogAutoAnswer(page,'cancel');
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]','download'+Date.now().toString().slice(-9));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(async()=>{await(await mirrorFileContext()).files.mkdir('/Course');[...surfaces.values()][0].launch('browser')});await ready();
 await writeFile(fixture,html);
 const picker=await page.evaluateHandle(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('input[type=file]'));
 await picker.asElement().uploadFile(fixture);
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Page loaded.',{timeout:30000});
 if(process.env.CODI_TEST_SCREENSHOT)await page.screenshot({path:process.env.CODI_TEST_SCREENSHOT});
 await clickLink(0);await rows(1);assert.equal(await page.evaluate(()=>{const e=new Event('beforeunload',{cancelable:true});window.dispatchEvent(e);return e.defaultPrevented}),true,'Unsaved downloads protect against accidental reload');
 assert.equal(await page.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/cookie-result.bin');return true}catch{return false}}),false,'No account file exists before explicit save');
 await rowButton(0,'Save to My files');await rows(1);
 await setDesktopDialogPromptValue(page,'cookie-result.bin');await setDesktopDialogAutoAnswer(page,'accept');await rowButton(0,'Save to My files');await folder('Course');await rows(0);assert.equal(await page.evaluate(()=>{const e=new Event('beforeunload',{cancelable:true});window.dispatchEvent(e);return e.defaultPrevented}),false,'Saving removes the unload guard');
 const saved=await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();return Array.from((await(await serverFileContext()).files.read('Course/cookie-result.bin')).data)});
 assert.equal(saved.length,65566);assert.equal(new TextDecoder().decode(Uint8Array.from(saved.slice(0,30))),'authenticated-cookie-download-');
 await clickLink(0);await rows(1);await setDesktopDialogPromptValue(page,'cookie-result.bin');await setDesktopDialogAutoAnswer(page,'accept');await rowButton(0,'Save to My files');await page.waitForSelector('.codi-file-picker');await setDesktopDialogAutoAnswer(page,'cancel');await folder('Course');await rows(1);
 assert.deepEqual(await page.evaluate(async()=>Array.from((await(await mirrorFileContext()).files.read('/Course/cookie-result.bin')).data)),saved,'Declining replacement preserves the existing file');
 await setDesktopDialogPromptValue(page,'cookie-result-2.bin');await setDesktopDialogAutoAnswer(page,'accept');await rowButton(0,'Save to My files');await folder();await rows(0);

 await clickLink(0);await rows(1);await setDesktopDialogPromptValue(page,'cookie-result.bin');await setDesktopDialogAutoAnswer(page,'accept');await rowButton(0,'Save to My files');await page.waitForSelector('.codi-file-picker');await setDesktopDialogAutoAnswer(page,'accept');const before=await page.evaluate(async()=>(await(await mirrorFileContext()).files.stat('/Course/cookie-result.bin')).version);await folder('Course');await rows(0);assert.notEqual(await page.evaluate(async()=>(await(await mirrorFileContext()).files.stat('/Course/cookie-result.bin')).version),before,'confirmed replacement writes a new version');
 await clickLink(0);await rows(1);await page.evaluate(async()=>{const c=await mirrorFileContext(),write=c.files.write.bind(c.files);c.files.write=async(path,data,expected)=>{c.files.write=write;if(path==='/Course/cookie-result.bin'){const latest=await c.files.stat(path);await write(path,new TextEncoder().encode('newer file'),latest.version)}return write(path,data,expected)}});await setDesktopDialogPromptValue(page,'cookie-result.bin');await setDesktopDialogAutoAnswer(page,'accept');await rowButton(0,'Save to My files');await page.waitForSelector('.codi-file-picker');await setDesktopDialogAutoAnswer(page,'accept');await folder('Course');await failure('file changed');await rows(1);assert.equal(await page.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Course/cookie-result.bin')).data)),'newer file','a concurrent edit survives the stale download');
 await setDesktopDialogAutoAnswer(page,'cancel');
 // Locate the reset control by its visible label because it is intentionally
 // inside the Browser application's shadow root.
 await page.evaluate(()=>{const root=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...root.querySelectorAll('button')].find(b=>b.textContent==='Reset engine').click()});
 await page.waitForFunction(()=>!document.querySelector('.codi-confirm-dialog[open]'));
 await rows(1);assert.equal(await page.evaluate(()=>{const e=new Event('beforeunload',{cancelable:true});window.dispatchEvent(e);return e.defaultPrevented}),true,'cancelling reset keeps unsaved downloads');
 await setDesktopDialogAutoAnswer(page,'accept');await page.evaluate(()=>{const root=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...root.querySelectorAll('button')].find(b=>b.textContent==='Reset engine').click()});
 await ready();await rows(0);
 assert.deepEqual(nativeDialogs,[],'Browser save and reset actions use desktop dialogs, not browser-native popups');
 console.log('PASS actual Browser clicked download folder selection, themed dialogs, cancellation, confirmed replacement and account sync');
}catch(error){console.error('DIAGNOSTIC',await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot;return {status:r?.querySelector('.status')?.textContent,downloads:r?.querySelector('.downloads')?.textContent}}).catch(()=>null));throw error}
finally{await context.close();await browser.disconnect();await unlink(fixture).catch(()=>{})}
