import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({
  browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19364',
  protocolTimeout:120000,
});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[];
const external=[];
const base=process.env.CODI_ORBITAL_URL||'http://127.0.0.1:18364/';
page.on('pageerror',error=>errors.push(error.message));
page.on('request',request=>{
  if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==new URL(base).origin)external.push(request.url());
});

const click=label=>page.evaluate(label=>{
  const root=document.querySelectorAll('.orbital-view')[0];
  const button=[...root.querySelectorAll('button')].find(node=>node.textContent===label||node.getAttribute('aria-label')===label);
  if(!button)throw Error('Missing button: '+label);
  button.click();
},label);

try{
  await page.setViewport(process.env.CODI_PHONE
    ?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}
    :{width:1366,height:900});
  const manifest=JSON.parse(await readFile(process.env.CODI_ORBITAL_MANIFEST||'.build/orbital-courier/apps.json','utf8'));
  const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
  await page.goto(base+'orbital-courier-fixture.html?app='+encodeURIComponent(entry));
  await page.waitForFunction(()=>window.instances?.length===2);
  await page.waitForFunction(()=>document.querySelectorAll('.orbital-stage canvas').length===2,{timeout:60000});
  assert.match(await page.$eval('.orbital-rive-pending',node=>node.textContent),/pending/i);
  await click('Resume');
  await page.waitForFunction(()=>document.querySelector('.orbital-view .app-status')?.textContent.includes('Mission running'));
  await new Promise(resolve=>setTimeout(resolve,250));
  const initialEnergy=await page.$eval('.orbital-panel',node=>node.textContent);
  assert.match(initialEnergy,/Energy:/);
  await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
  await page.waitForFunction(()=>document.querySelector('.orbital-view .app-status')?.textContent.includes('lost attention'));
  assert.ok(await page.$('.orbital-view button[aria-label="Resume"]'));
  await click('Resume');
  await page.evaluate(()=>document.querySelector('.orbital-save').open=true);
  await page.$eval('[aria-label="Orbital Courier save path"]',input=>input.value='/Orbital Courier.game.json');
  await click('Save to My files');
  await page.waitForFunction(()=>document.querySelector('.orbital-view .app-status')?.textContent.includes('syncing with the server'));
  const saved=JSON.parse(await page.evaluate(()=>new TextDecoder().decode(window.fileStore.get('/Orbital Courier.game.json').data)));
  assert.equal(saved.appId,'orbital-courier');
  assert.equal(saved.payload.missionId,0);
  assert.equal(saved.payload.paused,true);
  await page.evaluate(()=>window.targetPath='/Orbital Courier.game.json');
  await click('Open from My files');
  await page.waitForFunction(()=>document.querySelector('.orbital-view .app-status')?.textContent.includes('Mission loaded and paused'));
  assert.equal(await page.$eval('[aria-label="Orbital Courier save path"]',input=>input.value),'/Orbital Courier.game.json');
  await page.evaluate(()=>window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'}));
  await page.evaluate(()=>window.targetPath='/Bad.game.json');
  await click('Open from My files');
  await page.waitForFunction(()=>document.querySelector('.orbital-view .app-status')?.textContent.includes('Could not open mission'));
  await page.evaluate(()=>{const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove()});
  assert.equal(await page.$$eval('.orbital-view',nodes=>nodes.length),1);
  assert.deepEqual(errors,[]);
  assert.deepEqual(external,[]);
  if(process.env.CODI_PHONE==='1'){
    const sizes=await page.$$eval('.orbital-controls button',nodes=>nodes.map(node=>node.getBoundingClientRect().height));
    assert.ok(sizes.every(height=>height>=44),'phone controls must be at least 44px');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  }
  console.log(`PASS ${process.env.CODI_PHONE?'phone':'desktop'} Orbital Courier launch, run, focus pause, save, invalid-file recovery and disposal`);
}finally{
  await context.close();
  await browser.disconnect();
}
