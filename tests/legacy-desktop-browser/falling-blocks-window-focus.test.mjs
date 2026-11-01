import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),user='focus'+Date.now().toString().slice(-9);
try {
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18305/');
 await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);
 await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');console.log('Test account',user,await page.evaluate(()=>signedInSubject()));
 await page.evaluate(()=>surfaces.get('Desktop').launch('falling-blocks'));
 await page.waitForSelector('.window.focused .blocks-app canvas',{timeout:30000});
 await page.click('.window.focused .blocks-app [aria-label=Resume]');
 await page.waitForFunction(()=>document.querySelector('.blocks-info')?.textContent.includes('Playing'));
 await page.evaluate(()=>surfaces.get('Desktop').launch('calculator'));
 await page.waitForSelector('.window.focused .calculator-content',{timeout:30000});
 await page.waitForFunction(()=>document.querySelector('.blocks-info')?.textContent.includes('Paused'),{timeout:5000});
 await page.evaluate(()=>{const d=surfaces.get('Desktop'),w=d.windows.find(w=>w.app==='falling-blocks');d.activateWindow(w)});
 await page.waitForSelector('.window.focused .blocks-app');
 assert.match(await page.$eval('.blocks-info',e=>e.textContent),/Paused/,'returning to the game must not resume automatically');
 await page.click('.window.focused .blocks-app [aria-label=Resume]');
 await page.waitForFunction(()=>document.querySelector('.blocks-info')?.textContent.includes('Playing'));
 await page.evaluate(()=>surfaces.get('Desktop').launch('falling-blocks'));
 await page.waitForFunction(()=>document.querySelectorAll('.blocks-app').length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.blocks-info')[0].textContent.includes('Paused'),{timeout:5000});
 console.log('PASS desktop focus loss pauses, stays paused on return, and another game window pauses the first');
} finally {await context.close();await browser.disconnect()}
