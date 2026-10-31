import puppeteer from 'puppeteer-core';
const b=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),c=await b.createBrowserContext(),p=await c.newPage();
try{
 await p.setViewport({width:1280,height:900});await p.goto('http://127.0.0.1:18195/demo/index.html');await p.waitForFunction(()=>document.querySelector('.window-content')?.shadowRoot?.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 const go=async url=>p.evaluate(url=>{const a=document.querySelector('.window-content').shadowRoot.querySelector('[aria-label="Website address"]');a.value=url;a.form.requestSubmit()},url);
 await go('http://fixture.example/slow');await p.waitForFunction(async()=>{const r=await fetch('/test-calls');return (await r.json()).resolved.includes('SLOW_REQUEST')},{timeout:30000});
 const started=Date.now();await p.evaluate(()=>[...document.querySelector('.window-content').shadowRoot.querySelectorAll('button')].find(x=>x.textContent==='Stop').click());
 await p.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('.status').textContent==='Stopped.',{timeout:5000});
 const state=await p.evaluate(async()=>(await(await fetch('/test-calls')).json()).resolved);
 if(state.includes('SLOW_RESPONSE'))throw Error('Stop completed only after the response');console.log('PASS Stop completed before delayed response in',Date.now()-started,'ms');
 await go('http://fixture.example/after');await p.waitForFunction(async()=>{const r=await fetch('/test-calls');return (await r.json()).resolved.includes('AFTER_RESPONSE')},{timeout:30000});
 await p.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('[aria-label="Website address"]').value==='http://fixture.example/after',{timeout:15000});
 console.log('PASS later navigation remained usable');
 await p.evaluate(()=>{const r=document.querySelector('.window-content').shadowRoot;const a=r.querySelector('[aria-label="Website address"]');a.value='http://fixture.example/slow';a.form.requestSubmit();[...r.querySelectorAll('button')].find(x=>x.textContent==='Stop').click()});
 await p.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('.status').textContent==='Stopped.',{timeout:5000});
 console.log('PASS immediate Stop returned');
 await go('http://fixture.example/final');await p.waitForFunction(()=>document.querySelector('.window-content').shadowRoot.querySelector('[aria-label="Website address"]').value==='http://fixture.example/final',{timeout:20000});
 console.log('PASS navigation after immediate Stop remained usable');
}finally{await c.close();await b.disconnect()}
