import puppeteer from 'puppeteer-core';
const b=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),c=await b.createBrowserContext(),p=await c.newPage();
try{
 await p.setViewport({width:1280,height:1000});await p.goto('http://127.0.0.1:18195/demo/index.html');await p.waitForFunction(()=>[...(document.querySelector('.window-content')?.shadowRoot?.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled),{timeout:180000});
 await p.click('#open');await p.waitForFunction(()=>{const r=[...document.querySelectorAll('.window-content')];return r.length===2&&r.every(e=>[...(e.shadowRoot?.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled))},{timeout:180000});
 const go=async(i,url)=>p.evaluate(({i,url})=>{const a=document.querySelectorAll('.window-content')[i].shadowRoot.querySelector('[aria-label="Website address"]');a.value=url;a.form.requestSubmit()},{i,url});
 await go(0,'http://fixture.example/slow');await p.waitForFunction(async()=>{const r=await fetch('/test-calls');return (await r.json()).resolved.includes('SLOW_REQUEST')},{timeout:30000});
 await go(1,'http://fixture.example/after');await p.waitForFunction(async()=>{const r=await fetch('/test-calls');return (await r.json()).resolved.includes('AFTER_RESPONSE')},{timeout:30000});
 await p.evaluate(()=>[...document.querySelectorAll('.window-content')[0].shadowRoot.querySelectorAll('button')].find(x=>x.textContent==='Stop').click());
 await p.waitForFunction(()=>document.querySelectorAll('.window-content')[0].shadowRoot.querySelector('.status').textContent==='Stopped.',{timeout:5000});
 const second=await p.evaluate(()=>{const r=document.querySelectorAll('.window-content')[1].shadowRoot;return {address:r.querySelector('[aria-label="Website address"]').value,status:r.querySelector('.status').textContent}});
 if(second.address!=='http://fixture.example/after'||/failed|error|terminated/i.test(second.status))throw Error('Second window changed: '+JSON.stringify(second));
 console.log('PASS stopping a slow navigation did not disrupt the other Browser window');
}finally{await c.close();await b.disconnect()}
