import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18464/',username=process.env.CODI_TEST_USER||'pinball'+Date.now().toString().slice(-9);
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19465',protocolTimeout:120000}),contexts=[],errors=[];
async function login(page,register){
 page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{const original=window.fetch;window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):original(url,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');if(register)await page.click('.login-toggle');await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');if(register)await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function checkGamesMenu(page){
 for(let attempt=0;attempt<4;attempt++){try{await page.click('.app-menu-button');break}catch(error){if(attempt===3||!String(error.message).includes('detached'))throw error}}await page.waitForSelector('.menu-pane');
 await page.evaluate(()=>[...document.querySelectorAll('.menu-row')].find(x=>x.getAttribute('aria-label')==='Games').click());
 await page.waitForFunction(()=>[...document.querySelectorAll('.menu-row')].some(x=>x.getAttribute('aria-label')==='Memory Garden (preview)'));
 const metrics=await page.evaluate(()=>{const row=[...document.querySelectorAll('.menu-row')].find(x=>x.getAttribute('aria-label')==='Memory Garden (preview)');row.scrollIntoView({block:'nearest'});const p=row.closest('.menu-pane'),r=row.getBoundingClientRect(),v=p.getBoundingClientRect();return {count:p.querySelectorAll('.menu-row').length,bottom:r.bottom,viewBottom:v.bottom,top:r.top,viewTop:v.top}});
 assert.ok(metrics.count>=28);assert.ok(metrics.bottom<=metrics.viewBottom+1&&metrics.top>=metrics.viewTop-1,'last game reachable in scrollable menu');await page.keyboard.press('Escape');
}
async function launch(page){await page.evaluate(()=>surfaces.get('Desktop').launch('gravity-pinball'));await page.waitForSelector('.pinball-stage canvas',{timeout:30000});await page.waitForFunction(()=>document.querySelector('.pinball-marquee')?.textContent.includes('Balls 3'))}
try{
 const first=await browser.createBrowserContext();contexts.push(first);const page=await first.newPage();await page.setViewport({width:1366,height:900});await login(page,true);await checkGamesMenu(page);
 await page.evaluate(()=>{localStorage.setItem('codi.gravity-pinball.highScore','999999');localStorage.setItem('codi.gravity-pinball.highScore:'+signedInSubject(),'77')});
 await launch(page);assert.match(await page.$eval('.pinball-marquee',e=>e.textContent),/High 77/);
 await page.evaluate(()=>{const input=document.createElement('input');input.id='focus-review';document.querySelector('.pinball-view').append(input);input.focus()});await page.keyboard.press('p');assert.equal(await page.$eval('[aria-label=Start]',e=>e.textContent),'Start / Resume');
 await page.evaluate(()=>{document.querySelector('#focus-review').remove();document.querySelector('.pinball-view').closest('.window').classList.remove('focused')});await page.keyboard.press('p');assert.equal(await page.$eval('[aria-label=Start]',e=>e.textContent),'Start / Resume');await page.evaluate(()=>document.querySelector('.pinball-view').closest('.window').classList.add('focused'));
 await page.click('[aria-label=Start]');await page.click('[aria-label="Save to My files"]');await page.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('syncing with the server'),{timeout:30000});await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Gravity Pinball.game.json')).data)));assert.equal(saved.appId,'gravity-pinball');
 await page.evaluate(()=>document.querySelector('.gravity-pinball-app').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.gravity-pinball-app'));
 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Gravity Pinball.game.json'));await page.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('Checkpoint loaded and paused'),{timeout:30000});
 const fresh=await browser.createBrowserContext();contexts.push(fresh);const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});await login(phone,false);await checkGamesMenu(phone);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);await phone.evaluate(()=>document.querySelector('[aria-label="Open from My files"]').click());await phone.waitForSelector('[aria-label="Choose file Gravity Pinball.game.json"]');await phone.click('[aria-label="Choose file Gravity Pinball.game.json"]');await phone.waitForFunction(()=>document.querySelector('.pinball-side > .app-status')?.textContent.includes('Checkpoint loaded and paused'),{timeout:30000});
 assert.deepEqual(errors,[]);console.log('PASS account save, sync, Files route, close and phone-sized paused reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
