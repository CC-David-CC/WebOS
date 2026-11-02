import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
import {randomBytes} from 'node:crypto';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19795/';
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(base))throw Error('An isolated loopback preview is required');
const require=createRequire(resolve(process.env.PUPPETEER_CORE_PATH||'.','package.json'));
const puppeteer=require('puppeteer-core');
const browser=await puppeteer.launch({executablePath:process.env.CODI_CHROMIUM,args:['--no-sandbox','--disable-dev-shm-usage'],headless:true});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>{errors.push('Unexpected native dialog');void d.dismiss()});
try{
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]','heldtext'+randomBytes(5).toString('hex'));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>surfaces.get('Desktop').launch('text'));
 await page.waitForFunction(()=>{const win=document.querySelector('[data-window]:has(.codi-text-editor)');return !!win?.appView?.lifecycle&&!win.appView.lifecycle.snapshot().pending&&!!window.codiDesktopCommands?.list().find(x=>x.appId==='text')},{timeout:60000});
 const id=await page.evaluate(()=>window.codiDesktopCommands.list().find(x=>x.appId==='text').windowId);
 const call=(command,args)=>page.evaluate(({id,command,args})=>window.codiDesktopCommands.execute({windowId:id,command,args}),{id,command,args});
 const initial=await call('inspect',{});const initialDom=await page.$eval('.cm-content',e=>e.innerText);await page.evaluate(()=>{window.oldFetch=fetch;window.fetch=(url,...args)=>String(url).includes('/logout')?new Promise((_,reject)=>{window.rejectLogout=()=>reject(new TypeError('injected offline logout'))}):oldFetch(url,...args);void endSession()});
 await page.waitForFunction(()=>typeof window.rejectLogout==='function',{timeout:30000});
 assert.equal(await page.evaluate(()=>document.querySelector('[data-window]:has(.codi-text-editor)').appView.lifecycle.snapshot().quiesced),true);
 assert.equal(await page.evaluate(()=>surfaces.get('Desktop').root.inert),true);
 let rejected=false;try{await call('replace-range',{from:0,to:0,text:'should not be applied',revision:initial.revision})}catch{rejected=true}assert.equal(rejected,true,'agent edit must be blocked while logout is pending');
 await page.click('.cm-content');await page.keyboard.type('should not be typed');assert.equal(await page.$eval('.cm-content',e=>e.innerText),initialDom,'inert desktop blocks user keyboard edits');
 await page.evaluate(()=>window.rejectLogout());await page.waitForFunction(()=>document.body.innerText.includes('Could not confirm sign-out'));
 assert.equal(await page.evaluate(()=>document.querySelector('[data-window]:has(.codi-text-editor)').appView.lifecycle.snapshot().quiesced),false);
 assert.equal(await page.evaluate(()=>surfaces.get('Desktop').root.inert),false);
 const after=await call('inspect',{});await call('replace-range',{from:0,to:0,text:'after failure',revision:after.revision});assert.match((await call('inspect',{})).text,/after failure/);
 assert.deepEqual(errors,[]);console.log('PASS real Text quiescence/inertness during held logout and recovery after rejected logout');
}finally{await context.close();await browser.close()}
