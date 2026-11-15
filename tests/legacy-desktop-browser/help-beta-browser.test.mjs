import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const name=process.env.CODI_TEST_USER;
if(!/^browserprobe[0-9a-f]{10}$/.test(name||''))throw Error('Set a disposable browserprobe username');
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 await page.setViewport(process.env.CODI_PHONE==='1'?{width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true}:{width:1366,height:950});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(process.env.CODI_TEST_URL||'https://ksu.codes/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',name);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>[...surfaces.values()][0].launch('help'));await page.waitForSelector('.help-content a[href="mailto:dflanag3@students.kennesaw.edu"]');
 const result=await page.$eval('.help-content',e=>({text:e.innerText,link:e.querySelector('a')?.getAttribute('href')}));
 assert.match(result.text,/beta service/i);assert.match(result.text,/Linux terminal has a separate temporary guest filesystem/);assert.doesNotMatch(result.text,/Files and Text Editor|Ctrl\+S|normal browser tab/);assert.equal(result.link,'mailto:dflanag3@students.kennesaw.edu');
 console.log('PASS beta help, contact email and Linux terminal guidance');
}finally{await context.close();await browser.disconnect()}
