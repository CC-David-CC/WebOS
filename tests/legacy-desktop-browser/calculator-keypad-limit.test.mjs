import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext();
try {
 for(const phone of [false,true]){
  const page=await context.newPage();
  await page.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true}:{width:1366,height:900});
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18303/');
  await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]','climit'+Date.now().toString().slice(-10));
  await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');await page.evaluate(()=>[...surfaces.values()][0].launch('calculator'));await page.waitForSelector('.calculator-content');
  const input='[aria-label="Arithmetic expression"]';
  await page.$eval(input,e=>{e.value='1'.repeat(512);e.dispatchEvent(new Event('input',{bubbles:true}));e.setSelectionRange(512,512)});
  async function tap(label){const buttons=await page.$$('.calculator-keys button');for(const b of buttons){if(await b.evaluate(e=>e.textContent)===label){await b.scrollIntoView();const p=await b.boundingBox();if(phone)await page.touchscreen.tap(p.x+p.width/2,p.y+p.height/2);else await page.mouse.click(p.x+p.width/2,p.y+p.height/2);return}}throw Error('Missing keypad button '+label)}
  await tap('1');assert.equal(await page.$eval(input,e=>e.value.length),512,'keypad cannot exceed the expression limit');
  assert.match(await page.$eval('.calculator-result-status',e=>e.textContent),/512 characters/);
  await page.$eval(input,e=>e.setSelectionRange(0,4));await tap('sin(');
  assert.equal(await page.$eval(input,e=>e.value.length),512,'selected text can be replaced at the limit');
  assert.ok(await page.$eval(input,e=>e.value.startsWith('sin(')));
  await tap('⌫');assert.equal(await page.$eval(input,e=>e.value.length),511);
  await tap('1');assert.equal(await page.$eval(input,e=>e.value.length),512);
  await page.close();
 }
 console.log('PASS calculator keypad respects the expression limit and replaces selections');
} finally {await context.close();await browser.disconnect()}
