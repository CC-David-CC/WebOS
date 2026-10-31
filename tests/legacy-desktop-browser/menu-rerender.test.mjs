import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255'});
try{for(const phone of [false,true]){
 const context=await browser.createBrowserContext(),page=await context.newPage();
 try{
  if(phone)await page.setViewport({width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true});
  await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18161/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]',(phone?'menuph':'menudt')+Date.now().toString().slice(-9));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
  await page.evaluate(()=>document.querySelector('[aria-label=Applications]').click());await page.waitForSelector('[aria-label=Crafts]');await page.evaluate(()=>document.querySelector('[aria-label=Crafts]').click());
  await page.waitForSelector('[aria-label="Stitch Converter"]');
  const result=await page.evaluate(()=>{const pane=document.querySelector('[aria-label="Stitch Converter"]').closest('.menu-pane');[...surfaces.values()][0].render();return {connected:pane.isConnected,visible:!!document.querySelector('[aria-label="Stitch Converter"]')}});
  assert.deepEqual(result,{connected:true,visible:true});console.log('PASS',phone?'phone':'desktop','submenu survives desktop redraw');
 }finally{await context.close()}
}}finally{await browser.disconnect()}
