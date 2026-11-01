import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262'});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[],external=[];
const base=process.env.CODI_LANTERN_URL||'http://127.0.0.1:18351/';
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
page.on('request',request=>{
 if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==new URL(base).origin)external.push(request.url());
});

const clickFirst=label=>page.evaluate(label=>{
 const root=document.querySelectorAll('.lantern-view')[0];
 const button=[...root.querySelectorAll('button')].find(node=>node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 const phone=process.env.CODI_PHONE==='1';
 await page.setViewport(phone?{width:390,height:844,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_LANTERN_MANIFEST||'.build/lantern-leap-test/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.lantern-stage canvas').length===2,{timeout:30000});
 assert.match(await page.$$eval('.lantern-rive-pending',nodes=>nodes[0].textContent),/Rive artwork.*pending/i);
 assert.match(await page.$$eval('.lantern-objective',nodes=>nodes[0].textContent),/Lanterns 0\/3/);
 await clickFirst('Resume');
 await page.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent==='Lantern Leap running.');
 if(phone){
  const right=await page.$('.lantern-view [aria-label="Right ▶"]');
  const box=await right.boundingBox();
  await page.touchscreen.tap(box.x+box.width/2,box.y+box.height/2);
  await page.tap('.lantern-view [aria-label=Jump]');
 }else{
  await page.focus('.lantern-stage');
  await page.keyboard.down('ArrowRight');
  await new Promise(resolve=>setTimeout(resolve,180));
  await page.keyboard.press('Space');
  await page.keyboard.up('ArrowRight');
 }
 await new Promise(resolve=>setTimeout(resolve,220));
 await page.evaluate(()=>{
  document.querySelector('.lantern-save').open=true;
  document.querySelector('[aria-label="Lantern save path"]').value='/Lantern Leap.game.json';
 });
 await clickFirst('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent.includes('syncing with the server'));
 const saved=JSON.parse(await page.evaluate(()=>new TextDecoder().decode(window.fileStore.get('/Lantern Leap.game.json').data)));
 assert.equal(saved.appId,'lantern-leap');
 assert.ok(saved.payload.elapsedMs>0);

 await page.evaluate(()=>{
  fileStore.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});
  window.targetPath='/bad.game.json';
 });
 await clickFirst('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent.includes('Could not open checkpoint'));
 assert.match(await page.$eval('.lantern-objective',node=>node.textContent),/Room 1\/6/);
 await page.evaluate(()=>window.targetPath='/Lantern Leap.game.json');
 await clickFirst('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent.includes('Checkpoint loaded and paused'));
 assert.match(await page.$eval('.lantern-objective',node=>node.textContent),/Room 1\/6/);

 await page.evaluate(()=>{
  const first=window.instances[0];
  first.controller.abort();
  first.app.dispose();
  first.app.dispose();
  first.app.element.remove();
 });
 assert.equal(await page.$$('.lantern-stage canvas').then(nodes=>nodes.length),1);
 await page.evaluate(()=>document.querySelector('.lantern-view [aria-label=Resume]').click());
 await page.waitForFunction(()=>document.querySelector('.lantern-status')?.textContent==='Lantern Leap running.');
 assert.deepEqual(errors,[]);
 assert.deepEqual(external,[]);
 console.log('PASS two independent Lantern Leap windows, play input, save, invalid recovery, reopen and disposal');
}finally{
 await context.close();
 await browser.disconnect();
}
