import {chooseRoot} from './browser-choose-root.mjs';
import puppeteer from 'puppeteer-core';import assert from 'node:assert/strict';
const name=process.env.CODI_TEST_USER;if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Set disposable test user');
const b=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),c=await b.createBrowserContext(),p=await c.newPage();
try{
 await p.setViewport(process.env.CODI_PHONE==='1'?{width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true}:{width:1366,height:950});
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await p.goto('https://ksu.codes/');await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',name);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await p.evaluate(()=>[...surfaces.values()][0].launch('browser'));await p.waitForFunction(()=>[...([...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled),{timeout:180000});
 await p.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;r.querySelector('[aria-label="Website address"]').value='https://example.com/'});
 p.once('dialog',d=>d.accept('browser-download-test.html'));await p.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...r.querySelectorAll('button')].find(b=>b.textContent==='Download URL').click()});await chooseRoot(p);
 await p.waitForFunction(()=>[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelector('.status')?.textContent.includes('Saved to My files'),{timeout:90000});
 const result=await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();const a=await c.files.read('/browser-download-test.html'),server=await(await serverFileContext()).files.read('browser-download-test.html');return {text:new TextDecoder().decode(a.data),same:a.sha256===server.sha256}});assert.match(result.text,/example/i);assert.equal(result.same,true);
 const second=await b.createBrowserContext();try{
  const q=await second.newPage();await q.goto('https://ksu.codes/');await q.waitForSelector('.login-form');await q.type('[aria-label=Username]',name);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  const recovered=await q.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();const f=await c.files.read('/browser-download-test.html');return new TextDecoder().decode(f.data)});assert.equal(recovered,result.text);
 }finally{await second.close()}
 await p.evaluate(async()=>{const c=await mirrorFileContext(),f=await c.files.read('/browser-download-test.html');await c.files.remove('/browser-download-test.html',f.version);await c.files.sync()});
 console.log('PASS live URL download saved and synchronized from '+(process.env.CODI_PHONE==='1'?'phone-sized':'desktop')+' UI and recovered in a fresh signed-in browser context');
}finally{
 await p.evaluate(async()=>{try{const c=await mirrorFileContext(),f=await c.files.read('/browser-download-test.html');await c.files.remove('/browser-download-test.html',f.version);await c.files.sync()}catch{}}).catch(()=>{});
 await c.close();await b.disconnect()
}
