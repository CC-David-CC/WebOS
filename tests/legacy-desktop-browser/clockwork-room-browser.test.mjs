import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
const base=process.env.CODI_CLOCKWORK_URL||'http://127.0.0.1:18343/';
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
page.on('request',request=>{
 if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==new URL(base).origin)external.push(request.url());
});

const click=label=>page.evaluate(label=>{
 const first=document.querySelectorAll('.clockwork-view')[0];
 const button=[...first.querySelectorAll('button')].find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_CLOCKWORK_MANIFEST||'.build/clockwork-room/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.clockwork-stage-wrap canvas').length===2,{timeout:30000});
 await page.waitForFunction(()=>document.querySelectorAll('.clockwork-loading').length===0,{timeout:30000});
 assert.equal(await page.$$eval('.clockwork-view',nodes=>nodes.length),2);
 assert.match(await page.$eval('.clockwork-status',node=>node.textContent),/Press Run/);
 assert.match(await page.$eval('.clockwork-rive-pending',node=>node.textContent),/Rive artwork.*pending/);

 const run=await page.$('.clockwork-toolbar [aria-label=Run]');
 if(process.env.CODI_PHONE)await run.tap();else await run.click();
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room running'));
 await click('Use Gear alignment');
 await click('Use Chime sequence');
 await click('Use Pendulum brake');
 await click('Use Exit lock');
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('exit is open'));
 assert.deepEqual(await page.evaluate(()=>[...document.querySelectorAll('.clockwork-view')[0]
  .querySelectorAll('.clockwork-objectives li')].map(row=>row.dataset.solved)),['true','true','true','true']);
 assert.match(await page.$eval('.clockwork-inventory',node=>node.textContent),/crystal-lens/);
 await click('Hint for Exit lock');
 assert.match(await page.$eval('.clockwork-status',node=>node.textContent),/hint/i);

 await page.evaluate(()=>document.querySelector('.clockwork-save').open=true);
 await page.$eval('[aria-label="Clockwork room save path"]',node=>node.value='/Clockwork Room.game.json');
 await click('Save');
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room saved to My files'));
 const saved=JSON.parse(await page.evaluate(()=>new TextDecoder().decode(window.fileStore.get('/Clockwork Room.game.json').data)));
 assert.equal(saved.appId,'clockwork-room');
 assert.deepEqual(saved.payload.solved,[true,true,true,true]);
 assert.equal(saved.payload.exitOpen,true);

 await click('Restart');
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room reset'));
 await click('Open');
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('loaded and paused'));
 assert.deepEqual(await page.evaluate(()=>[...document.querySelectorAll('.clockwork-view')[0]
  .querySelectorAll('.clockwork-objectives li')].map(row=>row.dataset.solved)),['true','true','true','true']);
 await page.evaluate(()=>window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{"format":"wrong"}'),version:'bad',status:'synced'}));
 await page.evaluate(()=>window.target='/Bad.game.json');
 await click('Open');
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Could not open room'));
 assert.deepEqual(await page.evaluate(()=>[...document.querySelectorAll('.clockwork-view')[0]
  .querySelectorAll('.clockwork-objectives li')].map(row=>row.dataset.solved)),['true','true','true','true']);

 await page.evaluate(()=>{
  const first=window.instances[0];
  first.controller.abort();
  first.app.dispose();
  first.app.dispose();
  first.app.element.remove();
 });
 assert.equal(await page.$$('.clockwork-view').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 assert.deepEqual(external,[]);
 console.log(`PASS ${process.env.CODI_PHONE?'phone':'desktop'} Babylon room, full puzzle loop, save/reopen, invalid recovery and disposal`);
}catch(error){
 console.error('FAIL',error.stack||error.message,'errors:',errors,'body:',await page.evaluate(()=>document.body.innerText.slice(0,1600)).catch(()=>''));
 throw error;
}finally{
 await context.close();
 await browser.disconnect();
}
