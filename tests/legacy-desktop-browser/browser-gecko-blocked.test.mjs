import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';

const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage();
const username=process.env.CODI_TEST_USERNAME||'blockedtest'+Date.now().toString().slice(-8);
try {
  await page.evaluateOnNewDocument(()=>{const fetch0=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):fetch0(url,...args);});
  await page.goto(process.env.CODI_TEST_DESKTOP_URL||'http://127.0.0.1:18154/');
  await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');
  await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  await page.click('[aria-label=Applications]');await page.waitForSelector('[aria-label=Browser]');await page.click('[aria-label=Browser]');
  await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].some(e=>e.shadowRoot?.querySelector('.status')?.textContent==='Ready'),{timeout:180000});
  await page.evaluate(()=>{const root=[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot).shadowRoot;root.querySelector('[aria-label="Website address"]').value='https://youtube.com/';root.querySelector('form').requestSubmit();});
  await page.waitForFunction(()=>[...document.querySelectorAll('.window-content')].some(e=>e.shadowRoot?.querySelector('.status')?.textContent.includes('blocked by the server network policy')),{timeout:60000});
  const status=await page.evaluate(()=>[...document.querySelectorAll('.window-content')].find(e=>e.shadowRoot).shadowRoot.querySelector('.status').textContent);
  assert.match(status,/youtube\.com/);
  console.log('PASS real Browser shows the server policy denial for a blocked destination');
}finally{await context.close();await browser.disconnect();}
