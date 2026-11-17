/** Isolated headed Chromium: open the real PDF print preview and cancel without printing. */
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
const origin=process.env.WEBOS_VIEWER_ORIGIN,output=process.env.WEBOS_TEST_OUTPUT,engine=process.env.WEBOS_ENGINE_COMMIT;
assert(origin&&path.isAbsolute(output)&&engine);await mkdir(output,{mode:0o700});
const credentials={username:'wcout'+randomBytes(6).toString('hex'),password:randomBytes(12).toString('hex')};
await writeFile(path.join(output,'credentials.json'),JSON.stringify(credentials),{mode:0o600});
const checks=[],errors=[];let browser,page,frame,id,interceptor;
async function button(label,parent=''){for(const n of await page.$$(parent+'button'))if(await n.evaluate((n,l)=>(n.querySelector('.row-text')||n).textContent.trim()===l,label)){await n.click();return;}throw Error('Missing '+label);}
async function command(command,params={}){return frame.evaluate(async(command,params)=>{const s=await window.wordcraft.uiInspect();return window.wordcraft.request('engine.execute',{command,params,doc:s.document});},command,params);}
async function ui(){return frame.evaluate(()=>window.wordcraft.uiInspect());}
async function settled(){await frame.waitForFunction(async()=>!(await window.wordcraft.uiInspect()).pendingSaves);}
async function backstage(value,page='saveAs'){await command('ui.backstage',{value,page});}
async function editor(){await frame.waitForFunction(async()=>!(await window.wordcraft.uiInspect()).ui.backstage);}
async function state(){return page.evaluate(id=>document.querySelector('.window[data-window="'+id+'"]').appView.inspect(),id);}
async function check(name,fn){await fn();checks.push(name);console.log(JSON.stringify({check:name,status:'PASS'}));}
async function intercept(fn){interceptor=fn;await page.setRequestInterception(true);page.on('request',interceptor);}
async function restoreRequests(){if(interceptor){page.off('request',interceptor);interceptor=null;await page.setRequestInterception(false);}}
try{
 browser=await puppeteer.launch({executablePath:'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:false,args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],userDataDir:path.join(output,'browser-profile')});page=await browser.newPage();await page.setViewport({width:1500,height:1000});page.setDefaultTimeout(60000);page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin,{waitUntil:'networkidle0'});assert.equal(await page.evaluate(async()=>{const r=await fetch('/viewer-build.json');return(await r.json()).engine.sourceCommit;}),engine);
 await page.waitForSelector('.login-gate');await page.click('.login-toggle');await page.type('[aria-label="Username"]',credentials.username);await page.type('[aria-label="Password"]',credentials.password);await page.type('[aria-label="Confirm password"]',credentials.password);await button('Register','.login-gate ');await page.waitForFunction(()=>!!window.desktopLab?.session&&!document.querySelector('.login-gate'));
 await page.click('.app-menu-button');await button('Office','.menu-pane ');await button('WordCraft','.menu-pane ');await page.waitForSelector('.webos-wordcraft');id=await page.$eval('.window:has(.webos-wordcraft)',n=>n.dataset.window);await page.waitForFunction(async id=>{try{return(await document.querySelector('.window[data-window="'+id+'"]').appView.inspect()).phase==='ready';}catch{return false;}},{timeout:120000},id);frame=await(await page.$('iframe[title="WordCraft document"]')).contentFrame();await command('text.insert',{text:'File actions preserve this document.'});

 await check('Desktop CSP is unchanged; only WordCraft allows its generated PDF frame',async()=>{const policies=await page.evaluate(async()=>{const root=await fetch('/'),word=await fetch('/wordcraft/index.html');return {root:root.headers.get('Content-Security-Policy'),word:word.headers.get('Content-Security-Policy')};});assert(policies.root.includes("frame-src 'self';"));assert.equal(policies.word,policies.root.replace("frame-src 'self';", "frame-src 'self' blob:;"));assert(policies.word.includes("object-src 'none'"));});
 for(let attempt=0;attempt<2;attempt++)await check('Real browser print preview opens and cancellation returns to the document, attempt '+(attempt+1),async()=>{
  await command('file.print');assert.equal((await ui()).ui.backstage,true);await command('ui.print');
  const target=await browser.waitForTarget(t=>t.url()==='chrome://print/',{timeout:30000});const preview=await target.createCDPSession();await preview.send('Runtime.enable');const evaluate=async fn=>{const r=await preview.send('Runtime.evaluate',{expression:'('+fn.toString()+')()',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;};
  let previewReady=false;for(let n=0;n<150;n++){previewReady=await evaluate(()=>{if(typeof document==='undefined')return false;const app=document.querySelector('print-preview-app'),area=app?.shadowRoot?.querySelector('print-preview-preview-area');return !!area;});if(previewReady)break;await new Promise(r=>setTimeout(r,200));}assert(previewReady,'The real browser preview UI loaded');
  await browser.waitForTarget(t=>t.url().startsWith('chrome-untrusted://print/')&&t.url().endsWith('/print.pdf'),{timeout:30000});
  const shot=await preview.send('Page.captureScreenshot',{format:'png'});await writeFile(path.join(output,'print-preview-'+attempt+'.png'),Buffer.from(shot.data,'base64'));
  const closed=new Promise((resolve,reject)=>{const timer=setTimeout(()=>{browser.off('targetdestroyed',done);reject(Error('Print preview did not close'));},10000);function done(t){if(t===target){clearTimeout(timer);browser.off('targetdestroyed',done);resolve();}}browser.on('targetdestroyed',done);});
  let cancelled=false;try{cancelled=await evaluate(()=>{const roots=[document];while(roots.length){const root=roots.shift();for(const n of root.querySelectorAll('*')){if(n.shadowRoot)roots.push(n.shadowRoot);if((n.localName==='cr-button'||n.localName==='button')&&n.textContent.trim()==='Cancel'&&!n.disabled){n.click();return true;}}}return false;});}catch(error){if(!/Target closed/.test(error.message))throw error;await closed;cancelled=true;}assert(cancelled,'Cancel the isolated browser preview; never submit a print job');
  await closed;assert(browser.connected,'Only the preview closes; the test browser stays connected');await editor();assert.equal((await ui()).dirty,true,'Printing/cancelling cannot claim an account save');assert.equal(await frame.$$eval('#wordcraft-print-frame',n=>n.length),1,'Only one retained PDF frame');assert.equal((await command('ui.printSettings')).status,'submitted');
 });
 assert.deepEqual(errors,[]);await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,engine,pageErrors:errors,physicalPrinting:'No print job submitted; preview cancelled by test'},null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length}));
}catch(error){await writeFile(path.join(output,'failure.json'),JSON.stringify({error:error.message,checks,pageErrors:errors},null,2)+'\n');if(page)await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});throw error;}finally{await browser?.close();}
