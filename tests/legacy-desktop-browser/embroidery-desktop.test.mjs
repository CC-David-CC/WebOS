import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,deviceScaleFactor:2.625,isMobile:true,hasTouch:true});
 page.on('pageerror',e=>console.log('PAGEERROR',e.message));page.on('requestfailed',r=>console.log('REQUESTFAIL',r.url(),r.failure()?.errorText));page.on('response',r=>{if(r.status()>=400)console.log('HTTPERROR',r.status(),r.url())});
 await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18159/');await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]',process.env.CODI_TEST_USERNAME||'craft'+Date.now().toString().slice(-9));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(()=>document.querySelector('[aria-label=Applications]').click());await page.waitForSelector('[aria-label=Crafts]');await page.evaluate(()=>document.querySelector('[aria-label=Crafts]').click());
 console.log('CRAFTS',await page.$$eval('[aria-label]',es=>es.map(e=>e.getAttribute('aria-label')).filter(x=>/stitch|embroid/i.test(x))));
 await page.evaluate(()=>[...surfaces.values()][0].launch('stitch-converter'));await page.waitForSelector('.stitch-converter');
 await page.evaluate(()=>[...document.querySelectorAll('.stitch-bar button')].find(b=>b.textContent==='Create stitch preview').click());
 await page.waitForFunction(()=>document.querySelector('.stitch-converter .app-status').textContent.includes('Preview ready'),{timeout:30000});
 console.log('PREVIEW',await page.$eval('.stitch-converter .app-status',e=>e.textContent));
 await page.evaluate(()=>[...document.querySelectorAll('.stitch-bar button')].find(b=>b.textContent==='Save machine file').click());
 await page.waitForFunction(()=>document.querySelector('.stitch-converter .app-status').textContent.includes('Saved '),{timeout:30000});
 console.log('SAVE',await page.$eval('.stitch-converter .app-status',e=>e.textContent));
 console.log('SAVED',await page.evaluate(async()=>{let c=await mirrorFileContext();let f=await c.files.read('/Design.pes');return {size:f.data.length,magic:Array.from(f.data.slice(0,8))}}));
 await page.evaluate(()=>[...surfaces.values()][0].launch('embroidery-studio'));await page.waitForSelector('.embroidery-studio');
 await page.waitForFunction(()=>document.querySelector('.embroidery-studio .app-status').textContent.startsWith('Editor ready'),{timeout:120000});
 console.log('STUDIO',await page.$eval('.embroidery-studio .app-status',e=>e.textContent));
 await page.evaluate(()=>[...document.querySelectorAll('.embroidery-bar button')].find(b=>b.textContent==='Open heart example').click());
 await page.waitForFunction(()=>document.querySelector('.embroidery-studio .app-status').textContent.startsWith('Opened example'),{timeout:30000});
 console.log('EXAMPLE',await page.$eval('.embroidery-studio .app-status',e=>e.textContent));
 const fr=page.frames().find(f=>f.url().includes('/vendor/index.html'));const exportResult=await fr.evaluate(async()=>{const a=window.vectorcraft;await a.execute('file.new',{name:'Test'});const sh=await a.execute('shape.rectangle',{x:0,y:0,width:100,height:60});await a.execute('embroidery.set',{type:'fill',ids:[sh.id]});const result=await a.execute('embroidery.export',{format:'dst'});return {keys:Object.keys(result),len:result.dataBase64?.length,files:a.files()};});assert.ok(exportResult.len>0,'StitchFoundry generated a DST');console.log('EXPORT',exportResult);await page.evaluate(()=>[...document.querySelectorAll('.embroidery-bar button')].find(b=>b.textContent==='Export stitches to My files').click());await page.waitForFunction(()=>document.querySelector('.embroidery-studio .app-status').textContent.startsWith('Saved /Embroidery.dst'),{timeout:30000});console.log('STUDIO SAVE',await page.$eval('.embroidery-studio .app-status',e=>e.textContent));console.log('DST',await page.evaluate(async()=>{let c=await mirrorFileContext();let f=await c.files.read('/Embroidery.dst');return {size:f.data.length,header:new TextDecoder().decode(f.data.slice(0,12))}}));if(process.env.CODI_TEST_CLEAN_FILES==='1')await page.evaluate(async()=>{const c=await mirrorFileContext();for(const path of ['/Design.pes','/Embroidery.dst']){const f=await c.files.read(path);await c.files.remove(path,f.version)}await c.files.sync()});console.log('PASS');
}catch(e){console.log('DIAGNOSTIC',await page.evaluate(()=>({text:document.body.innerText.slice(-1600),apps:typeof appCatalog==='undefined'?null:appCatalog})).catch(()=>null));throw e}finally{await context.close();await browser.disconnect();}
