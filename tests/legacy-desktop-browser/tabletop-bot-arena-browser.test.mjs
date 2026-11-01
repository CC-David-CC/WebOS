import assert from 'node:assert/strict';
import {copyFile,readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_ARENA_BASE||'http://127.0.0.1:18466/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19466',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
try{
  const phone=process.env.CODI_PHONE==='1';
  await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
  page.on('pageerror',error=>errors.push(error.message));
  page.on('request',request=>{if(/^https?:/.test(request.url())&&!request.url().startsWith(base))external.push(request.url())});
  const manifest=JSON.parse(await readFile(process.env.CODI_ARENA_MANIFEST||'.build/tabletop-bot-arena/apps.json','utf8'));
  const record=manifest.apps.find(app=>app.id==='tabletop-bot-arena');assert.ok(record);
  const entry='/'+record.path.replace(/^assets\/desktop\//,'');
  await copyFile('tests/tabletop-bot-arena-fixture.html','.build/tabletop-bot-arena/tabletop-bot-arena-fixture.html');
  await page.goto(base+'tabletop-bot-arena-fixture.html?app='+encodeURIComponent(entry));
  await page.waitForSelector('.arena-stage canvas',{timeout:60000});
  await page.waitForFunction(()=>document.querySelector('.arena-score-output')?.textContent.includes('s'));
  const click=async label=>{const element=await page.$(`[aria-label="${label}"]`);assert.ok(element,label);if(phone){await element.scrollIntoView();await element.tap()}else await element.click()};
  await click('Start');await page.waitForFunction(()=>document.querySelector('[aria-label="Start"]')?.textContent==='Pause');
  await page.keyboard.down('d');await new Promise(resolve=>setTimeout(resolve,180));await page.keyboard.up('d');await click('Weapon');
  await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
  await page.waitForFunction(()=>document.querySelector('[aria-label="Start"]')?.textContent==='Start / resume');
  await click('Save match');await page.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Match saved'));
  const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Tabletop Bot Arena.game.json').data)));
  assert.equal(saved.appId,'tabletop-bot-arena');assert.equal(saved.kind,'match-snapshot');assert.equal(saved.payload.paused,true);assert.ok(saved.payload.worldSnapshot.length>0);
  await click('Save cup progress');await page.waitForFunction(()=>window.test.store.has('/Tabletop Bot Arena cup.game.json'));
  const cup=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Tabletop Bot Arena cup.game.json').data)));
  assert.equal(cup.kind,'cup-progress');
  await page.evaluate(()=>{window.test.store.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});globalThis.target='/bad.game.json'});
  await click('Open from My files');await page.waitForFunction(()=>document.querySelector('.arena-side > .app-status')?.textContent.includes('Could not open arena'));
  await page.evaluate(()=>window.test.dispose());await page.waitForFunction(()=>!document.querySelector('.arena-view'));
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log(`PASS ${phone?'phone':'desktop'} Tabletop Bot Arena drive, weapon, focus pause, match/cup save, invalid recovery and disposal`);
}finally{await context.close();await browser.disconnect()}
