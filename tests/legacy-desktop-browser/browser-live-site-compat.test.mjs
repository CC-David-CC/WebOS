import puppeteer from 'puppeteer-core';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const user=process.env.CODI_TEST_USER;
if(!/^browserprobe[0-9a-f]{10}$/.test(user||''))throw Error('Set a disposable browserprobe username');
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage(),phone=process.env.CODI_PHONE==='1';
try{
 await page.setViewport(phone?{width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true}:{width:1366,height:950});
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(u,...a)});
 await page.goto(process.env.CODI_TEST_URL||'https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));await page.waitForFunction(()=>[...([...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled),{timeout:180000});
 await fs.mkdir('.build/browser-live-site-compat',{recursive:true});
 const sites=process.env.CODI_REFERENCE_ONLY==='1'?[['reference','https://example.com/']]:process.env.CODI_STRESS==='1'?Array.from({length:5},(_,i)=>[`mcmaster-${i}`,'https://www.mcmaster.com/']):[['reference','https://example.com/'],['grainger','https://www.grainger.com/'],['mcmaster','https://www.mcmaster.com/']];
 for(const [name,url] of sites){
  await page.evaluate(url=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;r.querySelector('[aria-label="Website address"]').value=url;r.querySelector('form').requestSubmit()},url);
  await new Promise(resolve=>setTimeout(resolve,process.env.CODI_STRESS==='1'?8000:18000));
  const handle=await page.evaluateHandle(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas'));
  await handle.asElement().screenshot({path:`.build/browser-live-site-compat/${phone?'phone':'desktop'}-${name}.png`});
  const state=await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;return {status:r.querySelector('.status')?.textContent,address:r.querySelector('[aria-label="Website address"]')?.value}});
  console.log(JSON.stringify({name,phone,...state}));
  assert.doesNotMatch(state.status||'',/Engine buffer outside WASM memory|Gecko aborted|Engine command timed out/i);
 }
}finally{await context.close();await browser.disconnect()}
