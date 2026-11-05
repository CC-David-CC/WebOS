// Actual CAD/app frames and file coordinator; only the host mirror is in memory.
// Hold completed real CAD results to test destruction of their Promise realm.
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.JSKETCHER_HOST_URL),cdp=new URL(process.env.CODI_TEST_CDP);
for(const u of [base,cdp])if(!['127.0.0.1','localhost','[::1]'].includes(u.hostname))throw Error('Loopback only');
const browser=await puppeteer.connect({browserURL:cdp.href,protocolTimeout:120000}),context=await browser.createBrowserContext(),page=await context.newPage();let passed=false;
try{
 await page.evaluateOnNewDocument(()=>{
  if(window===top)return;
  if(Object.getOwnPropertyDescriptor(window,'__CAD_APP'))throw Error('Unexpected pre-existing CAD application descriptor.');
  Object.defineProperty(window,'__CAD_APP',{configurable:true,enumerable:true,set(context){
   const manager=context?.projectManager,original=manager?.restoreSnapshotBytesInEmptyWorkspace;
   if(typeof original!=='function')throw Error('CAD restore hook unavailable at application publication.');
   manager.restoreSnapshotBytesInEmptyWorkspace=async function(...args){
    const result=await original.apply(this,args);
    if(parent.holdRestoreReturn){window.restoreReturnHeld=true;return new Promise(()=>{});}
    return result;
   };
   window.restoreHookInstalled=true;Object.defineProperty(window,'__CAD_APP',{configurable:true,enumerable:true,writable:true,value:context});
  }});
 });
 await page.goto(base.href);await page.waitForFunction('window.launch');await page.evaluate(()=>launch());
 const ready=index=>page.waitForFunction(i=>views[i]?.view.element.querySelector('.app-status')?.textContent.startsWith('New model.'),{timeout:90000},index);
 await ready(0);
 await page.evaluate(()=>{window.seedSave=registry.execute({windowId:'w0',command:'inspect',args:{}}).then(info=>registry.execute({windowId:'w0',command:'save',args:{revision:info.revision,path:'/seed.jsketcher.json'}}));});
 assert.equal((await page.evaluate(()=>seedSave)).path,'/seed.jsketcher.json');
 const first=await(await page.$('.jsketcher-app iframe')).contentFrame();
 await first.evaluate(()=>{
  const manager=__CAD_APP.projectManager,original=manager.prepareHostSave;
  manager.prepareHostSave=async function(...args){await original.apply(this,args);window.saveReturnHeld=true;return new Promise(()=>{});};
 });
 await page.evaluate(()=>{window.closedSave=null;registry.execute({windowId:'w0',command:'inspect',args:{}}).then(info=>registry.execute({windowId:'w0',command:'save',args:{revision:info.revision}})).then(()=>closedSave={ok:true},e=>closedSave={ok:false,name:e.name});});
 await first.waitForFunction('window.saveReturnHeld',{timeout:30000});
 await page.evaluate(()=>closeView(0));
 await page.waitForFunction('closedSave!==null',{timeout:3000});
 assert.deepEqual(await page.evaluate(()=>closedSave),{ok:false,name:'AbortError'});
 assert.equal(await page.evaluate(()=>views[0].documentOperations.state.kind),null);
 await page.evaluate(()=>{window.holdRestoreReturn=true;window.releasedSnapshots=0;launch();});await ready(1);
 const second=await(await page.$('.jsketcher-app iframe')).contentFrame();
 await page.evaluate(()=>pick.push('/seed.jsketcher.json'));
 await second.evaluate(()=>__CAD_APP.actionService.run('NativeFormatImport'));
 await page.waitForFunction(()=>views[1].view.element.querySelector('.jsketcher-staging')?.contentWindow?.restoreReturnHeld===true,{timeout:90000});
 assert.equal(await page.evaluate(()=>releasedSnapshots),0,'snapshot stays leased during actual restore');
 await page.evaluate(()=>closeView(1));
 await page.waitForFunction('releasedSnapshots===1',{timeout:3000});
 assert.equal(await page.evaluate(()=>views[1].documentOperations.state.kind),null);
 await page.evaluate(()=>{window.holdRestoreReturn=false;launch();});await ready(2);
 assert.equal(await page.evaluate(()=>views[2].documentOperations.busy),false);
 await page.evaluate(()=>closeView(2));passed=true;
 console.log('PASS closed real CAD Promise realms settle parent Save and release opened snapshot leases');
}finally{
 if(passed)await context.close();else console.error('Retained failing context',context.id);
 browser.disconnect();
}
