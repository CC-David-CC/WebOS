// Actual WebOS app adapter, command registry, CAD runtime and Worker; mirror is an in-memory fixture.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.JSKETCHER_HOST_URL||'http://127.0.0.1:19935/'),cdp=new URL(process.env.CODI_TEST_CDP||'http://127.0.0.1:19991/');
if(![base,cdp].every(u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Loopback only');
const b=await puppeteer.connect({browserURL:cdp.href,protocolTimeout:120000}),c=await b.createBrowserContext(),p=await c.newPage();
try{
 await p.setViewport({width:390,height:844,isMobile:true,hasTouch:true});await p.goto(base.href);await p.waitForFunction('window.launch');await p.evaluate(()=>launch());await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('New model.'),{timeout:90000});
 const f=await(await p.$('.jsketcher-app iframe')).contentFrame();const ids=await p.evaluate(()=>registry.list().map(x=>x.id));assert.ok(ids.includes('inspect-rectangle-creation')&&ids.includes('create-rectangle-sketch'));
 const capability=await p.evaluate(()=>registry.execute({windowId:'w0',command:'inspect-rectangle-creation',args:{}}));assert.equal(capability.ready,true);
 const args={revision:capability.revision,unit:'millimeter',origin:[10,20],width:100,height:50,depth:7};
 const result=await p.evaluate(args=>registry.execute({windowId:'w0',command:'create-rectangle-sketch',args}),args);assert.equal(result.persistence,'volatile-workspace');
 const stale=await p.evaluate(async args=>{try{await registry.execute({windowId:'w0',command:'create-rectangle-sketch',args});return ''}catch(e){return e.name}},args);assert.equal(stale,'AbortError');
 await f.evaluate(()=>{const btn=document.querySelector('[data-action-id="menu.primitives"]');if(!btn)throw Error('Add menu missing');btn.click()});
 await f.waitForFunction(()=>/Dimensioned rectangle/i.test(document.body.innerText));
 await f.evaluate(()=>{const el=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&/^Dimensioned rectangle$/i.test(e.textContent.trim()));if(!el)throw Error('Rectangle menu action missing');el.click()});
 await p.waitForSelector('dialog.jsketcher-rectangle-dialog[open]');
 const newer=await p.evaluate(()=>registry.execute({windowId:'w0',command:'inspect-rectangle-creation',args:{}}));
 await p.evaluate(args=>registry.execute({windowId:'w0',command:'create-rectangle-sketch',args}),{...args,revision:newer.revision,depth:15});
 await p.click('dialog.jsketcher-rectangle-dialog button[type=submit]');await p.waitForFunction(()=>document.querySelector('dialog.jsketcher-rectangle-dialog [role=alert]')?.textContent.length>0);
 assert.equal(await f.evaluate(()=>__CAD_APP.craftService.modifications$.value.history.length),2,'stale confirmation creates no plane');
 await p.evaluate(()=>[...document.querySelectorAll('dialog.jsketcher-rectangle-dialog button')].find(b=>b.textContent==='Cancel').click());
 await f.evaluate(()=>document.querySelector('[data-action-id="menu.primitives"]').click());await f.waitForFunction(()=>/Dimensioned rectangle/i.test(document.body.innerText));
 await f.evaluate(()=>[...document.querySelectorAll('*')].find(e=>e.children.length===0&&/^Dimensioned rectangle$/i.test(e.textContent.trim())).click());
 await p.waitForSelector('dialog.jsketcher-rectangle-dialog[open]');await p.$eval('dialog.jsketcher-rectangle-dialog input[name=width]',e=>e.value='80');await p.$eval('dialog.jsketcher-rectangle-dialog input[name=height]',e=>e.value='30');await p.click('dialog.jsketcher-rectangle-dialog button[type=submit]');
 await p.waitForFunction(()=>!document.querySelector('dialog.jsketcher-rectangle-dialog'));await f.waitForFunction('__CAD_APP.craftService.modifications$.value.history.length===3',{timeout:60000});
 assert.match(await p.$eval('.jsketcher-app .app-status',e=>e.textContent),/Save the project to My files/);
 await p.evaluate(()=>prompts.push('/rect.jsketcher.json'));await f.evaluate(()=>__CAD_APP.actionService.run('Save'));await p.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.includes('syncing with the server'),{timeout:30000});
 const saved=await p.evaluate(()=>JSON.parse(data.get('user:a:/rect.jsketcher.json').value));assert.equal(saved.project.model.history.length,3);assert.equal(saved.project.sketches.length,3);
 await p.evaluate(()=>launch());await p.waitForFunction(()=>document.querySelectorAll('.jsketcher-app').length===2&&document.querySelectorAll('.jsketcher-app .app-status')[1].textContent.startsWith('New model.'),{timeout:90000});
 const second=await(await p.$$('.jsketcher-app iframe'))[1].contentFrame();await p.evaluate(()=>pick.push('/rect.jsketcher.json'));await second.evaluate(()=>__CAD_APP.actionService.run('NativeFormatImport'));await p.waitForFunction(()=>document.querySelectorAll('.jsketcher-app .app-status')[1].textContent.startsWith('Opened /rect.jsketcher.json'),{timeout:90000});
 const restoredFrame=await(await p.$$('.jsketcher-app iframe'))[1].contentFrame();const reopened=await restoredFrame.evaluate(()=>__CAD_APP.projectManager.snapshotCurrentProject());assert.deepEqual(reopened.project.sketches,saved.project.sketches);
 await restoredFrame.addScriptTag({url:new URL('node_modules/jsketcher-build/static/webosTest.bundle.js',base).href});
 await restoredFrame.evaluate(()=>{window.Cypress={$:s=>{const a=[...document.querySelectorAll(s)];a.index=n=>a.indexOf(n);return a}};const ui=webosTest.modellerUISubject(__CAD_APP);ui.selectFaces([20,30,20],[20,30,-10]);ui.openSketcher();window.sc=__CAD_APP.services.sketcher.inPlaceEditor.sketcherAppContext;const c=sc.viewer.parametricManager.stage.algNumSystem.allConstraints.find(c=>c.schema.id==='SegmentLength'&&Number(c.constants.length)===100);if(!c?.annotations?.length)throw Error('Width annotation missing');sc.viewer.select([c.annotations[0]],true);sc.actions.EditConstraintFromItsAnnotation.invoke(sc);});
 await restoredFrame.waitForFunction(()=>document.body.innerText.includes('SEGMENT LENGTH'));const widthInput=(await restoredFrame.$$('input[type=text]'))[0];await widthInput.click({clickCount:3});await widthInput.press('Backspace');await widthInput.type('150');await widthInput.press('Enter');await restoredFrame.waitForFunction(()=>!document.body.innerText.includes('SEGMENT LENGTH'));
 const editedWidth=await restoredFrame.evaluate(()=>{const c=sc.viewer.parametricManager.stage.algNumSystem.allConstraints.find(c=>c.schema.id==='SegmentLength'&&Number(c.constants.length)===150);return Math.hypot(c.objects[0].b.x-c.objects[0].a.x,c.objects[0].b.y-c.objects[0].a.y)});assert.ok(Math.abs(editedWidth-150)<1e-6,'real editor changes the driving dimension');
 // Hold the actual Worker dispatch, change account, then let it continue.
 await p.evaluate(()=>launch());await p.waitForFunction(()=>document.querySelectorAll('.jsketcher-app').length===3&&document.querySelectorAll('.jsketcher-app .app-status')[2].textContent.startsWith('New model.'),{timeout:90000});
 const held=await(await p.$$('.jsketcher-app iframe'))[2].contentFrame();
 await held.evaluate(()=>{const Native=window.Worker;window.workerHeld=false;window.Worker=class extends Native{postMessage(...args){window.workerHeld=true;window.releaseWorker=()=>super.postMessage(...args);}}});
 const third=await p.evaluate(()=>registry.execute({windowId:'w2',command:'inspect-rectangle-creation',args:{}}));
 await p.evaluate(args=>{window.heldOutcome=registry.execute({windowId:'w2',command:'create-rectangle-sketch',args}).then(()=>({accepted:true}),e=>({accepted:false,name:e.name,message:e.message}));},{...args,revision:third.revision});
 await held.waitForFunction('window.workerHeld',{timeout:30000});await p.evaluate(()=>{currentOwner='user:b';currentSession={}});assert.equal(await p.evaluate(()=>registry.list().length),0);await held.evaluate(()=>releaseWorker());
 const outcome=await p.evaluate(()=>heldOutcome);assert.equal(outcome.accepted,false);assert.equal(await held.evaluate(()=>__CAD_APP.craftService.modifications$.value.history.length),0);
 await p.evaluate(()=>{currentOwner='user:a';currentSession={}});
 await p.evaluate(()=>{closeView(0);closeView(1);closeView(2)});console.log('PASS actual CAD worker, scoped registry, visible Add action, stale revision and in-memory My files save/reopen (phone viewport)');
}finally{await c.close();b.disconnect()}
