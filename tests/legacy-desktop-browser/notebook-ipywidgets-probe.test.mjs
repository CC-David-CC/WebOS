import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
import {randomBytes} from 'node:crypto';
const require=createRequire(process.env.PUPPETEER_CORE_PATH||import.meta.url);
const puppeteer=require('puppeteer-core');
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19752/';
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(base))throw Error('Requires an isolated loopback preview');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000});
try{
 for(const mode of ['phone']){
  const phone=mode==='phone';
  const context=await browser.createBrowserContext(),page=await context.newPage(),name='plot'+randomBytes(6).toString('hex');
  try{
   await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:mode==='4k'?{width:3840,height:2160}:{width:1366,height:900});
   await page.evaluateOnNewDocument(()=>{const fetch0=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):fetch0(u,...a)});
   await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
   await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/inline.ipynb',JSON.stringify({nbformat:4,nbformat_minor:5,metadata:{kernelspec:{name:'python',display_name:'Python (Pyodide)',language:'python'}},cells:[{cell_type:'code',execution_count:null,metadata:{},outputs:[],source:"import ipywidgets as widgets\nw = widgets.IntSlider(value=2, min=0, max=10)\ndisplay(w)"}]}),null);await f.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/inline.ipynb')});
   await page.waitForFunction(()=>document.querySelector('.notebook-app .app-status')?.textContent==='Notebook opened from My files.',{timeout:120000});
   const frame=await(await page.$('.notebook-app iframe')).contentFrame();
   const run=phone?(await page.$('.notebook-mobile-controls button')).tap():frame.evaluate(()=>window.jupyterapp.commands.execute('notebook:run-cell'));
   const dialog=await frame.waitForSelector('.jp-Dialog-button.jp-mod-accept',{timeout:5000}).catch(()=>null);if(dialog){if(phone)await dialog.tap();else await dialog.click();}await run;
   await frame.waitForFunction(()=>{const outputs=window.jupyterapp.shell.currentWidget?.context?.model?.toJSON()?.cells?.[0]?.outputs||[];return outputs.some(x=>x.output_type==='error'||x.data?.['application/vnd.jupyter.widget-view+json'])},{timeout:90000});
   const report=await frame.evaluate(()=>({outputs:window.jupyterapp.shell.currentWidget.context.model.toJSON().cells[0].outputs,slider:!!document.querySelector('[role=slider],input[type=range]')}));console.log('WIDGET-PROBE',mode,JSON.stringify(report));
  }finally{await context.close()}
 }
}finally{await browser.disconnect()}
