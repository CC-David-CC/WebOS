/** Focused actual-engine checks for Design styles and the available font policy. */
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
const origin=process.env.WEBOS_VIEWER_ORIGIN,output=process.env.WEBOS_TEST_OUTPUT,expected=process.env.WEBOS_ENGINE_COMMIT;
assert(origin&&path.isAbsolute(output)&&expected);await mkdir(output,{mode:0o700});
const credentials={username:'wcdesign'+randomBytes(6).toString('hex'),password:randomBytes(12).toString('hex')};
await writeFile(path.join(output,'credentials.json'),JSON.stringify(credentials),{mode:0o600});
const checks=[],errors=[],consoleErrors=[],httpErrors=[];let browser,page,frame;
async function button(label,parent=''){for(const node of await page.$$(parent+'button'))if(await node.evaluate((n,l)=>(n.querySelector('.row-text')||n).textContent.trim()===l,label)){await node.click();return;}throw Error('Missing button: '+label);}
async function command(command,params={}){return frame.evaluate(async(command,params)=>{const s=await window.wordcraft.uiInspect();return window.wordcraft.request('engine.execute',{command,params,doc:s.document});},command,params);}
async function model(){return JSON.parse((await command('document.recoverySnapshot')).data);}
function heading(doc){return doc.styles.styles.find(s=>s.id==='Heading1');}
async function capture(name){await frame.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await page.screenshot({path:path.join(output,name+'.png')});}
async function check(name,fn){await fn();checks.push(name);console.log(JSON.stringify({check:name,status:'PASS'}));}
try{
 browser=await puppeteer.launch({executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',headless:true,args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],userDataDir:path.join(output,'browser-profile')});
 page=await browser.newPage();await page.setViewport({width:1600,height:1050});page.setDefaultTimeout(60000);
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});page.on('response',r=>{if(r.status()>=400)httpErrors.push({status:r.status(),path:new URL(r.url()).pathname});});
 await page.goto(origin,{waitUntil:'networkidle0'});assert.equal(await page.evaluate(async()=>{const r=await fetch('/viewer-build.json');return(await r.json()).engine.sourceCommit;}),expected);
 await page.waitForSelector('.login-gate');await page.click('.login-toggle');await page.type('[aria-label="Username"]',credentials.username);await page.type('[aria-label="Password"]',credentials.password);await page.type('[aria-label="Confirm password"]',credentials.password);await button('Register','.login-gate ');await page.waitForFunction(()=>!!window.desktopLab?.session&&!document.querySelector('.login-gate'));
 await page.click('.app-menu-button');await button('Office','.menu-pane ');await button('WordCraft','.menu-pane ');await page.waitForSelector('.webos-wordcraft');
 const id=await page.$eval('.window:has(.webos-wordcraft)',n=>n.dataset.window);await page.waitForFunction(async id=>{try{return(await document.querySelector('.window[data-window="'+id+'"]').appView.inspect()).phase==='ready';}catch{return false;}},{timeout:120000},id);
 await page.click('.window:has(.webos-wordcraft) [aria-label="Maximize"]');frame=await(await page.$('iframe[title="WordCraft document"]')).contentFrame();
 await check('The real native model has a heading and a separate Normal paragraph',async()=>{await command('para.heading1');await command('text.insert',{text:'Design preset heading'});await command('text.newParagraph');await command('para.normal');await command('text.insert',{text:'Normal body stays readable.'});await command('ui.backstage',{value:false});await command('ui.tab',{tab:'Design'});const d=await model();assert(d.body.some(b=>b.kind==='para'&&b.props.style==='Heading1'));assert(d.body.some(b=>b.kind==='para'&&b.props.style==='Normal'));});
 await check('All seven style presets apply their intended structure and contrasting Shaded text',async()=>{
  for(const name of ['default','basic','lines','shaded','casual','centered','minimalist']){
   await command('design.styleSet',{name});const h=heading(await model());assert(h,name);
   if(name==='basic')assert.equal(h.chr.bold,true);
   if(name==='lines')assert(h.para.borders.bottom);
   if(name==='shaded'){assert.deepEqual(h.chr.color,{Rgb:[255,255,255]});assert(h.para.shading);}
   if(name==='casual')assert.equal(h.chr.italic,true);
   if(name==='centered')assert.equal(h.para.align,'center');
   if(name==='minimalist')assert.equal(h.chr.caps,true);
   await capture('preset-'+name);
  }
 });
 await check('Shaded retains white text when theme colors change and after undo/redo',async()=>{
  await command('design.styleSet',{name:'shaded'});
  for(const name of ['Craft','Studio','Gallery','Atelier','Darkroom','Sketchbook']){await command('design.themeColors',{name});const d=await model(),h=heading(d);assert.deepEqual(h.chr.color,{Rgb:[255,255,255]});assert.deepEqual(h.para.shading,d.settings.themeColors[4]);}
  await command('edit.undo');assert.deepEqual(heading(await model()).chr.color,{Rgb:[255,255,255]});await command('edit.redo');assert.deepEqual(heading(await model()).chr.color,{Rgb:[255,255,255]});await capture('shaded-new-theme');
 });
 await check('Available font choices use real bundled families and document-wide font application works',async()=>{
  await command('design.themeFonts',{heading:'Source Serif 4',body:'Source Sans 3'});const d=await model();assert.equal(d.settings.majorFont,'Source Serif 4');assert.equal(d.settings.minorFont,'Source Sans 3');assert.equal(heading(d).chr.font,'Source Serif 4');await capture('available-fonts-applied');
 });
 await check('Existing unavailable requested names remain truthful rather than silently rewriting imported formatting',async()=>{
  await command('select.all');await command('format.font',{name:'Not Installed Design Fixture'});const d=await model();assert(JSON.stringify(d).includes('Not Installed Design Fixture'));await command('edit.undo');
 });
 await check('The actual account Save confirms the new rich styles without losing Shaded contrast',async()=>{
  await command('file.saveAs',{path:'Documents/Design-presets.docx'});await page.waitForFunction(async id=>{const s=await document.querySelector('.window[data-window="'+id+'"]').appView.inspect();return s.path==='Documents/Design-presets.docx'&&!s.dirty&&s.pendingSaves===0;},{},id);assert.deepEqual(heading(await model()).chr.color,{Rgb:[255,255,255]});
 });
 assert.deepEqual(errors,[]);assert.deepEqual(consoleErrors,[]);assert.deepEqual(httpErrors,[]);
 await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,engineCommit:expected,pageErrors:errors,consoleErrors,httpErrors,scope:'Focused native Design model, actual rendered presets, font application and account Save; native UI tests separately qualify font menu availability.'},null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length}));
}catch(error){await writeFile(path.join(output,'failure.json'),JSON.stringify({error:error.message,checks,pageErrors:errors,consoleErrors,httpErrors},null,2)+'\n');if(page)await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});throw error;}
finally{await browser?.close();}
