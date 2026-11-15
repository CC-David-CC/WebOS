import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.setViewport({width:1366,height:950});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;let failed=false;window.fetch=(url,...args)=>{const u=String(url);if(u.endsWith('assets/terminal/v2/image.json'))return Promise.resolve(new Response('',{status:404}));if(!failed&&u.endsWith('/browser-relay/challenge')){failed=true;return Promise.resolve(new Response('upstream unavailable',{status:502}))}return f(url,...args)}});
 await page.goto('http://127.0.0.1:18191/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]','browserprobecb77a00002');await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent.includes('temporarily unavailable'), {timeout:30000});
 const result=await page.evaluate(()=>{const root=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;return {message:root.querySelector('.status').textContent,reset:[...root.querySelectorAll('button')].find(b=>b.textContent==='Reset engine')?.disabled}});
 assert.match(result.message,/Select Reset engine/);assert.equal(result.reset,false);
 await page.evaluate(()=>{const root=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...root.querySelectorAll('button')].find(b=>b.textContent==='Reset engine').click()});
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 console.log('PASS relay outage explains recovery and Reset engine reconnects');
}finally{await context.close();await browser.disconnect()}
