import puppeteer from 'puppeteer-core';import assert from 'node:assert/strict';
const b=await puppeteer.connect({browserURL:'http://127.0.0.1:19255'}),c=await b.createBrowserContext(),p=await c.newPage(),user='phoneweb'+Date.now().toString().slice(-8),errors=[];
p.on('pageerror',e=>errors.push(e.message));
try{
 await p.setViewport({width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:1});
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await p.goto(process.env.CODI_TEST_DESKTOP_URL||'http://127.0.0.1:18141/');await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 const html=`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;background:#ddeeff;font:20px sans-serif}input{position:absolute;left:10px;top:10px;width:240px;height:44px;font:22px sans-serif}article{margin-top:80px;height:1600px;background:linear-gradient(#f44,#44f)}</style><input id="field" placeholder="type here"><article>Scroll test</article><script>document.getElementById('field').oninput=e=>{location.hash=encodeURIComponent(e.target.value)};</script>`;
 await p.evaluate(async html=>{const f=await mirrorFileContext();await f.files.write('/touch.html',html);},html);
 await p.click('[aria-label=Applications]');await p.waitForSelector('[aria-label="Browser"]');await p.click('[aria-label="Browser"]');
 await p.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent==='Ready',{timeout:180000});
 const visible=await p.evaluate(()=>{const host=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot),status=host.shadowRoot.querySelector('.status').getBoundingClientRect(),bounds=host.getBoundingClientRect();return status.height>0&&status.top>=bounds.top&&status.bottom<=bounds.bottom+1;});
 assert.ok(visible,'Browser status must fit within the phone window');
 await p.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelectorAll('button').forEach(x=>{if(x.textContent==='Open from My files')x.click()}));
 await p.waitForSelector('[aria-label="Choose file touch.html"]',{timeout:15000});await p.click('[aria-label="Choose file touch.html"]');
 await p.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value.includes('page-2.html'),{timeout:30000});
 await new Promise(r=>setTimeout(r,1500));
 const rect=await p.evaluate(()=>{const e=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas').getBoundingClientRect();return {x:e.x,y:e.y,width:e.width,height:e.height};});
 await p.touchscreen.tap(rect.x+40,rect.y+30);await new Promise(r=>setTimeout(r,300));
 await p.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelectorAll('button').forEach(x=>{if(x.textContent==='Keyboard')x.click()}));
 await p.keyboard.type('abc');
 await p.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('[aria-label="Website address"]')?.value.endsWith('#abc'),{timeout:30000});
 console.log('PASS phone touch focuses Gecko input and keyboard text reaches page');
 const snapshot=()=>p.evaluate(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot.querySelector('canvas').toDataURL());
 const before=await snapshot(),cdp=await p.createCDPSession(),x=Math.round(rect.x+rect.width/2),y=Math.round(rect.y+rect.height*.7);
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-80}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await new Promise(r=>setTimeout(r,1500));assert.notEqual(await snapshot(),before,'Touch drag should change rendered page');
 assert.deepEqual(errors,[]);console.log('PASS phone touch scroll changes real Gecko page');
}catch(e){await p.screenshot({path:'/tmp/codi-browser-phone-failure.png'}).catch(()=>{});console.error('FAIL',e.message,JSON.stringify(errors));process.exitCode=1;}
finally{await c.close();await b.disconnect();}
