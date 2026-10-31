import puppeteer from 'puppeteer-core';
const name=process.env.CODI_TEST_USER;if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Disposable account required');
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000}),context=await browser.createBrowserContext(),page=await context.newPage();
const file='/browser-blocked-resource-test.html';
try{
 await page.setViewport({width:1366,height:950});await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto('https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(async path=>{const c=await mirrorFileContext();await c.files.write(path,'<!doctype html><h1>Policy resource fixture</h1><img src="https://www.youtube.com/codi-policy-test.png">');await c.files.sync()},file);
 await page.evaluate(()=>[...surfaces.values()][0].launch('browser'));await page.waitForFunction(()=>[...([...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot.querySelectorAll('button')||[])].some(b=>b.textContent==='Stop'&&!b.disabled),{timeout:180000});
 await page.evaluate(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot).shadowRoot;[...r.querySelectorAll('button')].find(b=>b.textContent==='Open from My files').click()});
 await page.waitForSelector('[aria-label="Choose file browser-blocked-resource-test.html"]',{timeout:30000});await page.click('[aria-label="Choose file browser-blocked-resource-test.html"]');
 await page.waitForFunction(()=>{const r=[...document.querySelectorAll('.window-content')].find(x=>x.shadowRoot)?.shadowRoot;const t=r?.querySelector('.status')?.textContent||'';return t.includes('blocked by the server network policy')&&t.includes('youtube.com')},{timeout:60000});
 console.log('PASS live Browser explains a blocked embedded resource in an account HTML document');
}finally{
 await page.evaluate(async path=>{try{const c=await mirrorFileContext(),f=await c.files.read(path);await c.files.remove(path,f.version);await c.files.sync()}catch{}},file).catch(()=>{});
 await context.close();await browser.disconnect();
}
