// Read-only file investigation: actual editor transitions, no host Save.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
const puppeteer=createRequire(import.meta.url)(process.env.PUPPETEER_CORE_PATH||'/tmp/codi-occt-release-control/node_modules/puppeteer-core');
const base=new URL(process.env.CODI_TEST_URL),cdp=new URL(process.env.CODI_TEST_CDP);
for(const u of [base,cdp])if(!['127.0.0.1','localhost','[::1]'].includes(u.hostname))throw Error('Loopback only');
const path=process.env.CODI_NOOP_PATH||'/diameter-diag.jsketcher.json',user=process.env.CODI_NOOP_USER;
if(!user)throw Error('Provide the owned fixture account.');
const browser=await puppeteer.connect({browserURL:cdp.href,protocolTimeout:120000}),context=await browser.createBrowserContext();
const result={source:'0b9e38394',user,path,phases:{}};let passed=false;
async function inspect(page){return page.evaluate(async()=>{const command=codiDesktopCommands.list().find(c=>c.appId==='jsketcher'&&c.id==='inspect');try{return await codiDesktopCommands.execute({windowId:command.windowId,command:'inspect',args:{}})}catch(error){return {error:error.message}}});}
function changed(a,b,path='$',out=[]){if(JSON.stringify(a)===JSON.stringify(b))return out;if(a&&b&&typeof a==='object'&&typeof b==='object'){for(const key of new Set([...Object.keys(a),...Object.keys(b)]))changed(a[key],b[key],path+'.'+key,out);}else out.push({path,before:a,after:b});return out;}
try{
 const page=await context.newPage();await page.goto(base);await page.waitForSelector('.login-toggle');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]',process.env.CODI_NOOP_PASSWORD||'test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>surfaces.get('Desktop').launch('files'));await page.waitForSelector(`[data-chonky-file-id="${path}"]`,{timeout:45000});await page.click(`[data-chonky-file-id="${path}"]`);await page.waitForFunction(()=>[...document.querySelectorAll('.codi-chonky button')].some(b=>b.textContent.trim()==='Open'&&!b.disabled));await page.evaluate(()=>[...document.querySelectorAll('.codi-chonky button')].find(b=>b.textContent.trim()==='Open'&&!b.disabled).click());await page.waitForFunction(path=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('Opened '+path),{timeout:90000},path);
 const frame=await(await page.$('.jsketcher-app iframe')).contentFrame();result.frameURL=frame.url();
 const server=()=>page.evaluate(async path=>{const file=await(await serverFileContext()).files.read(path.slice(1));return {sha256:file.sha256,native:JSON.parse(new TextDecoder().decode(file.data))}},path);
 result.serverBefore=await server();
 await frame.evaluate(()=>{window.captureNoop=()=>{const c=__CAD_APP,s=c.services.storage,ns=c.projectService.sketchStorageNamespace,keys=s.getAllKeysFromNamespace(ns).sort(),read=()=>Object.fromEntries(keys.map(key=>[key.slice(ns.length),s.get(key)])),before=read(),storageRevisionBefore=s.revision;let native=null,nativeError=null;try{native=c.projectManager.snapshotCurrentProject()}catch(error){nativeError=error.message}const editor=c.services.sketcher.inPlaceEditor,v=editor.viewer;return {storedBefore:before,storedAfter:read(),storageRevisionBefore,storageRevisionAfter:s.revision,native,nativeError,history:JSON.parse(JSON.stringify(c.craftService.modifications$.value)),metadata:c.projectManager.getManufacturingMetadata(),source:c.expressionService.script$.value,expressionsSignature:c.expressionService.signature,expressionTable:JSON.parse(JSON.stringify(c.expressionService.table$.value)),inEditMode:editor.inEditMode,activeSource:v?v.io.serializeSketch(undefined,{strict:true}):null,editorHistory:v?{diffs:JSON.parse(JSON.stringify(v.historyManager.diffs)),pointer:v.historyManager.historyPointer,last:v.historyManager.lastCheckpoint,counter:v.historyManager._counter}:null}};});
 const capture=async name=>{result.phases[name]=await frame.evaluate(()=>captureNoop());result.phases[name].hostInspect=await inspect(page);};
 await capture('fresh');await capture('freshSnapshotControl');
 const faceId=Object.entries(result.phases.fresh.storedAfter).find(([,text])=>JSON.parse(text).stages.some(stage=>stage.constraints.some(c=>c.typeId==='DiameterLength'&&c.constants?.diameter==='D')))?.[0];assert.ok(faceId,'A stored named-D circle sketch is required');result.faceId=faceId;
 const open=async()=>{await frame.evaluate(faceId=>{const c=__CAD_APP,face=c.cadRegistry.findFace(faceId);if(!face)throw Error('Face unavailable');c.services.sketcher.sketchFace(face)},faceId);await frame.waitForFunction('__CAD_APP.services.sketcher.inPlaceEditor.inEditMode===true');};
 await open();await capture('open');
 await page.evaluate(()=>document.querySelector('.jsketcher-app').closest('.window').querySelector('[aria-label="Close"]').click());await page.waitForSelector('dialog.codi-confirm-dialog[open]');result.openEditorCloseConfirmation=true;
 const keep=await page.evaluate(()=>{const buttons=[...document.querySelectorAll('dialog.codi-confirm-dialog[open] button')],button=buttons.find(b=>/Keep editing|Keep changes|Cancel/i.test(b.textContent));if(!button)throw Error('Keep-editing button unavailable');const text=button.textContent;button.click();return text;});result.keepButton=keep;
 await frame.evaluate(()=>__CAD_APP.services.sketcher.inPlaceEditor.exit());await frame.waitForFunction(()=>!__CAD_APP.services.sketcher.inPlaceEditor.inEditMode);await capture('exitWithoutSave');
 await open();await capture('reopen');await frame.evaluate(()=>__CAD_APP.actionService.run('sketchSaveAndExit'));await frame.waitForFunction(()=>!__CAD_APP.services.sketcher.inPlaceEditor.inEditMode&&!__CAD_APP.craftService.isProcessing,{timeout:90000});await capture('saveAndExitNoEdit');
 result.serverAfter=await server();assert.equal(result.serverAfter.sha256,result.serverBefore.sha256,'No host Save/server write occurred');
 result.diffs={snapshotControl:changed(result.phases.fresh.native,result.phases.freshSnapshotControl.native),exitWithoutSave:changed(result.phases.fresh.native,result.phases.exitWithoutSave.native),saveAndExit:changed(result.phases.exitWithoutSave.native,result.phases.saveAndExitNoEdit.native)};
 result.storedSketchDiffs={exitWithoutSave:changed(JSON.parse(result.phases.fresh.storedAfter[faceId]),JSON.parse(result.phases.exitWithoutSave.storedAfter[faceId])),saveAndExit:changed(JSON.parse(result.phases.exitWithoutSave.storedAfter[faceId]),JSON.parse(result.phases.saveAndExitNoEdit.storedAfter[faceId]))};
 console.log('NOOP_DIFFS',JSON.stringify({diffs:result.diffs,storedSketchDiffs:result.storedSketchDiffs,dirty:Object.fromEntries(Object.entries(result.phases).map(([name,data])=>[name,data.hostInspect])),serverSha:result.serverAfter.sha256}));passed=true;
}finally{
 await writeFile(process.env.CODI_NOOP_OUTPUT||'/tmp/codi-noop-editor-diamdiag-0b9-20261105.json',JSON.stringify(result,null,2)+'\n');
 if(passed)await context.close();else console.error('Retained investigation context',context.id);browser.disconnect();
}
