/** Real Text editing through Files and signed server storage. */
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {createInterface} from 'node:readline';
import {randomBytes} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
const root=process.cwd(), output=process.env.WEBOS_TEST_OUTPUT && path.resolve(process.env.WEBOS_TEST_OUTPUT), python=process.env.WEBOS_TEST_PYTHON;
assert(output && python && !output.startsWith(root+path.sep)); await mkdir(output,{mode:0o700});
const publicRoot=path.join(output,'public');const built=spawnSync(process.execPath,['scripts/build_development.mjs',publicRoot],{cwd:root,encoding:'utf8'});assert.equal(built.status,0,built.stderr);
const server=spawn(python,['-u','scripts/run_development.py','--public-root',publicRoot,'--private-root',path.join(output,'state'),'--port','0'],{stdio:['ignore','pipe','pipe']});const serverErrors=[];server.stderr.on('data',v=>serverErrors.push(v));let browser;const errors=[],report={status:'FAIL',scope:'Actual Text/CodeMirror, Files, signed Accounts/Storage; local test accounts only'};
try {
 const origin=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Server timeout')),15000);createInterface({input:server.stdout}).once('line',line=>{clearTimeout(timer);resolve(JSON.parse(line).origin);});server.once('exit',()=>reject(Error('Server stopped')));});
 browser=await puppeteer.launch({executablePath:'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const username='text'+randomBytes(6).toString('hex'),password=randomBytes(18).toString('base64url');
 async function context(){const c=await browser.createBrowserContext(),p=await c.newPage();await p.setViewport({width:1500,height:1050});p.on('pageerror',e=>errors.push(e.message));await p.goto(origin,{waitUntil:'networkidle0'});return {c,p};}
 async function signin(p,register=false){await p.waitForSelector('.login-gate[data-phase=ready]');if(register)await p.click('.login-toggle');await p.type('[name=username]',username);await p.type('[name=password]',password);if(register)await p.type('[name=confirmation]',password);await p.click('[type=submit]');await p.waitForSelector('.webos-desktop');}
 async function launchFiles(p){await p.click('[aria-label=Applications]');await p.click('[data-app-id=files]');await p.waitForFunction(()=>document.querySelector('.webos-files-status')?.textContent.includes('Showing account files'));}
 async function focus(p,id){await p.click(`.webos-task[data-window-id="${id}"]`);}
 async function openText(p,name){const task=await p.$('.webos-task');const fileId=await p.$eval('.webos-window[aria-label=Files]',e=>e.dataset.windowId);await focus(p,fileId);const handle=await p.evaluateHandle(name=>[...document.querySelectorAll('.webos-files-browser [title]')].find(e=>e.getAttribute('title')===name),name);assert(handle.asElement(),'Missing Files entry');await handle.asElement().click();await handle.asElement().click();await handle.dispose();await p.waitForFunction(()=>document.querySelector('.webos-window.webos-focused[aria-label=Text]')?.dataset.phase==='ready');return p.$eval('.webos-window.webos-focused[aria-label=Text]',e=>e.dataset.windowId);}
 const selector=id=>`.webos-window[data-window-id="${id}"]`;
 async function button(p,id,text){for(const b of await p.$$(selector(id)+' nav button')){if(await b.evaluate(e=>e.textContent)===text){await b.click();return;}}throw Error('Missing Text button: '+text);}
 async function replace(p,id,value){await focus(p,id);await p.click(selector(id)+' .cm-content');await p.keyboard.down('Control');await p.keyboard.press('KeyA');await p.keyboard.up('Control');await p.keyboard.type(value);}
 async function saved(p,id){await p.waitForFunction(sel=>document.querySelector(sel+' .webos-text-status')?.textContent==='Saved to your account.',{},selector(id));}
 async function text(p,id){return p.$eval(selector(id)+' .cm-content',e=>e.textContent);}
 const first=await context();await signin(first.p,true);await launchFiles(first.p);
 for(const [name,value] of [['alpha.txt','Alpha original'],['beta.txt','Beta original']]){const file=path.join(output,name);await writeFile(file,value);await(await first.p.$('input[type=file]')).uploadFile(file);await first.p.waitForFunction(name=>document.querySelector('.webos-files-status')?.textContent.includes('Saved to your account: '+name),{},name);}
 const alpha=await openText(first.p,'alpha.txt');await replace(first.p,alpha,'Alpha edited');await button(first.p,alpha,'Save');await saved(first.p,alpha);
 const beta=await openText(first.p,'beta.txt');assert.notEqual(alpha,beta);await replace(first.p,beta,'Beta edited');await button(first.p,beta,'Save');await saved(first.p,beta);assert.equal(await text(first.p,alpha),'Alpha edited');
 await focus(first.p,alpha);await button(first.p,alpha,'Save As');await first.p.waitForSelector('.webos-text-dialog input');await first.p.$eval('.webos-text-dialog input',e=>{e.value='';});await first.p.type('.webos-text-dialog input','alpha-copy.txt');await first.p.click('.webos-text-dialog button');await saved(first.p,alpha);await replace(first.p,alpha,'Alpha copy edited');await button(first.p,alpha,'Save');await saved(first.p,alpha);
 await replace(first.p,beta,'Beta unsaved close');await first.p.click(selector(beta)+' [aria-label=Close]');await first.p.waitForSelector('.webos-text-dialog');
 async function dialogChoice(p,label){for(const b of await p.$$('.webos-text-dialog button'))if(await b.evaluate(e=>e.textContent)===label){await b.click();return;}throw Error('Missing dialog choice');}
 await dialogChoice(first.p,'Cancel');assert(await first.p.$(selector(beta)));assert.equal(await text(first.p,beta),'Beta unsaved close');await first.p.click(selector(beta)+' [aria-label=Close]');await first.p.waitForSelector('.webos-text-dialog');await dialogChoice(first.p,'Save');await first.p.waitForFunction(sel=>!document.querySelector(sel),{},selector(beta));
 await first.p.reload({waitUntil:'networkidle0'});await signin(first.p);await launchFiles(first.p);
 for(const [name,expected] of [['alpha.txt','Alpha edited'],['beta.txt','Beta unsaved close'],['alpha-copy.txt','Alpha copy edited']]){const id=await openText(first.p,name);assert.equal(await text(first.p,id),expected);await first.p.click(selector(id)+' [aria-label=Close]');await first.p.waitForFunction(sel=>!document.querySelector(sel),{},selector(id));}
 const second=await context();await signin(second.p);await launchFiles(second.p);const copy=await openText(second.p,'alpha-copy.txt');assert.equal(await text(second.p,copy),'Alpha copy edited');
 await second.p.screenshot({path:path.join(output,'text-account-document.png')});assert.deepEqual(errors,[]);Object.assign(report,{status:'PASS',twoIndependentDocuments:true,filesOpenEditSaveCloseReopen:true,saveAsPreservesOriginal:true,cancelUnsavedClose:true,saveOnClose:true,reloadReopensAllThree:true,secondCleanContextRetrievesSavedDocument:true,pageErrors:0});
}catch(error){report.error={name:error.name,message:error.message};if(browser){let i=0;for(const p of await browser.pages())await p.screenshot({path:path.join(output,'failure-'+i+++'.png')}).catch(()=>{});}throw error;}
finally{await browser?.close();server.kill('SIGTERM');await new Promise(resolve=>{if(server.exitCode!==null||server.signalCode)resolve();else server.once('exit',resolve);});await writeFile(path.join(output,'result.json'),JSON.stringify(report,null,2)+'\n');await writeFile(path.join(output,'server-errors.log'),Buffer.concat(serverErrors));}
console.log(JSON.stringify(report));
