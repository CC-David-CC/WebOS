import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.setViewport({width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true});
 await page.goto('http://127.0.0.1:18199/demo/');
 await page.evaluate(()=>{document.querySelector('body>header').style.display='none';document.querySelector('#windows').style.cssText='display:block;padding:0';document.querySelector('.window').style.cssText='width:412px;height:860px;display:flex;flex-direction:column';});
 await page.waitForFunction(()=>[...([...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled),{timeout:180000});
 const html='<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0}main{width:400px;height:1600px;background:linear-gradient(180deg,red,blue)}</style><main>Drag vertically</main><script>onscroll=()=>location.hash="x"+Math.round(scrollY)</script>';
 await page.evaluate(html=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot,p=r.querySelector('input[type=file]'),dt=new DataTransfer();dt.items.add(new File([html],'wide.html',{type:'text/html'}));p.files=dt.files;p.dispatchEvent(new Event('change',{bubbles:true}));},html);
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value.includes('page-2.html'),{timeout:30000});
 await new Promise(r=>setTimeout(r,1000));
 const rect=await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}});
 await page.evaluate(()=>{const c=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas');window.__testPointerMoves=[];c.addEventListener('pointermove',e=>window.__testPointerMoves.push([e.clientX,e.clientY]),{once:false});});
 const x=Math.round(rect.x+rect.width*.4),y=Math.round(rect.y+rect.height*.8),cdp=await page.createCDPSession();
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
 for(let i=1;i<=6;i++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-i*35}]});await new Promise(r=>setTimeout(r,40));}
 await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await page.waitForFunction(()=>{const s=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value||'';return /#x[1-9][0-9]*/.test(s);},{timeout:15000});
 await new Promise(r=>setTimeout(r,2000)); // Allow queued input and navigation status to settle.
 const address=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('[aria-label="Website address"]').value);
 assert.match(address,/#x[1-9]/);assert.ok(Number(address.split('#x').at(-1))>=170,'The six-step 210px drag should not lose most of its movement');console.log('PASS vertical touch drag moved the real embedded page:',address.split('#').at(-1),'pointer moves:',JSON.stringify(await page.evaluate(()=>window.__testPointerMoves)));
 // Compare with a single move of the same distance on a fresh guest page.
 await page.evaluate(html=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot,p=r.querySelector('input[type=file]'),dt=new DataTransfer();dt.items.add(new File([html],'wide2.html',{type:'text/html'}));p.files=dt.files;p.dispatchEvent(new Event('change',{bubbles:true}));},html);
 await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value.includes('page-3.html'),{timeout:30000});
 await new Promise(r=>setTimeout(r,1000));
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
 await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-210}]});
 await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await page.waitForFunction(()=>{const s=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value||'';return /#x[1-9][0-9]*/.test(s);},{timeout:15000});
 await new Promise(r=>setTimeout(r,2000));
 const single=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('[aria-label="Website address"]').value);
 console.log('Single-move final offset:',single.split('#').at(-1));

}finally{await context.close();await browser.disconnect()}
