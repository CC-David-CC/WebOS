import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
async function run(phone,user){
 const context=await browser.createBrowserContext(),page=await context.newPage();
 try{
  await page.setViewport(phone?{width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true}:{width:1366,height:950});
  await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(u,...a)});
  await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18189/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  const state=()=>page.evaluate(()=>({hidden:document.querySelector('#voice-control').hidden,keyboard:document.documentElement.dataset.keyboardMode,buttons:document.querySelectorAll('#voice-control button').length}));
  assert.deepEqual(await state(),{hidden:true,keyboard:'typing',buttons:1});
  async function clickTool(name){await page.click('[aria-label=Applications]');await page.evaluate(()=>[...document.querySelectorAll('.menu-row')].find(n=>n.textContent.includes('System Tools')).click());await page.evaluate(name=>[...document.querySelectorAll('.menu-row')].find(n=>n.textContent===name).click(),name);}
  await clickTool('Voice input');assert.equal((await state()).hidden,false);
  await clickTool('Voice input');assert.equal((await state()).hidden,true);
  await clickTool('Keyboard lock');assert.equal((await state()).keyboard,'voice');
  await clickTool('Keyboard lock');assert.equal((await state()).keyboard,'typing');
  console.log(phone?'phone menu PASS':'desktop menu PASS');
 }finally{await context.close();}
}
try{const unique=Date.now().toString().slice(-8);await run(false,'voiced'+unique);await run(true,'voicep'+unique);}finally{await browser.disconnect()}
