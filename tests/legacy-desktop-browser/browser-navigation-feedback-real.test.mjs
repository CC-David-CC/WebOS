import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try {
 await page.setViewport(process.env.CODI_PHONE==='1'?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1280,height:900});
 await page.goto('http://127.0.0.1:18195/demo/index.html');
 await page.waitForFunction(()=>{const r=document.querySelector('.window-content')?.shadowRoot;return r&&[...r.querySelectorAll('button')].some(b=>b.textContent==='Stop'&&!b.disabled)},{timeout:180000});
 await page.evaluate(()=>{const r=document.querySelector('.window-content').shadowRoot,s=r.querySelector('.status');window.testStatuses=[];new MutationObserver(()=>window.testStatuses.push(s.textContent)).observe(s,{childList:true,characterData:true,subtree:true});});
 const go=url=>page.evaluate(url=>{const a=document.querySelector('.window-content').shadowRoot.querySelector('[aria-label="Website address"]');a.value=url;a.form.requestSubmit()},url);
 const status=expected=>page.waitForFunction(expected=>document.querySelector('.window-content').shadowRoot.querySelector('.status').textContent===expected,{timeout:30000},expected);
 const count=path=>page.evaluate(async path=>(await(await fetch('/test-calls')).json()).resolved.filter(x=>x==='response:'+path).length,path);
 const response=(path,before)=>page.waitForFunction(async(path,before)=>(await(await fetch('/test-calls')).json()).resolved.filter(x=>x==='response:'+path).length>before,{timeout:30000},path,before);
 let seen=await count('/ok');await go('http://fixture.example/ok');await response('/ok',seen);await status('Page loaded.');console.log('PASS 200 displays page loaded');
 seen=await count('/missing');await go('http://fixture.example/missing');await response('/missing',seen);await status('The site returned HTTP 404.');console.log('PASS 404 displayed');
 let prior=await count('/missing');await go('http://fixture.example/redirect');await response('/missing',prior);await status('The site returned HTTP 404.');console.log('PASS HTTP redirect final status');
 prior=await count('/missing');await page.evaluate(()=>window.testStatuses=[]);await go('http://fixture.example/chain');await response('/missing',prior);await status('The site returned HTTP 404.');
 const observed=await page.evaluate(()=>window.testStatuses);if(observed.some(x=>x.startsWith('Could not load')))throw Error('Script redirect was reported as an error: '+JSON.stringify(observed));console.log('PASS script redirect avoids false cancellation error');
 await go('http://fixture.example/slow');await page.waitForFunction(async()=>(await(await fetch('/test-calls')).json()).resolved.includes('request:/slow'),{timeout:30000});
 await page.evaluate(()=>[...document.querySelector('.window-content').shadowRoot.querySelectorAll('button')].find(b=>b.textContent==='Stop').click());await status('Stopped.');await new Promise(r=>setTimeout(r,1500));await status('Stopped.');console.log('PASS Stop remains acknowledged');
 await go('https://www.youtube.com/');await page.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('.status').textContent.includes('blocked by the server network policy'),{timeout:30000});console.log('PASS policy block retains its explanation');
 await go('https://fixture.example/ok');await status('Could not load the page. Check the address or connection.');console.log('PASS connection failure explained');
 await go('http://fixture.example/ok?recovery');await response('/ok?recovery',0);await status('Page loaded.');console.log('PASS subsequent navigation recovers');
} finally {await context.close();await browser.disconnect();}
