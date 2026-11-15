import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18303/');
 await page.evaluate(async()=>{
  const catalog=await (await fetch('/apps.json')).json(),record=catalog.apps.find(x=>x.id==='arduino-simulator');
  const module=await import(`/apps/arduino-simulator/${record.bundleSHA256}/index.mjs`);
  window.workers=[];window.Worker=class{constructor(){this.terminated=false;window.workers.push(this)}postMessage(){}terminate(){this.terminated=true}emit(data){this.onmessage?.({data})}};
  window.nativeCalls=0;window.confirm=()=>{window.nativeCalls++;return false};window.desktopCalls=0;
  const make=(tag,cls='',value='')=>{const e=document.createElement(tag);e.className=cls;e.textContent=value;return e};
  const textButton=(label,handler)=>{const b=make('button','',label);b.addEventListener('click',handler);return b};
  const files={stat:async()=>{throw Error('File not found.')},write:async()=>({version:'local-v1',status:'conflict'})};
  const host={signal:new AbortController().signal,ui:{make,textButton,confirm:async()=>{window.desktopCalls++;return window.deferConfirm?await new Promise(resolve=>window.resolveConfirm=resolve):false}},storage:{signedInSubject:()=> 'test-account',mirrorFileContext:async()=>({valid:()=>true,path:p=>p,files}),pickFile:async()=>null}};
  window.view=module.mount(host);document.body.replaceChildren(window.view.element);
 });
 const click=async label=>page.evaluate(label=>[...document.querySelectorAll('button')].find(x=>x.textContent===label).click(),label);
 await page.$eval('.circuit-source',e=>{e.value+='\n* edited';e.dispatchEvent(new Event('input',{bubbles:true}))});
 await click('RC step');await page.waitForTimeout?.(50);const dialog=await page.evaluate(()=>({native:window.nativeCalls,desktop:window.desktopCalls}));
 assert.deepEqual(dialog,{native:0,desktop:1},'replacement uses the desktop confirmation');
 await page.evaluate(()=>window.deferConfirm=true);await click('RC step');await page.waitForFunction(()=>!!window.resolveConfirm);await page.$eval('.circuit-source',e=>{e.value+='\n* changed during confirmation';e.dispatchEvent(new Event('input',{bubbles:true}))});await page.evaluate(()=>window.resolveConfirm(true));await page.waitForFunction(()=>document.querySelector('.circuit-status').textContent.includes('changed while opening'));assert.match(await page.$eval('.circuit-source',e=>e.value),/changed during confirmation/);
 await click('Save to My files');await page.waitForFunction(()=>/Saved|Could not save/.test(document.querySelector('.circuit-status').textContent));const saveStatus=await page.$eval('.circuit-status',e=>e.textContent);
 assert.match(saveStatus,/conflict/i);
 await click('Run');await page.$eval('.circuit-source',e=>{e.value+='\n* newer';e.dispatchEvent(new Event('input',{bubbles:true}))});
 const result=await page.evaluate(()=>{const w=window.workers.at(-1),terminated=w.terminated;w.emit({type:'result',points:1,series:[{name:'v(out)',values:[5]}]});return {terminated,output:document.querySelector('.circuit-results').textContent}});
 assert.equal(result.terminated,true,'editing terminates the old simulation');assert.equal(result.output,'','old simulation cannot replace current results');
 console.log('PASS themed discard confirmation, conflict reporting, and stale simulation guard (mock storage and worker)');
}finally{await context.close();await browser.disconnect()}
