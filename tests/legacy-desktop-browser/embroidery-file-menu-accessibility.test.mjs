import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18303/',phone=process.env.CODI_PHONE==='1';
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>{errors.push('Unexpected browser dialog');void dialog.dismiss()});
page.on('request',request=>{const url=new URL(request.url());if(['http:','https:'].includes(url.protocol)&&url.origin!==new URL(base).origin)external.push(url.href)});
try {
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:process.env.CODI_4K==='1'?{width:3840,height:2160}:{width:1366,height:900});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]','embroiderui'+Date.now().toString().slice(-8));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
 await page.evaluate(()=>surfaces.get('Desktop').launch('embroidery-studio'));await page.waitForFunction(()=>document.querySelector('.embroidery-studio .app-status')?.textContent.includes('local design'),{timeout:120000});
 const frame=await(await page.$('.embroidery-studio iframe')).contentFrame(),trigger=await frame.$('#codi-file-menu button[aria-label=File]');
 if(phone)await trigger.tap();else await trigger.click();
 const geometry=await frame.evaluate(()=>{const root=document.querySelector('#codi-file-menu'),menu=root.querySelector('[role=menu]'),trigger=root.querySelector('[aria-label=File]');return {labels:[...menu.querySelectorAll('[role=menuitem]')].map(x=>x.textContent),heights:[...menu.querySelectorAll('[role=menuitem],select')].map(x=>x.getBoundingClientRect().height),trigger:trigger.getBoundingClientRect().height,viewport:innerHeight,menu:menu.getBoundingClientRect().toJSON(),expanded:trigger.getAttribute('aria-expanded')}});
 assert.equal(geometry.expanded,'true');assert.equal(geometry.labels[0],'Open from My files');assert.equal(geometry.labels.at(-1),'Editor source and licenses');assert.ok(geometry.heights.every(height=>height>=44));if(phone)assert.ok(geometry.trigger>=44);assert.ok(geometry.menu.bottom<=geometry.viewport);
 await frame.focus('#codi-file-menu [role=menuitem]');await page.keyboard.press('Escape');assert.equal(await frame.$eval('#codi-file-menu [role=menu]',e=>e.hidden),true);assert.equal(await frame.evaluate(()=>document.activeElement?.getAttribute('aria-label')),'File');
 // A real pointer/touch action opens the account-backed picker.
 if(phone)await trigger.tap();else await trigger.click();const item=(await frame.$$('#codi-file-menu [role=menuitem]'))[0];if(phone)await item.tap();else await item.click();await page.waitForSelector('.codi-file-picker[open]');await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.codi-file-picker[open]'));
 await page.evaluate(()=>document.querySelector('.embroidery-studio').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.embroidery-studio'));
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);console.log('PASS embroidery File menu ordering, touch targets, dismissal and My files picker');
}finally{await context.close();await browser.disconnect()}
