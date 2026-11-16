/** Existing-viewer fidelity and real account/app smoke; explicit disposable test data. */
import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const origin=process.env.WEBOS_VIEWER_ORIGIN,output=process.env.WEBOS_TEST_OUTPUT;
assert(origin&&output&&path.isAbsolute(output),'Explicit origin and new private external output required.');
await mkdir(output,{mode:0o700});
const credentials={username:'viewer'+randomBytes(6).toString('hex'),password:randomBytes(12).toString('hex')};
await writeFile(path.join(output,'test-credentials.json'),JSON.stringify(credentials),{mode:0o600});
const errors=[],requests=[],failed=[],checks=[];let browser,page;
async function button(page,label,scope=''){
  for(const handle of await page.$$(scope+'button'))if((await handle.evaluate(n=>(n.querySelector('.row-text')||n).textContent.trim()))===label){await handle.click();return;}
  throw Error('Button unavailable: '+label);
}
async function launch(page,group,name){await page.click('.app-menu-button');await button(page,group,'.menu-pane ');await button(page,name,'.menu-pane ');}
try{
  browser=await puppeteer.launch({executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,
    args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],userDataDir:path.join(output,'browser-profile')});
  page=await browser.newPage();await page.setViewport({width:1440,height:1000});page.setDefaultTimeout(30000);
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(new URL(r.url()).pathname));page.on('requestfailed',r=>failed.push({path:new URL(r.url()).pathname,error:r.failure()?.errorText}));
  await page.goto(origin,{waitUntil:'networkidle0'});await page.waitForSelector('.login-toggle');
  await page.click('.login-toggle');await page.type('[aria-label="Username"]',credentials.username);await page.type('[aria-label="Password"]',credentials.password);await page.type('[aria-label="Confirm password"]',credentials.password);
  await button(page,'Register','.login-gate ');await page.waitForFunction(()=>!!window.desktopLab?.session&&!document.querySelector('.login-gate'));
  const viewer=await page.evaluate(()=>{
    const rectangle=n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
    return {desktop:rectangle(document.querySelector('.desktop')),panel:rectangle(document.querySelector('.panel')),apps:rectangle(document.querySelector('.app-menu-button')),
      account:rectangle(document.querySelector('.account')),clock:rectangle(document.querySelector('.clock')),background:getComputedStyle(document.querySelector('.desktop')).backgroundColor,
      separateSignOutButton:[...document.querySelectorAll('.panel button')].some(n=>n.textContent.trim()==='Sign out'),guest:window.desktopLab.guestState};
  });
  assert(viewer.panel.x>1300&&viewer.panel.width<=80,'Original narrow right rail');
  assert(viewer.apps.y>900,'APPs remains at bottom right');assert(viewer.account.y<150&&viewer.clock.y<200,'Account and date remain at the top');
  assert.equal(viewer.separateSignOutButton,false);assert.notEqual(viewer.background,'rgb(70, 109, 128)');assert.equal(viewer.guest,'disabled');
  await page.screenshot({path:path.join(output,'correct-viewer.png')});checks.push('original viewer geometry, rail order, palette and account presentation');
  await launch(page,'System Tools','Calculator');await page.waitForSelector('.webos-calculator input');
  await page.type('.webos-calculator input','8*7');await button(page,'Calculate','.webos-calculator ');
  await page.waitForFunction(()=>document.querySelector('.webos-calculator output')?.textContent==='56');
  const firstCalculator=await page.$eval('.webos-calculator',n=>n.closest('.window').dataset.window);
  const windowSelector='.window[data-window="'+firstCalculator+'"]';
  const before=await page.$eval(windowSelector,n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};});
  const caption=await page.$(windowSelector+' .window-caption'),cap=await caption.boundingBox();
  await page.mouse.move(cap.x+80,cap.y+15);await page.mouse.down();await page.mouse.move(cap.x+120,cap.y+55,{steps:8});await page.mouse.up();
  const moved=await page.$eval(windowSelector,n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y};});assert(moved.x!==before.x||moved.y!==before.y);
  const resize=await page.$(windowSelector+' .resize-handle'),resizeBox=await resize.boundingBox();
  await page.mouse.move(resizeBox.x+2,resizeBox.y+2);await page.mouse.down();await page.mouse.move(resizeBox.x-60,resizeBox.y-60,{steps:8});await page.mouse.up();
  const resized=await page.$eval(windowSelector,n=>n.getBoundingClientRect().width);assert(resized<before.width);
  await page.click(windowSelector+' [aria-label="Minimize"]');assert(await page.$eval(windowSelector,n=>n.hidden));
  await page.click('.task[data-app="calculator"]');await page.click('.task-popup [data-window-id="'+firstCalculator+'"]');assert.equal(await page.$eval(windowSelector,n=>n.hidden),false);
  checks.push('original window move, resize, minimize and restore');
  await launch(page,'System Tools','Calculator');await page.waitForFunction(()=>document.querySelectorAll('.webos-calculator input').length===2);
  const values=await page.$$eval('.webos-calculator input',ns=>ns.map(n=>n.value));assert.deepEqual(values,['8*7','']);checks.push('Calculator mouse/keyboard calculation and two independent instances');
  await page.click('.window.focused:has(.webos-calculator) [aria-label="Close"]');await page.waitForFunction(()=>document.querySelectorAll('.webos-calculator').length===1);
  assert.equal(await page.$eval('.webos-calculator output',n=>n.textContent),'56');
  checks.push('closing one Calculator retains the other');
  await launch(page,'System Tools','Files');await page.waitForSelector('.webos-files-view');
  await page.waitForFunction(()=>document.querySelector('.webos-files')?.textContent.includes('My files'));
  const files=await page.evaluate(async()=>{const w=[...document.querySelectorAll('.window')].find(n=>n.querySelector('.webos-files'));await w.appView.ready;return await w.appView.inspect();});
  assert(files.entries.some(e=>e.name==='Documents'&&e.directory));checks.push('Files actual signed account listing');
  await button(page,'New folder','.webos-files ');await page.waitForSelector('.webos-files-dialog input');await page.type('.webos-files-dialog input','ViewerCheck');await button(page,'Continue','.webos-files-dialog ');
  await page.waitForSelector('.webos-files-browser [title="ViewerCheck"]');
  await writeFile(path.join(output,'viewer-upload.txt'),'Disposable viewer upload\n');
  const upload=await page.$('.webos-files input[type=file]');await upload.uploadFile(path.join(output,'viewer-upload.txt'));await page.waitForSelector('.webos-files-browser [title="viewer-upload.txt"]');
  checks.push('Files folder creation and actual upload');
  await launch(page,'Office','Text Editor (CodeMirror 6)');await page.waitForSelector('.webos-text .cm-content');
  await page.waitForFunction(()=>document.querySelector('.webos-text-status')?.textContent.includes('ready'));checks.push('Text actual CodeMirror document startup');
  await page.click('.webos-text .cm-content');await page.keyboard.type('Saved through the original viewer.');await button(page,'Save','.webos-text nav ');
  await page.waitForSelector('.webos-text-dialog input');await page.click('.webos-text-dialog input',{count:3});await page.keyboard.press('Backspace');await page.type('.webos-text-dialog input','Documents/ViewerText.txt');await button(page,'Save','.webos-text-dialog ');
  await page.waitForFunction(()=>document.querySelector('.webos-text-status')?.textContent==='Saved to your account.');
  await page.click('.webos-text .cm-content');await page.keyboard.type(' unsaved');await page.click('.window:has(.webos-text) [aria-label="Close"]');
  await page.waitForSelector('.webos-text-dialog');await button(page,'Cancel','.webos-text-dialog ');assert(await page.$('.webos-text .cm-content'));
  await page.click('.window:has(.webos-text) [aria-label="Close"]');await page.waitForSelector('.webos-text-dialog');await button(page,'Discard','.webos-text-dialog ');await page.waitForFunction(()=>!document.querySelector('.webos-text'));
  checks.push('Text server save and close Cancel/Discard protection');
  await launch(page,'Office','WordCraft');await page.waitForSelector('iframe[title="WordCraft document"]');
  await page.waitForFunction(()=>!!document.querySelector('iframe[title="WordCraft document"]')?.contentWindow?.wordcraft?.request,{timeout:120000});
  await page.evaluate(async()=>{const w=[...document.querySelectorAll('.window')].find(n=>n.querySelector('iframe[title="WordCraft document"]'));await w.appView.ready;});
  checks.push('WordCraft actual WASM engine and account host startup');
  let frame=await (await page.$('iframe[title="WordCraft document"]')).contentFrame();
  const command=(f,name,args={})=>f.evaluate(async(name,args)=>{const s=await window.wordcraft.uiInspect();return window.wordcraft.request('engine.execute',{command:name,params:args,doc:s.document});},name,args);
  const structure=f=>f.evaluate(async()=>{const d=await window.wordcraft.docInspect({text:true});return d.blocks.filter(b=>b.type==='paragraph').map(b=>({text:b.text,style:b.style,list:b.list||null}));});
  await command(frame,'para.heading1');await command(frame,'text.insert',{text:'Correct viewer document'});await command(frame,'text.newParagraph');await command(frame,'para.normal');await command(frame,'text.insert',{text:'An account-backed paragraph.'});
  await command(frame,'text.newParagraph');await command(frame,'para.bullets');await command(frame,'text.insert',{text:'A list item'});
  await page.click('.app-menu-button');await button(page,'End session','.menu-pane ');await page.waitForSelector('.webos-wordcraft-close');await button(page,'Cancel','.webos-wordcraft-close ');
  await page.waitForFunction(()=>!document.querySelector('.desktop').inert);assert(await page.evaluate(()=>!!window.desktopLab.session));
  checks.push('End session honors WordCraft unsaved-work cancellation');
  const documentStructure=await structure(frame);assert.equal(documentStructure[0].style,'Heading1');assert(documentStructure.some(b=>b.list));
  await command(frame,'file.saveAs',{path:'ViewerAuthoring.docx'});await page.waitForFunction(()=>document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('Saved to your account:'));
  await frame.waitForFunction(async()=>{const s=await window.wordcraft.uiInspect();return !s.dirty&&s.pendingSaves===0;});
  await page.click('.window:has(.webos-wordcraft) [aria-label="Close"]');await page.waitForFunction(()=>!document.querySelector('.webos-wordcraft'));
  checks.push('WordCraft heading/paragraph/list, acknowledged account save and clean close');
  await launch(page,'System Tools','Files');await page.waitForFunction(()=>document.querySelectorAll('.webos-files').length===2);
  const filesWindow=(await page.$$eval('.webos-files',ns=>ns.map(n=>n.closest('.window').dataset.window))).at(-1),filesScope='.window[data-window="'+filesWindow+'"] ';
  await page.waitForSelector(filesScope+'.webos-files-browser [title="Documents"]');await page.click(filesScope+'.webos-files-browser [title="Documents"]',{count:2});
  await page.waitForSelector(filesScope+'.webos-files-browser [title="ViewerText.txt"]');await page.click(filesScope+'.webos-files-browser [title="ViewerText.txt"]',{count:2});
  await page.waitForFunction(()=>document.querySelector('.webos-text .cm-content')?.textContent==='Saved through the original viewer.');
  await page.click('.window:has(.webos-text) [aria-label="Close"]');await page.waitForFunction(()=>!document.querySelector('.webos-text'));
  await page.click(filesScope+'.webos-files-browser [title="ViewerAuthoring.docx"]',{count:2});await page.waitForSelector('iframe[title="WordCraft document"]');
  await page.waitForFunction(()=>document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('Opened account file:'),{timeout:120000});
  frame=await (await page.$('iframe[title="WordCraft document"]')).contentFrame();assert.deepEqual(await structure(frame),documentStructure);
  checks.push('Files opens saved Text and WordCraft; document formatting survives reopen');
  const second=await browser.createBrowserContext(),other=await second.newPage();await other.setViewport({width:1440,height:1000});other.setDefaultTimeout(30000);other.on('pageerror',e=>errors.push(e.message));
  await other.goto(origin,{waitUntil:'networkidle0'});await other.waitForSelector('.login-gate');await other.type('[aria-label="Username"]',credentials.username);await other.type('[aria-label="Password"]',credentials.password);await button(other,'Sign in','.login-gate ');
  await other.waitForFunction(()=>!!window.desktopLab?.session&&!document.querySelector('.login-gate'));await launch(other,'System Tools','Files');await other.waitForSelector('.webos-files-browser [title="Documents"]');await other.click('.webos-files-browser [title="Documents"]',{count:2});
  await other.waitForSelector('.webos-files-browser [title="ViewerAuthoring.docx"]');await other.click('.webos-files-browser [title="ViewerAuthoring.docx"]',{count:2});
  await other.waitForFunction(()=>document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('Opened account file:'),{timeout:120000});
  const otherFrame=await (await other.$('iframe[title="WordCraft document"]')).contentFrame();assert.deepEqual(await structure(otherFrame),documentStructure);await other.screenshot({path:path.join(output,'second-context-document.png')});
  checks.push('fresh browser context retrieves the same server-backed formatted document');await second.close();
  await page.reload({waitUntil:'networkidle0'});await page.waitForSelector('.login-gate');await page.type('[aria-label="Username"]',credentials.username);await page.type('[aria-label="Password"]',credentials.password);await button(page,'Sign in','.login-gate ');
  await page.waitForFunction(()=>document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('Opened account file:'),{timeout:120000});
  frame=await (await page.$('iframe[title="WordCraft document"]')).contentFrame();assert.deepEqual(await structure(frame),documentStructure);checks.push('reload, sign-in and original layout restore retain the account document');
  assert(!requests.some(p=>p.includes('/.build/v86/')||p.includes('/guest-network')));assert.deepEqual(errors,[]);
  await page.screenshot({path:path.join(output,'viewer-apps.png')});
  await page.click('.app-menu-button');await button(page,'End session','.menu-pane ');await page.waitForSelector('.login-gate');assert.equal(await page.evaluate(()=>window.desktopLab.session),null);checks.push('End session returns to the original sign-in gate');
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,viewer,pageErrors:errors,failedRequests:failed,noGuestRequests:true,scope:'Original viewer/window behavior and real account-file/editing round trips, including fresh browser context. No full-suite or physical-second-machine claim.'},null,2)+'\n');
  console.log(JSON.stringify({status:'PASS',checks:checks.length,output}));
}catch(error){
  if(page){await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});await writeFile(path.join(output,'failure-state.json'),JSON.stringify({error:error.message,pageErrors:errors,failedRequests:failed,body:await page.evaluate(()=>document.body.innerText).catch(()=>null)},null,2));}
  throw error;
}finally{await browser?.close();}
