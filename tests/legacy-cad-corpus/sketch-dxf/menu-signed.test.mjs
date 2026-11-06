// Actual selected-face File menu route and signed storage. The sole selection
// setup uses the production marker service; this does not claim pointer picking.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL),cdp=new URL(process.env.CODI_TEST_CDP);
if(![base,cdp].every(u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Loopback only');
const browser=await puppeteer.connect({browserURL:cdp.href,protocolTimeout:120000}),context=await browser.createBrowserContext();
const name='dxfmenu'+Date.now(),password='test1234',path='/menu-sketch.dxf';
const page=await context.newPage(),dialogs=[];page.on('dialog',async dialog=>{dialogs.push(dialog.type());await dialog.dismiss();});
async function command(id,args={}){return page.evaluate(({id,args})=>{const c=codiDesktopCommands.list().find(c=>c.appId==='jsketcher'&&c.id===id);return codiDesktopCommands.execute({windowId:c.windowId,command:id,args});},{id,args});}
async function synced(){const until=Date.now()+60000;while(Date.now()<until){try{const value=await page.evaluate(async path=>{const local=await(await mirrorFileContext()).files.read(path),server=await(await serverFileContext()).files.read(path.slice(1));return {local:local.sha256,server:server.sha256,text:new TextDecoder().decode(server.data)}},path);if(value.local===value.server)return value;}catch{}await new Promise(r=>setTimeout(r,200));}throw Error('Signed menu file did not sync');}
try{
 console.log('TEST_ACCOUNT',name,'FILE',path,'SELECTION production marker setup; actual visible File/menu/prompt controls');
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]',password);await page.type('[aria-label="Confirm password"]',password);await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>desktopLab?.session?.kind==='registered');
 await page.evaluate(()=>surfaces.get('Desktop').launch('jsketcher'));await page.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});
 const creation=await command('inspect-sketch-creation'),plane=await command('create-empty-sketch-plane',{revision:creation.revision,unit:'millimeter',plane:'XY',depth:0});
 let sketches=await command('inspect-closed-sketches'),state=await command('inspect-closed-sketch',{revision:sketches.revision,faceId:plane.faceId});await command('append-sketch-primitive',{revision:state.revision,faceId:plane.faceId,stage:0,kind:'Point',role:null,data:{x:2,y:3}});
 // A top-window message cannot impersonate the currently active CAD iframe.
 await page.evaluate(faceId=>window.postMessage({codiJSketcher:{type:'file-action',action:'export-dxf',faceId}},location.origin),plane.faceId);await new Promise(r=>setTimeout(r,150));assert.equal(await page.$('.codi-prompt-dialog'),null);
 const iframe=await(await page.$('.jsketcher-app iframe')).contentFrame();await iframe.evaluate(faceId=>{const c=__CAD_APP,face=c.cadRegistry.findFace(faceId);c.services.marker.markExclusively(face.TYPE,face.id);},plane.faceId);
 async function exportMenu(){await iframe.click('[data-action-id="menu.file"]');await iframe.waitForSelector('[data-action-id="ExportFaceToDXF"]');await iframe.click('[data-action-id="ExportFaceToDXF"]');await page.waitForSelector('.codi-prompt-dialog input');}
 await exportMenu();await page.evaluate(()=>[...document.querySelectorAll('.codi-prompt-dialog button')].find(b=>b.textContent==='Cancel').click());assert.equal(await page.$('.codi-prompt-dialog'),null);
 await exportMenu();await page.click('.codi-prompt-dialog input',{clickCount:3});await page.type('.codi-prompt-dialog input',path);await page.click('.codi-prompt-dialog button[type=submit]');const first=await synced();assert.match(first.text,/\$INSUNITS/);assert.match(first.text,/POINT/);
 // A competing signed-file revision after the replacement dialog must survive.
 await exportMenu();await page.click('.codi-prompt-dialog input',{clickCount:3});await page.type('.codi-prompt-dialog input',path);await page.click('.codi-prompt-dialog button[type=submit]');await page.waitForSelector('.codi-confirm-dialog');
 await page.evaluate(async path=>{const files=(await mirrorFileContext()).files,current=await files.stat(path);await files.write(path,'concurrent edit',current.version);await files.sync();},path);
 await page.evaluate(()=>[...document.querySelectorAll('.codi-confirm-dialog button')].find(b=>b.textContent==='Replace').click());await page.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.includes('file changed while confirming'));
 const after=await synced();assert.equal(after.text,'concurrent edit');assert.notEqual(after.server,first.server);assert.deepEqual(dialogs,[]);
 console.log('FIRST_SERVER_HASH',first.server,'CONCURRENT_HASH',after.server);console.log('PASS actual selected-face File menu -> themed prompt -> signed My files, cancel, forged-source rejection and replacement CAS preservation; no native dialog');
}finally{await context.close();browser.disconnect();}
