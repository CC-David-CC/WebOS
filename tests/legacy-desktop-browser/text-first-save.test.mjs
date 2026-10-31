import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'});
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18209/';
async function run(phone){const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
const username=(phone?process.env.CODI_TEST_PHONE_USER:process.env.CODI_TEST_DESKTOP_USER)||(phone?'saveph':'savedk')+Date.now().toString().slice(-9);
try{
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:1}:{width:1920,height:1080,deviceScaleFactor:1});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/Untitled.txt','existing',null);await c.files.sync();surfaces.get('Desktop').launch('text')});
 await page.waitForSelector('.codi-text-editor .cm-content',{visible:true,timeout:30000});await page.click('.cm-content');await page.keyboard.type('A new lesson');
 if(phone)await page.tap('.ce-toolbar [data-command=save]');else await page.click('.ce-desktop-save [data-command=save]');
 await page.waitForSelector('.ce-dialog-backdrop:not([hidden])');assert.equal(await page.$eval('.ce-dialog h2',e=>e.textContent),'Save to My files');
 await page.click('.ce-dialog-primary');await page.waitForFunction(()=>!document.querySelector('.ce-dialog-error')?.hidden,{timeout:30000});
 const intact=await page.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Untitled.txt')).data));assert.equal(intact,'existing');assert.equal(await page.$eval('.cm-content',e=>e.innerText),'A new lesson');
 await page.focus('.ce-path-input');await page.keyboard.down('Control');await page.keyboard.press('KeyA');await page.keyboard.up('Control');await page.keyboard.type('/lesson.txt');await page.click('.ce-dialog-primary');
 await page.waitForFunction(async()=>{try{const f=await(await mirrorFileContext()).files.read('/lesson.txt');return f.status==='synced'&&new TextDecoder().decode(f.data)==='A new lesson'}catch{return false}},{timeout:45000});
 const fresh=await browser.createBrowserContext(),q=await fresh.newPage();try{await q.goto(base);await q.waitForSelector('.login-gate');await q.type('[aria-label=Username]',username);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});await q.waitForFunction(async()=>{try{return new TextDecoder().decode((await(await mirrorFileContext()).files.read('/lesson.txt')).data)==='A new lesson'}catch{return false}},{timeout:30000});}finally{await fresh.close();}
 assert.deepEqual(errors,[]);console.log('PASS',phone?'phone-sized':'desktop','first Save asks for name, refuses collision, syncs and recovers');
}finally{await context.close();}}
try{await run(false);await run(true)}finally{await browser.disconnect()}
