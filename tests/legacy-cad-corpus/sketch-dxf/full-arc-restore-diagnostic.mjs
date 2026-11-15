// Passive observation of an existing test-only native fixture's normal loader.
// Does not alter the fixture, replace a Worker, or bypass native project open.
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL),cdp=new URL(process.env.CODI_TEST_CDP);if(![base,cdp].every(u=>['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Loopback only');
const browser=await puppeteer.connect({browserURL:cdp.href}),context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.type('[aria-label=Username]',process.env.CODI_DXF_TEST_ACCOUNT);await page.type('[aria-label=Password]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>desktopLab?.session?.kind==='registered');
 await page.evaluate(()=>{
  window.dxfRestoreObservations=[];const seen=new WeakSet();
  window.dxfRestoreObserver=setInterval(()=>{for(const frame of document.querySelectorAll('.jsketcher-app iframe')){const c=frame.contentWindow?.__CAD_APP;if(!c?.craftService?.pipelineFailure$||seen.has(c))continue;seen.add(c);c.craftService.pipelineFailure$.attach(value=>{if(!value)return;const visited=new WeakSet();const text=JSON.stringify(value,(key,v)=>{if(v instanceof frame.contentWindow.Error)return {name:v.name,message:v.message,stack:v.stack};if(v&&typeof v==='object'){if(visited.has(v))return '[circular]';visited.add(v);}return v;});dxfRestoreObservations.push(text.slice(0,12000));});}},5);
 });
 const path='/full-arc-native.jsketcher.json';await page.evaluate(()=>surfaces.get('Desktop').launch('files'));await page.waitForSelector(`[data-chonky-file-id="${path}"]`,{timeout:45000});await page.click(`[data-chonky-file-id="${path}"]`);await page.waitForFunction(()=>[...document.querySelectorAll('.codi-chonky button')].some(b=>b.textContent.trim()==='Open'&&!b.disabled));await page.evaluate(()=>[...document.querySelectorAll('.codi-chonky button')].find(b=>b.textContent.trim()==='Open'&&!b.disabled).click());await page.waitForFunction(()=>document.querySelector('.jsketcher-app .app-status')?.textContent.startsWith('Could not open project:'),{timeout:45000});
 console.log(JSON.stringify(await page.evaluate(()=>({status:document.querySelector('.jsketcher-app .app-status').textContent,failures:dxfRestoreObservations})),null,2));
}finally{await context.close();browser.disconnect();}
