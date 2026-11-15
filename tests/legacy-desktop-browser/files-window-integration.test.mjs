import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {writeFile,unlink} from 'node:fs/promises';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),username=process.env.CODI_TEST_USER||'files'+Date.now().toString().slice(-9),upload='/tmp/codi-files-upload-test.txt',url=process.env.CODI_TEST_URL||'http://127.0.0.1:18207/';
try {
 await page.setViewport({width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:1});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(url);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>surfaces.get('Desktop').launch('files'));const trigger='[aria-label="New or upload"]';await page.waitForSelector(trigger,{visible:true});await page.waitForFunction(s=>!document.querySelector(s).disabled,{},trigger);
 page.on('dialog',d=>d.accept('school.txt'));await page.tap(trigger);await page.evaluate(()=>[...document.querySelectorAll('[role=menuitem]')].find(e=>e.textContent==='New file').click());
 await page.waitForFunction(async()=>{try{return (await (await mirrorFileContext()).files.read('/school.txt')).status==='synced';}catch{return false;}},{timeout:45000});
 await writeFile(upload,'upload fixture');await page.tap(trigger);const chooserPromise=page.waitForFileChooser();await page.evaluate(()=>[...document.querySelectorAll('[role=menuitem]')].find(e=>e.textContent==='Upload').click());const chooser=await chooserPromise;await chooser.accept([upload]);
 await page.waitForFunction(async()=>{try{return (await (await mirrorFileContext()).files.read('/codi-files-upload-test.txt')).status==='synced';}catch{return false;}},{timeout:45000});

 const fresh=await browser.createBrowserContext(),freshPage=await fresh.newPage();try{await freshPage.goto(url);await freshPage.waitForSelector('.login-gate');await freshPage.type('[aria-label=Username]',username);await freshPage.type('[aria-label=Password]','test1234');await freshPage.click('.login-form button[type=submit]');await freshPage.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});await freshPage.waitForFunction(async()=>{try{const c=await mirrorFileContext();return !!(await c.files.read('/school.txt'))&&new TextDecoder().decode((await c.files.read('/codi-files-upload-test.txt')).data)==='upload fixture';}catch{return false;}},{timeout:45000});}finally{await fresh.close();}
 await page.evaluate(()=>surfaces.get('Desktop').launch('files'));
 async function assertMax(){return page.evaluate(()=>{const d=surfaces.get('Desktop'),root=d.root.getBoundingClientRect();return d.windows.filter(w=>w.app==='files').map(w=>{const r=d.root.querySelector('[data-window="'+w.id+'"]')?.getBoundingClientRect();return {x:r?.left-root.left,y:r?.top-root.top,width:r?.width,height:r?.height,rootWidth:root.width,rootHeight:root.height,panel:d.config.panelHeight};});});}
 for(const view of [{width:412,height:915,isMobile:true,hasTouch:true},{width:1366,height:900,isMobile:true,hasTouch:true},{width:3840,height:2160,isMobile:true,hasTouch:true},{width:1024,height:700,isMobile:true,hasTouch:true}]){
  await page.setViewport({...view,deviceScaleFactor:1});await page.waitForFunction(w=>surfaces.get('Desktop').root.getBoundingClientRect().width===w,{},view.width);
  await new Promise(r=>setTimeout(r,200));const sizes=await assertMax();console.log('viewport',view.width,'windows',JSON.stringify(sizes));assert.equal(sizes.length,2);
  for(const s of sizes){assert.ok(Math.abs(s.x)<=1&&Math.abs(s.y-s.panel)<=1&&Math.abs(s.width-s.rootWidth)<=1&&Math.abs(s.height-(s.rootHeight-s.panel))<=1,JSON.stringify({view,s}));}
 }
 await page.evaluate(()=>{const d=surfaces.get('Desktop'),w=d.windows.find(w=>w.app==='files');d.root.querySelector('[data-window="'+w.id+'"] [aria-label="Maximize"]').click();});
 const restored=await assertMax();assert.ok(restored[0].width<restored[0].rootWidth,'Maximize control should restore the first window');assert.equal(restored[1].width,restored[1].rootWidth,'Other window remains maximized');
 await page.evaluate(()=>surfaces.get('Desktop').saveLayout());
 await page.setViewport({width:1920,height:1080,isMobile:true,hasTouch:true,deviceScaleFactor:1});await page.waitForFunction(()=>surfaces.get('Desktop').root.getBoundingClientRect().width===1920);await new Promise(r=>setTimeout(r,200));
 const after=await assertMax();assert.ok(after[0].width<after[0].rootWidth);assert.equal(after[1].width,after[1].rootWidth);
 await page.evaluate(()=>surfaces.get('Desktop').saveLayout());await page.reload();await page.waitForSelector('.login-gate');await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.waitForFunction(()=>surfaces.get('Desktop').windows.filter(w=>w.app==='files').length===2,{timeout:30000});const reopened=await assertMax();assert.ok(reopened[0].width<reopened[0].rootWidth,'Restored window remains restored after reload');assert.equal(reopened[1].width,reopened[1].rootWidth,'Maximized window remains maximized after reload');
 const desktop=await context.newPage();await desktop.setViewport({width:1920,height:1080,isMobile:false,hasTouch:false,deviceScaleFactor:1});
 await desktop.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await desktop.goto(url);await desktop.waitForSelector('.login-gate');await desktop.type('[aria-label=Username]',username);await desktop.type('[aria-label=Password]','test1234');await desktop.click('.login-form button[type=submit]');await desktop.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 const initial=await desktop.evaluate(()=>{const d=surfaces.get('Desktop'),w=d.launch('files'),r=d.root.querySelector('[data-window="'+w.id+'"]')?.getBoundingClientRect(),root=d.root.getBoundingClientRect();return {width:r?.width,height:r?.height,rootWidth:root.width,rootHeight:root.height,panel:d.config.panelHeight};});
 assert.equal(initial.width,initial.rootWidth);assert.equal(initial.height,initial.rootHeight-initial.panel);await desktop.close();
 await page.evaluate(async()=>{const c=await mirrorFileContext();for(const name of ['/school.txt','/codi-files-upload-test.txt']){const f=await c.files.read(name);await c.files.remove(name,f.version);}await c.files.sync();});await page.waitForFunction(async()=>{try{return (await (await mirrorFileContext()).files.status()).pending===0;}catch{return false;}},{timeout:45000});
 console.log('PASS phone Files creates and uploads account files, syncs and recovers both in a fresh context; maximized windows follow viewport through 4K; restored window stays independent');
}finally{await unlink(upload).catch(()=>{});await context.close();await browser.disconnect()}
