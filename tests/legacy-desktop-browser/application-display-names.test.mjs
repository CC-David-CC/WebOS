import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const url=process.env.CODI_TEST_URL||'http://127.0.0.1:18470/';
if(!['http://127.0.0.1','https://ksu.codes'].includes(new URL(url).origin))throw Error('Unexpected test origin');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),contexts=[];
const names={Office:['Text Editor (CodeMirror 6)','Document Editor (Tiptap)','Spreadsheet (Jspreadsheet CE + SheetJS CE)','Data Explorer (Perspective + DuckDB)','PDF Viewer (PDF.js)'],Programming:['Python Notebook (JupyterLite + Pyodide)'],Electronics:['Arduino Simulator (AVR8js)','Pico Simulator (RP2040js)','Circuit Simulator (CircuitJS)','Electronics Design (designElectronics)','Digital Logic Simulator (DigitalJS)'],Crafts:['Embroidery Studio (StitchFoundry)','Stitch Converter (tsembroidery)'],Diagramming:['Image Editor (Filerobot)','Diagram Editor (diagrams.net)','Sketch Board (Excalidraw)','Vector Editor (SVG-Edit)'],'3D Printing':['Fabrication Studio (Kiri:Moto)','Mesh Editor (Mesh:Tool)','G-code Viewer (G-code Preview)','Primitive 3D Modeler (Replicad)'],'Audio Tools':['Audio Editor (AudioMass)']};
try{
 for(const phone of [false,true]){
  const ctx=await browser.createBrowserContext();contexts.push(ctx);const page=await ctx.newPage();await page.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1440,height:900});
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(url);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');const user='labels'+Date.now().toString().slice(-10)+(phone?'b':'a');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');console.log('Test account',user,await page.evaluate(()=>signedInSubject()));
  const clickLauncher=async()=>{for(let attempt=0;attempt<4;attempt++){try{await page.click('[aria-label=Applications]');return}catch(error){if(attempt===3||!String(error.message).includes('detached'))throw error}}};
  for(const [category,expected] of Object.entries(names)){
   await clickLauncher();await page.evaluate(category=>{[...document.querySelectorAll('.menu-pane button')].find(e=>e.getAttribute('aria-label')===category).click()},category);
   const labels=await page.$$eval('.menu-pane[data-depth="1"] button',buttons=>buttons.map(b=>b.getAttribute('aria-label')));
   for(const label of expected)assert.ok(labels.includes(label),`${category} missing ${label}`);
   await clickLauncher();
  }
  await clickLauncher();await page.evaluate(()=>[...document.querySelectorAll('.menu-pane button')].find(e=>e.getAttribute('aria-label')==='3D Printing').click());await page.evaluate(()=>[...document.querySelectorAll('.menu-pane button')].find(e=>e.getAttribute('aria-label')==='Fabrication Studio (Kiri:Moto)').click());
  await page.waitForSelector('.task[data-app="kiri-moto"]');const task=await page.$('.task[data-app="kiri-moto"]');assert.equal(await task.evaluate(e=>e.getAttribute('aria-label')),'Fabrication Studio (Kiri:Moto) windows');assert.match(await task.evaluate(e=>e.title),/^Fabrication Studio \(Kiri:Moto\): 1 open/);
  assert.equal(await page.$eval('.window.focused .caption-text',e=>e.textContent),'Fabrication Studio (Kiri:Moto)');await task.click();assert.ok((await page.$eval('.task-popup',e=>e.textContent)).includes('New Fabrication Studio (Kiri:Moto) window'));
  await page.evaluate(()=>{const d=surfaces.get('Desktop'),w=d.windows.find(w=>w.app==='kiri-moto');w.title='model.kiri — Kiri:Moto';d.render()});assert.equal(await page.$eval('.window.focused .caption-text',e=>e.textContent),'model.kiri — Fabrication Studio (Kiri:Moto)');
  assert.equal(await page.$eval('.task[data-app=terminal]',e=>e.getAttribute('aria-label')),'terminal windows');
  const labels=await page.evaluate(()=>({game:applicationMenuNames.get(desktopMenu.find(e=>e.name==='Games').children[0])??null,personal:applicationName('user-app:example:canvas','Blank canvas')}));assert.deepEqual(labels,{game:null,personal:'Blank canvas'});
  await page.evaluate(()=>{const d=surfaces.get('Desktop');d.closePopups();d.menu=true;d.showMenu([{name:'Text Editor',icon:'text',action:()=>{}}],0,0,0)});assert.ok(await page.$('.menu-pane [aria-label="Text Editor"]'),'personal app named Text Editor keeps its own name');assert.equal(await page.$('.menu-pane [aria-label="Text Editor (CodeMirror 6)"]'),null);
 }
 console.log('PASS exhaustive menu names and representative menu launch, taskbar, popup, changing window title on desktop and emulated phone');
}finally{for(const c of contexts)await c.close();await browser.disconnect()}
