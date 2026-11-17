/** Real native/account proof: blank defaults, file preservation and cross-browser ownership. */
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
const origin=process.env.WEBOS_VIEWER_ORIGIN,output=process.env.WEBOS_TEST_OUTPUT,expected=process.env.WEBOS_ENGINE_COMMIT;
assert(origin&&path.isAbsolute(output)&&expected);await mkdir(output,{mode:0o700});
const account=prefix=>({username:prefix+randomBytes(6).toString('hex'),password:randomBytes(12).toString('hex')});
const accounts={a:account('wcdefaulta'),b:account('wcdefaultb')};
await writeFile(path.join(output,'accounts.json'),JSON.stringify(accounts),{mode:0o600});
const checks=[],errors=[],consoleErrors=[],httpErrors=[];let browser,page,other;
const scope=id=>'.window[data-window="'+id+'"] ';
async function button(label,parent='',p=page){for(const n of await p.$$(parent+'button'))if(await n.evaluate((n,l)=>(n.querySelector('.row-text')||n).textContent.trim()===l,label)){await n.click();return;}throw Error('Missing button '+label);}
async function ids(p=page){return p.$$eval('.window:has(.webos-wordcraft)',ns=>ns.map(n=>n.dataset.window));}
async function frame(id,p=page){return(await p.$(scope(id)+'iframe[title="WordCraft document"]')).contentFrame();}
async function command(id,command,params={},p=page){return(await frame(id,p)).evaluate(async(command,params)=>{const s=await window.wordcraft.uiInspect();return window.wordcraft.request('engine.execute',{command,params,doc:s.document});},command,params);}
async function model(id,p=page){return JSON.parse((await command(id,'document.recoverySnapshot',{},p)).data);}
async function ready(id,p=page){await p.waitForFunction(async id=>{try{return(await document.querySelector('.window[data-window="'+id+'"]').appView.inspect()).phase==='ready';}catch{return false;}},{timeout:120000},id);}
async function launch(p=page){const before=await ids(p);await p.click('.app-menu-button');await button('Office','.menu-pane ',p);await button('WordCraft','.menu-pane ',p);await p.waitForFunction(n=>document.querySelectorAll('.webos-wordcraft').length>n,{},before.length);const id=(await ids(p)).find(id=>!before.includes(id));await ready(id,p);return id;}
async function save(id,name,p=page){await command(id,'file.saveAs',{path:name},p);await p.waitForFunction(async({id,name})=>{const s=await document.querySelector('.window[data-window="'+id+'"]').appView.inspect();return s.path===name&&!s.dirty&&s.pendingSaves===0;},{},{id,name});}
async function setDefaults(id,p=page){assert.equal((await command(id,'design.setDefault',{},p)).hostRequested,true);await p.waitForFunction(id=>document.querySelector('.window[data-window="'+id+'"] .webos-wordcraft-status')?.textContent==='Default formatting saved to your account for new blank documents.',{},id);}
async function close(id,p=page){await p.evaluate(id=>{for(const d of window.desktopLab.surfaces.values()){const w=d.windows.find(w=>String(w.id)===id);if(w)d.activateWindow(w);}},id);await p.click(scope(id)+'[aria-label="Close"]');await p.waitForFunction(id=>!document.querySelector('.window[data-window="'+id+'"]'),{},id);}
async function openExisting(from,p=page){const before=await ids(p);await command(from,'ui.openFileDialog',{},p);await p.waitForSelector('.webos-wordcraft-dialog[data-kind="open"]');await p.waitForFunction(()=>[...document.querySelectorAll('.webos-wordcraft-file-list button')].some(n=>n.textContent==='Documents'));await button('Documents','.webos-wordcraft-file-list ',p);await p.waitForFunction(()=>[...document.querySelectorAll('.webos-wordcraft-file-list button')].some(n=>n.textContent==='Existing-design.docx'));await button('Existing-design.docx','.webos-wordcraft-file-list ',p);await p.waitForFunction(n=>document.querySelectorAll('.webos-wordcraft').length>n,{},before.length);const id=(await ids(p)).find(id=>!before.includes(id));await ready(id,p);return id;}
async function signOut(p=page){for(const id of await ids(p))await close(id,p);await p.click('.app-menu-button');await button('End session','.menu-pane ',p);await p.waitForSelector('.login-gate');}
async function login(credentials,register=false,p=page){await p.waitForSelector('.login-gate');if(register)await p.click('.login-toggle');await p.type('[aria-label="Username"]',credentials.username);await p.type('[aria-label="Password"]',credentials.password);if(register)await p.type('[aria-label="Confirm password"]',credentials.password);await button(register?'Register':'Sign in','.login-gate ',p);await p.waitForFunction(()=>!!window.desktopLab?.session&&!document.querySelector('.login-gate'));}
async function prepare(p){await p.setViewport({width:1600,height:1050});p.setDefaultTimeout(60000);p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});p.on('response',r=>{if(r.status()>=400)httpErrors.push({status:r.status(),path:new URL(r.url()).pathname});});await p.goto(origin,{waitUntil:'networkidle0'});assert.equal(await p.evaluate(async()=>{const r=await fetch('/viewer-build.json');return(await r.json()).engine.sourceCommit;}),expected);}
async function check(name,fn){await fn();checks.push(name);console.log(JSON.stringify({check:name,status:'PASS'}));}
let baseline,formatting,source;
try{
 browser=await puppeteer.launch({executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],userDataDir:path.join(output,'browser-profile')});
 page=await browser.newPage();await prepare(page);await login(accounts.a,true);
 await check('Set as Default saves formatting to the account without changing document content or save state',async()=>{
  source=await launch();await command(source,'text.insert',{text:'An existing document keeps its original design.'});await save(source,'Documents/Existing-design.docx');
  await close(source);source=await launch();const existing=await openExisting(source);baseline=await model(existing);await close(existing);await close(source);
  source=await launch();await command(source,'text.insert',{text:'This text must never become blank-document defaults.'});
  await command(source,'design.themeFonts',{heading:'Inter',body:'Source Serif 4'});await command(source,'design.styleSet',{name:'shaded'});await command(source,'design.themeColors',{name:'Studio'});await command(source,'design.paragraphSpacing',{value:'relaxed'});
  formatting=await model(source);await setDefaults(source);assert.deepEqual(await model(source),formatting);
  const state=await page.evaluate(async id=>document.querySelector('.window[data-window="'+id+'"]').appView.inspect(),source);assert.equal(state.dirty,true);assert.equal(state.path,null);
  await save(source,'Documents/Defaults-source.docx');await close(source);
 });
 await check('A new blank gets saved styles, fonts and colors with no copied document text',async()=>{
  source=await launch();const d=await model(source);assert.equal(d.settings.majorFont,'Inter');assert.equal(d.settings.minorFont,'Source Serif 4');assert.deepEqual(d.settings.themeColors,formatting.settings.themeColors);assert.deepEqual(d.styles,formatting.styles);assert(!JSON.stringify(d.body).includes('This text'));
  const inspection=await command(source,'document.text');assert.equal(inspection.text.trim(),'');
  await page.screenshot({path:path.join(output,'new-blank-defaults.png')});
 });
 await check('Opening the saved existing file keeps its original formatting after defaults change',async()=>{
  const existing=await openExisting(source);const d=await model(existing);
  assert.equal(d.settings.majorFont,baseline.settings.majorFont);assert.equal(d.settings.minorFont,baseline.settings.minorFont);assert.deepEqual(d.styles,baseline.styles);assert.deepEqual(d.settings.themeColors,baseline.settings.themeColors);await close(existing);
 });
 await check('Another account in the same browser gets its own defaults',async()=>{
  await signOut();await login(accounts.b,true);source=await launch();let d=await model(source);assert.equal(d.settings.majorFont,baseline.settings.majorFont);assert.equal(d.settings.minorFont,baseline.settings.minorFont);
  await command(source,'design.themeFonts',{heading:'Source Sans 3',body:'JetBrains Mono'});await setDefaults(source);await save(source,'Documents/B-defaults-source.docx');await signOut();
  await login(accounts.a);source=await launch();d=await model(source);assert.equal(d.settings.majorFont,'Inter');assert.equal(d.settings.minorFont,'Source Serif 4');
 });
 await check('A fresh browser context retrieves A defaults from the server without browser preference state',async()=>{
  other=await browser.createBrowserContext();const p=await other.newPage();await prepare(p);await login(accounts.a,false,p);const id=await launch(p);const d=await model(id,p);assert.equal(d.settings.majorFont,'Inter');assert.equal(d.settings.minorFont,'Source Serif 4');assert.deepEqual(d.styles,formatting.styles);await command(id,'para.heading1',{},p);await command(id,'text.insert',{text:'Account A default heading'},p);await command(id,'text.newParagraph',{},p);await command(id,'para.normal',{},p);await command(id,'text.insert',{text:'A fresh browser uses this account’s saved design.'},p);await save(id,'Documents/Fresh-defaults.docx',p);await p.screenshot({path:path.join(output,'fresh-browser-account-defaults.png')});await close(id,p);await other.close();other=null;
 });
 let filesId;
 async function files(operation,args={}){return page.evaluate(async({id,operation,args})=>{if(operation==='import')args.blob=new Blob([args.contents]);return document.querySelector('.window[data-window="'+id+'"]').appView.execute(operation,args);},{id:filesId,operation,args});}
 async function openText(name,contents){
  await files('import',{name,contents});await files('open',{path:'Documents/'+name});
  await page.waitForFunction(async path=>{for(const w of document.querySelectorAll('.window:has(.webos-text)')){const s=await w.appView.inspect();if(s.path===path&&s.loaded)return true;}return false;},{},'Documents/'+name);
  const id=await page.evaluate(async path=>{for(const w of document.querySelectorAll('.window:has(.webos-text)'))if((await w.appView.inspect()).path===path)return w.dataset.window;},'Documents/'+name);
  assert(await page.$(scope(id)+'.cm-editor'));assert.equal(await page.$$eval(scope(id)+'.cm-line',ns=>ns.map(n=>n.textContent).join('\n')),contents.replace(/\n$/,''));return id;
 }
 await check('Files defaults .txt to the actual CodeMirror 6 Text editor',async()=>{
  await page.click('.app-menu-button');await button('System Tools','.menu-pane ');await button('Files','.menu-pane ');await page.waitForSelector('.webos-files');filesId=await page.$eval('.window:has(.webos-files)',n=>n.dataset.window);
  await page.waitForFunction(async id=>{const s=await document.querySelector('.window[data-window="'+id+'"]').appView.inspect();return !s.busy&&s.entries.length>0;},{},filesId);await files('list',{path:'Documents'});
  const id=await openText('Association.txt','Plain text association fixture');await close(id);
 });
 await check('Files defaults .py to CodeMirror Text with Python content preserved',async()=>{
  const id=await openText('Association.py','def answer():\n    return 42');assert(await page.$(scope(id)+'.cm-content .cm-line span'),'Python token highlighting is active');await page.screenshot({path:path.join(output,'python-codemirror-association.png')});await close(id);
 });
 await check('A real .dotx template saved by the native codec opens from Files in WordCraft',async()=>{
  await command(source,'text.insert',{text:'Word template association fixture'});await save(source,'Documents/Association.dotx');await close(source);await files('list',{path:'Documents'});await files('open',{path:'Documents/Association.dotx'});
  await page.waitForFunction(()=>!!document.querySelector('.webos-wordcraft'));source=(await ids())[0];await ready(source);const s=await page.evaluate(async id=>document.querySelector('.window[data-window="'+id+'"]').appView.inspect(),source);assert.equal(s.path,'Documents/Association.dotx');assert.equal((await command(source,'document.text')).text.trim(),'Word template association fixture');await close(source);
 });
 await check('Calculator still mounts and computes through the changed shared account-app wrapper',async()=>{
  await page.click('.app-menu-button');await button('System Tools','.menu-pane ');await button('Calculator','.menu-pane ');await page.waitForSelector('.webos-calculator input');await page.type('.webos-calculator input','8*7');await button('Calculate','.webos-calculator ');await page.waitForFunction(()=>document.querySelector('.webos-calculator output')?.textContent==='56');
 });
 assert.deepEqual(errors,[]);assert.deepEqual(consoleErrors,[]);assert.deepEqual(httpErrors,[]);
 await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,engineCommit:expected,pageErrors:errors,consoleErrors,httpErrors},null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length}));
}catch(error){await writeFile(path.join(output,'failure.json'),JSON.stringify({error:error.message,checks,pageErrors:errors,consoleErrors,httpErrors},null,2)+'\n');if(page)await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});throw error;}
finally{await other?.close();await browser?.close();}
