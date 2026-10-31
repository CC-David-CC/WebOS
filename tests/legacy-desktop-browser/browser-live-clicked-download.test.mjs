import {chooseRoot} from './browser-choose-root.mjs';
import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {writeFile,unlink} from 'node:fs/promises';
const name=process.env.CODI_TEST_USER;
if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Set a disposable browserprobe username');
const fixture=`/tmp/${name}.html`;
await writeFile(fixture,'<style>body {font: 32px sans-serif}</style><a href="data:application/octet-stream,codi%20file%20gateway%20probe%2020261030" download="clicked.txt">Download test</a>');
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto('https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 const picker=await page.evaluateHandle(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('input[type=file]'));
 await picker.asElement().uploadFile(fixture);await new Promise(r=>setTimeout(r,2500));
 const rect=await page.evaluate(()=>{const e=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas').getBoundingClientRect();return {x:e.x,y:e.y}});
 if(process.env.CODI_PHONE==='1')await page.touchscreen.tap(rect.x+60,rect.y+30);else await page.mouse.click(rect.x+60,rect.y+30);
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.download-row button')?.textContent==='Save to My files',{timeout:30000});
 page.once('dialog',d=>d.accept('gateway-probe.txt'));await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('.download-row button').click());await chooseRoot(page);
 await page.waitForFunction(()=>![...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.download-row'),{timeout:30000});
 const actual=await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();return new TextDecoder().decode((await(await serverFileContext()).files.read('gateway-probe.txt')).data)});assert.equal(actual,'codi file gateway probe 20261030');
 await page.evaluate(async()=>{const c=await mirrorFileContext(),f=await c.files.read('/gateway-probe.txt');await c.files.remove('/gateway-probe.txt',f.version);await c.files.sync()});
 console.log('PASS live clicked download, My files and server copy');
}finally{await context.close();await browser.disconnect();await unlink(fixture).catch(()=>{});}
