import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',protocolTimeout:120000});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));

try{
 const phone=process.env.CODI_PHONE==='1';
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_STACK_MANIFEST||'.build/stack-balance/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 const base=process.env.CODI_STACK_URL||'http://127.0.0.1:18345/';
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForSelector('.stack-stage canvas',{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('build'),{timeout:30000});
 const click=async label=>{
  const selector=`.stack-view [aria-label="${label}"]`;
  if(phone){const element=await page.$(selector);assert.ok(element,selector);await element.scrollIntoView();await element.tap()}
  else await page.$eval(selector,element=>element.click());
 };
 await page.click('.stack-side summary');
 assert.equal(await page.$eval('[aria-label="Sound effects"]',node=>node.checked),false);
 assert.match(await page.$eval('.stack-rive-pending',node=>node.textContent),/placeholder/);
 await click('Run');
 await page.$eval('.stack-app',node=>node.closest('.window').classList.remove('focused'));
 await page.waitForFunction(()=>document.querySelector('.stack-view [aria-label="Run"]'));
 assert.match(await page.$eval('.stack-view .app-status',node=>node.textContent),/paused/i);
 await page.$eval('.stack-app',node=>node.closest('.window').classList.add('focused'));
 await click('Run');
 for(let i=0;i<4;i++)await click('Release block');
 await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('settle'));
 await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('won'),{timeout:10000});
 await page.$eval('.stack-save',node=>node.open=true);
 await page.$eval('[aria-label="Stack save path"]',node=>node.value='/Stack Balance.game.json');
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('Tower saved to My files'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Stack Balance.game.json').data)));
 assert.equal(saved.appId,'stack-balance');
 assert.equal(saved.payload.phase,'won');
 assert.equal(saved.payload.blocks.length,4);
 assert.equal(saved.payload.nudgeApplied,true);
 await click('Restart');
 await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('build'));
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('Tower loaded and paused'));
 assert.match(await page.$eval('.stack-info',node=>node.textContent),/won/);
 await page.evaluate(()=>{window.test.store.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'});globalThis.target='/bad.game.json'});
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('Could not open tower'));
 assert.match(await page.$eval('.stack-info',node=>node.textContent),/won/);
 await page.evaluate(()=>window.test.dispose());
 await page.waitForFunction(()=>!document.querySelector('.stack-view'));
 assert.deepEqual(errors,[]);
 console.log(`PASS ${phone?'phone':'desktop'} Stack render, block sequence, dwell/nudge, save/reset/reopen, invalid recovery and disposal`);
}catch(error){
 console.error('Diagnostics:',await page.evaluate(()=>({
  status:document.querySelector('.stack-view .app-status')?.textContent,
  info:document.querySelector('.stack-info')?.textContent,
  stored:[...window.test?.store??[]].map(([path,item])=>({path,status:item.status,bytes:item.data.byteLength})),
 })).catch(()=>null));
 throw error;
}finally{
 await context.close();
 await browser.disconnect();
}
