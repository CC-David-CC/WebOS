import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const b=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'});
async function run(phone){const c=await b.createBrowserContext(),p=await c.newPage(),errors=[],username=(phone?process.env.CODI_TEST_PHONE_USER:process.env.CODI_TEST_DESKTOP_USER)||(phone?'ftphone':'ftdesk')+Date.now().toString().slice(-9),base=process.env.CODI_TEST_URL||'http://127.0.0.1:18208/';p.on('pageerror',e=>errors.push(e.message));
try{
 await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:1}:{width:1920,height:1080,deviceScaleFactor:1});
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',username);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await p.evaluate(()=>surfaces.get('Desktop').launch('files'));await p.waitForSelector('.codi-chonky');await p.waitForFunction(()=>document.querySelector('.files-content')?.innerText.includes('Files checked with the server.'));
 p.once('dialog',d=>d.accept('lesson.txt'));
 if(phone)await p.tap('[aria-label="New or upload"]');else await p.$eval('.codi-chonky',e=>e.dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true,clientX:350,clientY:350})));
 await p.waitForSelector('[role=menuitem]');await p.evaluate(()=>[...document.querySelectorAll('[role=menuitem]')].find(e=>e.textContent==='New file').click());
 await p.waitForSelector('[data-chonky-file-id="/lesson.txt"]',{timeout:30000});
 if(phone){await p.tap('[data-chonky-file-id="/lesson.txt"]');await p.waitForFunction(()=>[...document.querySelectorAll('.codi-chonky button')].some(b=>b.textContent.trim()==='Open'&&!b.disabled));const open=await p.evaluateHandle(()=>[...document.querySelectorAll('.codi-chonky button')].find(b=>b.textContent.trim()==='Open'));await open.asElement().tap();}else {await p.click('[data-chonky-file-id="/lesson.txt"]');await p.click('[data-chonky-file-id="/lesson.txt"]',{clickCount:2});}
 await p.waitForSelector('.codi-text-editor .cm-content',{timeout:12000});console.log('PASS',phone?'phone selection and Open':'desktop double-click','opened new file in Text');
 await p.click('.codi-text-editor .cm-content');await p.keyboard.type('Hello world');
 if(phone)await p.tap('.ce-toolbar [data-command=save]');else await p.click('.ce-desktop-save [data-command=save]');
 await p.waitForFunction(async()=>{try{const f=await(await mirrorFileContext()).files.read('/lesson.txt');return f.status==='synced'&&new TextDecoder().decode(f.data)==='Hello world'}catch{return false}},{timeout:45000});
 await p.evaluate(()=>document.querySelector('.codi-text-editor').closest('[data-window]').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.codi-text-editor'));
 if(phone){const button=await p.evaluateHandle(()=>[...document.querySelectorAll('.codi-chonky button')].find(b=>b.textContent.trim()==='Open'));await button.asElement().tap();}else {await p.click('[data-chonky-file-id="/lesson.txt"]');await p.click('[data-chonky-file-id="/lesson.txt"]',{clickCount:2});}
 await p.waitForFunction(()=>document.querySelector('.codi-text-editor .cm-content')?.innerText==='Hello world',{timeout:30000});
 const fresh=await b.createBrowserContext(),q=await fresh.newPage();try{await q.goto(base);await q.waitForSelector('.login-gate');await q.type('[aria-label=Username]',username);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});await q.waitForFunction(async()=>{try{return new TextDecoder().decode((await(await mirrorFileContext()).files.read('/lesson.txt')).data)==='Hello world'}catch{return false}},{timeout:30000});}finally{await fresh.close();}
 assert.deepEqual(errors,[]);console.log('PASS edit/save/sync/reopen/fresh-context',phone?'phone-sized':'desktop');
}catch(e){console.error('DETAIL',phone?'phone':'desktop',await p.evaluate(()=>document.body.innerText.slice(-1200)).catch(()=>''),errors);throw e}finally{await c.close()}}
try{await run(false);await run(true)}finally{await b.disconnect()}
