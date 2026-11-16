/** Real CodeMirror/IndexedDB recovery with disposable signed account files. */
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
const origin=process.env.WEBOS_VIEWER_ORIGIN,output=process.env.WEBOS_TEST_OUTPUT;
assert(origin&&path.isAbsolute(output),'Explicit origin and new private output required.');await mkdir(output,{mode:0o700});
const makeUser=()=>({username:'draft'+randomBytes(6).toString('hex'),password:randomBytes(12).toString('hex')});
const accountA=makeUser(),accountB=makeUser();await writeFile(path.join(output,'credentials.json'),JSON.stringify({accountA,accountB}),{mode:0o600});
const checks=[],errors=[],consoleErrors=[],faultConsoleErrors=[],dialogs=[];let browser,page,otherContext,decision='dismiss';
const scope=id=>'.window[data-window="'+id+'"] ';
async function button(p,label,parent='') {for(const n of await p.$$(parent+'button'))if(await n.evaluate((n,label)=>(n.querySelector('.row-text')||n).textContent.trim()===label,label)){await n.click();return;}throw Error('Button unavailable: '+label);}
async function login(p,account,register=false){await p.waitForSelector('.login-gate');if(register)await p.click('.login-toggle');await p.type('[aria-label="Username"]',account.username);await p.type('[aria-label="Password"]',account.password);if(register)await p.type('[aria-label="Confirm password"]',account.password);await button(p,register?'Register':'Sign in','.login-gate ');await p.waitForFunction(()=>!!window.desktopLab?.session&&!document.querySelector('.login-gate'));}
async function launch(p,group,label){await p.click('.app-menu-button');await button(p,group,'.menu-pane ');await button(p,label,'.menu-pane ');}
async function viewStates(p=page){return p.evaluate(async()=>{const out=[];for(const win of document.querySelectorAll('.window:has(.webos-text)'))out.push({id:win.dataset.window,...await win.appView.inspect(),text:win.querySelector('.cm-content')?.textContent});return out;});}
async function focus(id){await page.evaluate(id=>{for(const d of window.desktopLab.surfaces.values()){const w=d.windows.find(w=>String(w.id)===id);if(w){d.activateWindow(w);return;}}},id);}
async function edit(id,text){await page.waitForFunction(async id=>{const w=document.querySelector('.window[data-window="'+id+'"]');return w?.appView&&(await w.appView.inspect()).loaded&&w.querySelector('.cm-content')?.contentEditable==='true';},{},id);await focus(id);await page.click(scope(id)+'.cm-content');await page.keyboard.down('Control');await page.keyboard.press('a');await page.keyboard.up('Control');await page.keyboard.type(text);assert.equal(await page.$eval(scope(id)+'.cm-content',n=>n.textContent),text);}
async function stored(id){await page.waitForFunction(async id=>{const v=document.querySelector('.window[data-window="'+id+'"]')?.appView;if(!v)return false;const s=await v.inspect();return s.loaded&&s.dirty&&s.recovery==='stored';},{timeout:20000},id);}
async function file(p,operation,args={}){return p.evaluate(async({operation,args})=>{const win=[...document.querySelectorAll('.window')].find(n=>n.querySelector('.webos-files'));if(operation==='import')args.blob=new Blob([args.contents]);return win.appView.execute(operation,args);},{operation,args});}
async function files(p=page){if(await p.$('.webos-files'))return;await launch(p,'System Tools','Files');await p.waitForFunction(()=>document.querySelector('.webos-files-status')?.textContent.includes('Showing account files'));}
async function newText(){const before=new Set((await viewStates()).map(s=>s.id));await launch(page,'Office','Text Editor (CodeMirror 6)');await page.waitForFunction(n=>document.querySelectorAll('.webos-text').length>n,{},before.size);const s=(await viewStates()).find(s=>!before.has(s.id));await page.waitForFunction(async id=>(await document.querySelector('.window[data-window="'+id+'"]').appView.inspect()).loaded,{},s.id);return s.id;}
async function saveAs(id,name){await focus(id);await button(page,'Save As',scope(id)+'.webos-text nav ');await page.waitForSelector('.webos-text-dialog[data-kind=path] input');await page.click('.webos-text-dialog input',{count:3});await page.keyboard.press('Backspace');await page.type('.webos-text-dialog input',name);await button(page,'Save','.webos-text-dialog ');await page.waitForFunction(async({id,name})=>{const s=await document.querySelector('.window[data-window="'+id+'"]').appView.inspect();return s.path===name&&!s.busy;},{}, {id,name});}
async function reload({warning=true,accept=true}={}){
 const count=dialogs.length;decision=accept?'accept':'dismiss';const cdp=await page.createCDPSession();
 if(accept){await Promise.all([page.waitForNavigation({waitUntil:'networkidle0'}),cdp.send('Page.reload')]);}
 else {await cdp.send('Page.reload');await page.waitForFunction(()=>!!window.desktopLab?.session);await new Promise(r=>setTimeout(r,150));}
 await cdp.detach();assert.equal(dialogs.length-count,warning?1:0);if(warning)assert.equal(dialogs.at(-1),'beforeunload');decision='dismiss';
}
async function recoverAll(expected){for(let i=0;i<expected;i++){
 await page.waitForFunction(()=>document.activeElement?.closest('dialog')?.dataset.kind==='recovery');
 const dialog=await page.evaluateHandle(()=>document.activeElement.closest('dialog'));const buttons=await dialog.$$('button');
 for(const n of buttons)if(await n.evaluate(n=>n.textContent==='Recover draft')){await n.click();break;}
 await dialog.dispose();
 }await page.waitForFunction(async()=>{for(const w of document.querySelectorAll('.window:has(.webos-text)')){const s=await w.appView.inspect();if(!s.loaded||s.recovery==='writing')return false;}return true;});}
async function closeChoice(choice){await page.waitForFunction(()=>document.activeElement?.closest('dialog')?.dataset.kind==='close');const dialog=await page.evaluateHandle(()=>document.activeElement.closest('dialog'));for(const n of await dialog.$$('button'))if(await n.evaluate((n,c)=>n.textContent===c,choice)){await n.click();break;}await dialog.dispose();}
async function check(name,action){try{await action();checks.push({name,status:'PASS'});}catch(e){checks.push({name,status:'FAIL',error:e.message,states:await viewStates().catch(()=>null)});throw e;}}
let untitled,named;
try{
 browser=await puppeteer.launch({executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--disable-dev-shm-usage'],userDataDir:path.join(output,'browser-profile')});page=await browser.newPage();page.setDefaultTimeout(20000);await page.setViewport({width:1440,height:1000});
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});page.on('dialog',async d=>{dialogs.push(d.type());await(decision==='accept'?d.accept():d.dismiss());});
 await page.goto(origin,{waitUntil:'networkidle0'});await login(page,accountA,true);
 await check('Clean Text allows browser reload without an unsaved-work warning',async()=>{untitled=await newText();await reload({warning:false});await login(page,accountA);await page.waitForSelector('.webos-text');untitled=(await viewStates())[0].id;});
 await check('Cancelled reload preserves two real CodeMirror buffers, including an untitled draft',async()=>{
  await files();await file(page,'import',{name:'Base.txt',contents:'Server baseline'});await file(page,'open',{path:'Base.txt'});await page.waitForFunction(()=>document.querySelectorAll('.webos-text').length===2);named=(await viewStates()).find(s=>s.id!==untitled).id;
  await edit(untitled,'Untitled local recovery');await edit(named,'Named local recovery');await stored(untitled);await stored(named);
  const before=await viewStates();await reload({accept:false});assert.deepEqual((await viewStates()).map(s=>[s.documentId,s.text]),before.map(s=>[s.documentId,s.text]));
 });
 await check('Accepted reload and sign-in offer and restore both unsaved drafts without changing account bytes',async()=>{
  await reload();await login(page,accountA);await recoverAll(2);const s=await viewStates();assert.equal(s.length,2);assert.deepEqual(s.map(x=>x.text).sort(),['Named local recovery','Untitled local recovery']);assert(s.every(x=>x.dirty));untitled=s.find(x=>!x.path).id;named=s.find(x=>x.path==='Base.txt').id;
  await files();const original=await file(page,'snapshot',{path:'Base.txt'});const data=await file(page,'download',{path:'Base.txt',expectedRevision:original.sha256});assert.equal(new TextDecoder().decode(new Uint8Array(Object.values(data.data))),'Server baseline');
 });
 await check('Changed server revision keeps recovered text and requires Save As rather than overwriting',async()=>{
  otherContext=await browser.createBrowserContext();const other=await otherContext.newPage();await other.goto(origin,{waitUntil:'networkidle0'});await login(other,accountA);await files(other);const v=await file(other,'snapshot',{path:'Base.txt'});await file(other,'remove',{path:'Base.txt',expectedRevision:v.sha256});await file(other,'import',{name:'Base.txt',contents:'Changed in another browser'});await otherContext.close();otherContext=null;
  await reload();await login(page,accountA);await recoverAll(2);const s=await viewStates();named=s.find(x=>x.path==='Base.txt').id;untitled=s.find(x=>!x.path).id;assert.equal(s.find(x=>x.id===named).needsCopy,true);assert.equal(await page.$eval(scope(named)+'.webos-text nav button',n=>n.disabled),true);
  await saveAs(named,'Recovered-copy.txt');await files();const snap=await file(page,'snapshot',{path:'Base.txt'});const changed=await file(page,'download',{path:'Base.txt',expectedRevision:snap.sha256});assert.equal(new TextDecoder().decode(new Uint8Array(Object.values(changed.data))),'Changed in another browser');
 });
 await check('Typing during a delayed signed save keeps newer edits dirty and checkpoints them against the acknowledged revision',async()=>{
  await edit(untitled,'Snapshot sent to server');await stored(untitled);
  let release,entered;const intercepted=new Promise(r=>{entered=r;});let gate=true;
  await page.setRequestInterception(true);const intercept=request=>{if(gate&&new URL(request.url()).pathname.startsWith('/gateway/')&&request.method()==='POST'){gate=false;release=()=>request.continue();entered();}else void request.continue();};page.on('request',intercept);
  await focus(untitled);await button(page,'Save As',scope(untitled)+'.webos-text nav ');await page.waitForSelector('.webos-text-dialog input');await page.click('.webos-text-dialog input',{count:3});await page.keyboard.press('Backspace');await page.type('.webos-text-dialog input','During-save.txt');await button(page,'Save','.webos-text-dialog ');
  await intercepted;await edit(untitled,'Newer edits after save started');await release();await page.waitForFunction(async id=>!(await document.querySelector('.window[data-window="'+id+'"]').appView.inspect()).busy,{},untitled);
  await page.setRequestInterception(false);page.off('request',intercept);await stored(untitled);const state=(await viewStates()).find(s=>s.id===untitled);assert(state.dirty&&state.path==='During-save.txt');
  await file(page,'list');const v=await file(page,'snapshot',{path:'During-save.txt'});const data=await file(page,'download',{path:'During-save.txt',expectedRevision:v.sha256});assert.equal(new TextDecoder().decode(new Uint8Array(Object.values(data.data))),'Snapshot sent to server');
 });
 await check('Explicit Discard removes its draft; a clean reload does not resurrect it',async()=>{
  await focus(untitled);await page.click(scope(untitled)+'[aria-label="Close"]');await closeChoice('Discard');await page.waitForFunction(id=>!document.querySelector('.window[data-window="'+id+'"]'),{},untitled);
  await reload({warning:false});await login(page,accountA);await page.waitForFunction(()=>!!document.querySelector('.webos-files'));assert.equal(await page.$('.webos-text-dialog[data-kind=recovery]'),null);
 });
 await check('A durable orphan draft is offered even when its old desktop layout is missing',async()=>{
  const id=await newText();await edit(id,'Orphan local recovery');await stored(id);await page.evaluate(()=>{for(const d of window.desktopLab.surfaces.values())localStorage.removeItem(d.layoutKey(d.layoutOwner));});
  // Prevent the normal pagehide layout save solely in this disposable fixture
  // by clearing the account layout at the beginning of the next document.
  await page.evaluateOnNewDocument(()=>{for(const k of Object.keys(localStorage))if(k.includes('layout'))localStorage.removeItem(k);});
  await reload();await login(page,accountA);await recoverAll(1);assert((await viewStates()).some(s=>s.text==='Orphan local recovery'));
 });
 await check('Same browser signing into another account does not offer or display the first account drafts',async()=>{
  await reload();await login(page,accountB,true);await newText();assert.equal(await page.$('.webos-text-dialog[data-kind=recovery]'),null);assert((await viewStates()).every(s=>!s.text));
  const id=(await viewStates())[0].id;await edit(id,'Account B private draft');await stored(id);await reload();await login(page,accountA);await recoverAll(1);assert.deepEqual((await viewStates()).map(s=>s.text),['Orphan local recovery']);
 });
 await check('Cancelling session end after a Discard decision preserves every still-open draft',async()=>{
  const second=await newText();await edit(second,'Second session draft');await stored(second);
  await page.click('.app-menu-button');await button(page,'End session','.menu-pane ');await closeChoice('Discard');await closeChoice('Cancel');await page.waitForFunction(()=>!document.querySelector('.desktop').inert);
  assert.equal((await viewStates()).filter(s=>s.dirty).length,2);await reload();await login(page,accountA);await recoverAll(2);assert.deepEqual((await viewStates()).map(s=>s.text).sort(),['Orphan local recovery','Second session draft']);
 });
 await check('Completed session end with explicit Discard clears both drafts permanently',async()=>{
  await page.click('.app-menu-button');await button(page,'End session','.menu-pane ');await closeChoice('Discard');await closeChoice('Discard');await page.waitForSelector('.login-gate');await login(page,accountA);await newText();assert.equal(await page.$('.webos-text-dialog[data-kind=recovery]'),null);
 });
 await check('Unavailable local recovery is reported; dirty work still warns and can be saved to the account',async()=>{
  otherContext=await browser.createBrowserContext();const fault=await otherContext.newPage();await fault.setViewport({width:1440,height:1000});let warnings=0;
  fault.on('pageerror',e=>errors.push(e.message));fault.on('console',m=>{if(m.type()==='error')faultConsoleErrors.push(m.text());});
  fault.on('dialog',async d=>{assert.equal(d.type(),'beforeunload');warnings++;await d.dismiss();});
  await fault.evaluateOnNewDocument(()=>{const open=IDBFactory.prototype.open;IDBFactory.prototype.open=function(name,...args){if(name==='webos-text-recovery-v1')throw new DOMException('Injected recovery storage failure','QuotaExceededError');return open.call(this,name,...args);};});
  await fault.goto(origin,{waitUntil:'networkidle0'});await login(fault,accountA);await launch(fault,'Office','Text Editor (CodeMirror 6)');await fault.waitForSelector('.webos-text .cm-content');await fault.click('.webos-text .cm-content');await fault.keyboard.type('Account save despite recovery failure');
  await fault.waitForFunction(()=>document.querySelector('.webos-text-recovery')?.textContent.includes('Local recovery unavailable'));
  const cdp=await fault.createCDPSession();await cdp.send('Page.reload');await new Promise(r=>setTimeout(r,150));await cdp.detach();assert.equal(warnings,1);
  await button(fault,'Save','.webos-text nav ');await fault.waitForSelector('.webos-text-dialog input');await fault.click('.webos-text-dialog input',{count:3});await fault.keyboard.press('Backspace');await fault.type('.webos-text-dialog input','Storage-failure.txt');await button(fault,'Save','.webos-text-dialog ');await fault.waitForFunction(()=>document.querySelector('.webos-text-status')?.textContent==='Saved to your account.');
  await files(fault);const v=await file(fault,'snapshot',{path:'Storage-failure.txt'});const data=await file(fault,'download',{path:'Storage-failure.txt',expectedRevision:v.sha256});assert.equal(new TextDecoder().decode(new Uint8Array(Object.values(data.data))),'Account save despite recovery failure');
  assert.deepEqual(faultConsoleErrors,['Text recovery discovery unavailable: Injected recovery storage failure']);await otherContext.close();otherContext=null;
 });
 await page.screenshot({path:path.join(output,'text-recovery.png')});
 const report={status:checks.length===11&&checks.every(c=>c.status==='PASS')&&!errors.length&&!consoleErrors.length?'PASS':'FAIL',checks,pageErrors:errors,consoleErrors,faultConsoleErrors,browserDialogs:dialogs,scope:'Actual CodeMirror6, browser beforeunload, IndexedDB and signed account storage; disposable accounts. Recovery covers last acknowledged local checkpoints, not browser storage eviction or zero-loss power failure. The separate storage-failure context retains and verifies exactly one injected discovery error; unrelated errors fail.'};await writeFile(path.join(output,'result.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,checks,output}));assert.equal(report.status,'PASS');
}catch(e){await writeFile(path.join(output,'failure.json'),JSON.stringify({error:e.message,checks,pageErrors:errors,consoleErrors,states:await viewStates().catch(()=>null)},null,2)+'\n');throw e;}finally{await otherContext?.close();await browser?.close();}
