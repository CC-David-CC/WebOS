import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.JSKETCHER_HOST_URL),cdp=new URL(process.env.CODI_TEST_CDP);
if(![base,cdp].every(u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Loopback only');
const b=await puppeteer.connect({browserURL:cdp.href,protocolTimeout:120000});
try{
 for(const phone of [false,true]){
  const context=await b.createBrowserContext(),p=await context.newPage();
  try{
   await p.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1366,height:900});await p.goto(base.href);await p.waitForFunction('window.launch');await p.evaluate(()=>launch());await p.waitForFunction(()=>document.querySelector('.app-status')?.textContent.startsWith('New model.'),{timeout:90000});
   const f=await(await p.$('.jsketcher-app iframe')).contentFrame();const ids=await p.evaluate(()=>registry.list().map(x=>x.id));for(const id of ['inspect-rectangle-dimensions','edit-rectangle-dimensions'])assert.ok(ids.includes(id));
   const cap=await p.evaluate(()=>registry.execute({windowId:'w0',command:'inspect-rectangle-creation',args:{}}));await p.evaluate(args=>registry.execute({windowId:'w0',command:'create-rectangle-sketch',args}),{revision:cap.revision,unit:'millimeter',origin:[10,20],width:100,height:50,depth:7});
   let info=await p.evaluate(()=>registry.execute({windowId:'w0',command:'inspect-rectangle-dimensions',args:{}}));assert.equal(info.candidates.length,1);assert.equal(info.candidates[0].width,100);
   await p.evaluate(args=>registry.execute({windowId:'w0',command:'edit-rectangle-dimensions',args}),{revision:info.revision,faceId:info.candidates[0].faceId,width:120,height:45});
   const stale=await p.evaluate(async args=>{try{await registry.execute({windowId:'w0',command:'edit-rectangle-dimensions',args});return ''}catch(e){return e.name}},{revision:info.revision,faceId:info.candidates[0].faceId,width:140,height:35});assert.equal(stale,'AbortError');
   await f.evaluate(()=>document.querySelector('[data-action-id="menu.craft"]').click());await f.waitForFunction(()=>/Edit rectangle dimensions/i.test(document.body.innerText));await f.evaluate(()=>[...document.querySelectorAll('*')].find(e=>e.children.length===0&&/^Edit rectangle dimensions$/i.test(e.textContent.trim())).click());
   await p.waitForSelector('dialog.jsketcher-rectangle-dialog[open]');assert.equal(await p.$eval('dialog input[name=width]',e=>e.value),'120');await p.$eval('dialog input[name=width]',e=>e.value='150');await p.$eval('dialog input[name=height]',e=>e.value='30');await p.click('dialog button[type=submit]');await p.waitForFunction(()=>!document.querySelector('dialog.jsketcher-rectangle-dialog'),{timeout:60000});
   info=await p.evaluate(()=>registry.execute({windowId:'w0',command:'inspect-rectangle-dimensions',args:{}}));assert.equal(info.candidates[0].width,150);assert.equal(info.candidates[0].height,30);
   await p.evaluate(()=>prompts.push('/rect.jsketcher.json'));await f.evaluate(()=>__CAD_APP.actionService.run('Save'));await p.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('syncing with the server'),{timeout:30000});
   await p.evaluate(()=>launch());await p.waitForFunction(()=>document.querySelectorAll('.app-status')[1]?.textContent.startsWith('New model.'),{timeout:90000});const f2=await(await p.$$('.jsketcher-app iframe'))[1].contentFrame();await p.evaluate(()=>pick.push('/rect.jsketcher.json'));await f2.evaluate(()=>__CAD_APP.actionService.run('NativeFormatImport'));await p.waitForFunction(()=>document.querySelectorAll('.app-status')[1]?.textContent.startsWith('Opened /rect.jsketcher.json'),{timeout:90000});
   const reopened=await p.evaluate(()=>registry.execute({windowId:'w1',command:'inspect-rectangle-dimensions',args:{}}));assert.equal(reopened.candidates[0].width,150);assert.equal(reopened.candidates[0].height,30);console.log(`PASS ${phone?'phone':'desktop'} command, menu edit, stale revision, in-memory save/reopen`);
  }finally{await context.close();}
 }
 const context=await b.createBrowserContext(),p=await context.newPage(),session=await p.createCDPSession();try{let hits=0;await session.send('Fetch.enable',{patterns:[{urlPattern:'*/lib-assets/jsketcher-occ-engine/occt.wasm',requestStage:'Request'}]});session.on('Fetch.requestPaused',e=>{hits++;void session.send('Fetch.fulfillRequest',{requestId:e.requestId,responseCode:503,body:''})});await p.goto(base.href);await p.waitForFunction('window.launch');const start=Date.now();await p.evaluate(()=>launch());await p.waitForFunction(()=>document.querySelector('.app-status')?.textContent.includes('CAD could not finish starting'),{timeout:15000});assert.equal(hits,1);assert.ok(Date.now()-start<15000);console.log('PASS host reports actual WASM startup failure promptly');}finally{await context.close();}
}finally{b.disconnect()}
