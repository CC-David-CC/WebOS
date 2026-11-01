import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19507/';
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(base))throw Error('Requires an isolated loopback preview.');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000});
for(const phone of [false,true]){
 const context=await browser.createBrowserContext(),page=await context.newPage(),name='nboutput'+Date.now().toString().slice(-8)+(phone?'p':'d');
 const setup=async p=>{await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});await p.goto(base)};
 try{
  await setup(page);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/output.ipynb',JSON.stringify({nbformat:4,nbformat_minor:5,metadata:{kernelspec:{name:'python',display_name:'Python (Pyodide)',language:'python'}},cells:[{cell_type:'code',execution_count:null,metadata:{},outputs:[],source:'measurements = [10, 14]\nprint("mean", sum(measurements) / len(measurements))'}]}),null);await f.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/output.ipynb')});
  await page.waitForFunction(()=>document.querySelector('.notebook-app .app-status')?.textContent==='Notebook opened from My files.',{timeout:120000});const frame=await (await page.$('.notebook-app iframe')).contentFrame();
  // Running an imported notebook can present the real Jupyter kernel selector.
  const run=frame.evaluate(()=>window.jupyterapp.commands.execute('notebook:run-cell'));
  await frame.waitForSelector('.jp-Dialog-button.jp-mod-accept',{timeout:30000});if(phone)await (await frame.$('.jp-Dialog-button.jp-mod-accept')).tap();else await frame.click('.jp-Dialog-button.jp-mod-accept');await run;
  await frame.waitForFunction(()=>JSON.stringify(window.jupyterapp.shell.currentWidget.context.model.toJSON().cells[0].outputs).includes('mean 12.0'),{timeout:120000});
  await page.waitForFunction(async()=>{try{return new TextDecoder().decode((await(await mirrorFileContext()).files.read('/output.ipynb')).data).includes('mean 12.0')}catch{return false}},{timeout:45000});
  const stored=await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.sync();return new TextDecoder().decode((await(await serverFileContext()).files.read('output.ipynb')).data)});assert.match(stored,/mean 12\.0/);
  const fresh=await browser.createBrowserContext(),q=await fresh.newPage();try{await setup(q);await q.waitForSelector('[aria-label=Username]');await q.type('[aria-label=Username]',name);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});await q.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/output.ipynb'));await q.waitForFunction(()=>document.querySelector('.notebook-app .app-status')?.textContent==='Notebook opened from My files.',{timeout:120000});const reopened=await q.evaluate(()=>document.querySelector('.notebook-app iframe').contentWindow.jupyterapp.shell.currentWidget.context.model.toJSON());assert.match(JSON.stringify(reopened.cells[0].outputs),/mean 12\.0/);assert.equal(reopened.cells[0].execution_count,1);}finally{await fresh.close()}
  console.log('PASS',phone?'phone-sized':'desktop','Pyodide cell output autosaves, server sync, fresh account reopen');
 }finally{await context.close()}
}
await browser.disconnect();
