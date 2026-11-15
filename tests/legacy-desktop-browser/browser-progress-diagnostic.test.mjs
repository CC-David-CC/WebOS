import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try {
 await page.setViewport({width:1280,height:900});await page.goto('http://127.0.0.1:18195/demo/index.html');
 await page.waitForFunction(()=>document.querySelector('.window-content')?.shadowRoot?.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 const go=url=>page.evaluate(url=>{const a=document.querySelector('.window-content').shadowRoot.querySelector('[aria-label="Website address"]');a.value=url;a.form.requestSubmit()},url);
 const last=()=>page.evaluate(()=>{const text=document.querySelector('.window-content').shadowRoot.querySelector('pre').textContent;const line=text.split('\n').filter(x=>x.startsWith('PROGRESS ')).at(-1);return line?JSON.parse(line.slice(9)):null});
 const responses=path=>page.evaluate(async path=>(await (await fetch('/test-calls')).json()).resolved.filter(x=>x==='response:'+path).length,path);
 const response=(path,count)=>page.waitForFunction(async (path,count)=>(await (await fetch('/test-calls')).json()).resolved.filter(x=>x==='response:'+path).length>count,{timeout:30000},path,count);
 for(const path of ['/ok','/missing','/redirect']){
   const target=path==='/redirect'?'/missing':path, count=await responses(target);const before=await last();await go('http://fixture.example'+path);await response(target,count);
   await page.waitForFunction(n=>{const t=document.querySelector('.window-content').shadowRoot.querySelector('pre').textContent;const l=t.split('\n').filter(x=>x.startsWith('PROGRESS ')).at(-1);return l&&JSON.parse(l.slice(9)).stops>n},{timeout:20000},before?.stops??0);
   const state=await last(),expected=path==='/ok'?200:404;if(state.progress!==2||state.progressResult!==0||state.httpStatus!==expected)throw Error('Unexpected HTTP result for '+path+': '+JSON.stringify(state));console.log(path,JSON.stringify(state));
 }
 const chainCount=await responses('/missing');await go('http://fixture.example/chain');await response('/missing',chainCount);await new Promise(r=>setTimeout(r,1500));
 {const state=await last();if(state.progress!==2||state.httpStatus!==404)throw Error('Script redirect did not finish on the 404');console.log('script redirect',JSON.stringify(state));}
 await go('http://fixture.example/slow');await page.waitForFunction(async()=>(await(await fetch('/test-calls')).json()).resolved.includes('request:/slow'),{timeout:30000});
 await page.evaluate(()=>[...document.querySelector('.window-content').shadowRoot.querySelectorAll('button')].find(b=>b.textContent==='Stop').click());
 await page.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('.status').textContent==='Stopped.',{timeout:10000});
 await new Promise(r=>setTimeout(r,1500));{const state=await last();if(state.progress!==2||state.progressResult===0)throw Error('Cancellation was not reported');console.log('/slow stopped',JSON.stringify(state));}
 await go('http://fixture.example/ok?after-stop');await response('/ok?after-stop',0);await new Promise(r=>setTimeout(r,1500));{const state=await last();if(state.progress!==2||state.progressResult!==0||state.httpStatus!==200)throw Error('Navigation after stop failed');console.log('/ok after stop',JSON.stringify(state));}
 const beforeBlocked=await last();await go('https://www.youtube.com/');
 await page.waitForFunction(n=>{const t=document.querySelector('.window-content').shadowRoot.querySelector('pre').textContent;const l=t.split('\n').filter(x=>x.startsWith('PROGRESS ')).at(-1);return l&&JSON.parse(l.slice(9)).stops>n},{timeout:30000},beforeBlocked?.stops??0);
 {const state=await last();if(state.progress!==2||state.progressResult===0)throw Error('Blocked request did not report a network error');console.log('blocked destination',JSON.stringify(state));}
 const beforeTLS=await last();await go('https://fixture.example/ok');
 await page.waitForFunction(n=>{const t=document.querySelector('.window-content').shadowRoot.querySelector('pre').textContent;const l=t.split('\n').filter(x=>x.startsWith('PROGRESS ')).at(-1);return l&&JSON.parse(l.slice(9)).stops>n},{timeout:30000},beforeTLS?.stops??0);
 {const state=await last();if(state.progress!==2||state.progressResult===0)throw Error('TLS failure did not report a network error');console.log('TLS failure',JSON.stringify(state));}
} finally {await context.close();await browser.disconnect();}
