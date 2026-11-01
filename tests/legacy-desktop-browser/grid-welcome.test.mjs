import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18294/';
page.on('pageerror',e=>errors.push(e.message));
page.on('dialog',dialog=>{errors.push('Unexpected browser dialog');void dialog.dismiss();});
try {
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:process.env.CODI_4K?{width:3840,height:2160}:{width:1366,height:900});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]','gridwelcome'+Date.now().toString().slice(-8));
 await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
 for(const [index,app] of ['mesh-tool','mesh-tool','kiri-moto'].entries()) {
  await page.evaluate(id=>surfaces.get('Desktop').launch(id),app);
  const expected=index+1;
  await page.waitForFunction(count=>{const fs=document.querySelectorAll('.grid-frame'),f=fs[count-1],d=f?.contentDocument;return fs.length===count&&d?.getElementById('curtain')&&getComputedStyle(d.getElementById('curtain')).display==='none';},{timeout:60000},expected);
 }
 const frames=await page.$$('.grid-frame');assert.equal(frames.length,3);
 for(const handle of frames.slice(0,2)) {
  const frame=await handle.contentFrame();
  assert.equal(await frame.$eval('#modal_page',e=>getComputedStyle(e).display),'none','new Mesh window must not start with About');
  assert.equal(await frame.$eval('#container canvas',e=>e.getBoundingClientRect().width>0),true);
 }
 // The upstream About command remains available after suppressing startup.
 const first=await frames[0].contentFrame();
 await first.evaluate(()=>{const menu=[...document.querySelectorAll('.menu')].find(x=>x.firstElementChild?.textContent.trim()==='Help');menu.querySelector('.menu-items > div').click()});
 await first.waitForFunction(()=>document.querySelector('#modal_title_text')?.textContent==='About Mesh:Tool'&&getComputedStyle(document.querySelector('#modal_page')).display!=='none');
 await first.$eval('#modal_title_close',e=>e.click());
 assert.equal(await first.$eval('#modal_page',e=>getComputedStyle(e).display),'none');
 assert.equal(await (await frames[1].contentFrame()).$eval('#modal_page',e=>getComputedStyle(e).display),'none','About stays in its own window');
 assert.deepEqual(errors,[]);console.log('PASS Mesh startup, Help → About and independent windows; Kiri startup');
} finally {await context.close();await browser.disconnect();}
