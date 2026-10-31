import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const user=process.env.CODI_TEST_USER;
if(!/^browserprobe[0-9a-f]{10}$/.test(user||''))throw Error('Set a disposable browserprobe username');
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.setViewport({width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto('https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 const html='<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0}main{width:1600px;height:400px;background:linear-gradient(90deg,red,blue)}</style><main>Drag horizontally</main><script>onscroll=()=>location.hash="x"+Math.round(scrollX)</script>';
 await page.evaluate(html=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot,p=r.querySelector('input[type=file]'),dt=new DataTransfer();dt.items.add(new File([html],'wide.html',{type:'text/html'}));p.files=dt.files;p.dispatchEvent(new Event('change',{bubbles:true}));},html);
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value.includes('page-2.html'),{timeout:30000});
 await new Promise(r=>setTimeout(r,1000));
 const rect=await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}});
 const x=Math.round(rect.x+rect.width*.8),y=Math.round(rect.y+rect.height*.4),cdp=await page.createCDPSession();
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
 for(let i=1;i<=6;i++)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x-i*35,y}]});
 await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await page.waitForFunction(()=>{const s=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value||'';return /#x[1-9][0-9]*/.test(s);},{timeout:15000});
 const address=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('[aria-label="Website address"]').value);
 assert.match(address,/#x[1-9]/);console.log('PASS horizontal touch drag moved the real embedded page:',address.split('#').at(-1));
}finally{await context.close();await browser.disconnect()}
