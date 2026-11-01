import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18992/';
const username='measure'+Date.now().toString().slice(-8)+process.pid;
const action=label=>page.evaluate(label=>[...document.querySelectorAll('.spreadsheet-bar button')].find(e=>e.textContent===label).click(),label);
const value=()=>page.evaluate(()=>document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0].options.data);
try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]',username);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
 await page.evaluate(()=>surfaces.get('Desktop').launch('spreadsheet'));
 await page.waitForFunction(()=>!!document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]);
 await action('Try measurement example');
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]?.options.data[4]?.[1]==='=AVERAGE(B2:B4)');
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[title="=AVERAGE(B2:B4)"]')?.textContent==='9.96666666667');
 await page.evaluate(()=>document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0].setValueFromCoords(1,1,'12'));
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[title="=AVERAGE(B2:B4)"]')?.textContent==='10.7');
 await page.evaluate(()=>document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0].setValueFromCoords(2,4,'=B5*1000000000000000'));
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[title="=B5*1000000000000000"]')?.getAttribute('aria-label')?.includes('10700000000000002'));
 await action('Try measurement example');await page.waitForSelector('dialog[open]');
 await page.evaluate(()=>[...document.querySelectorAll('dialog[open] button')].find(e=>e.textContent==='Keep editing').click());
 await page.waitForFunction(()=>!document.querySelector('dialog[open]'));assert.equal((await value())[1][1],'12');
 await action('Export current sheet CSV');await page.waitForFunction(()=>document.querySelector('.spreadsheet-content .app-status')?.textContent.includes('CSV saved on this device'));
 const csv=await page.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Example-measurements.csv')).data));assert.match(csv,/10\.700000000000001/);assert.match(csv,/10700000000000002/);
 await page.$eval('.spreadsheet-content details summary',e=>e.click());
 const precision=await page.$('[aria-label="Show full floating-point precision"]');assert.ok(precision);await precision.click();
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[title="=AVERAGE(B2:B4)"]')?.textContent==='10.700000000000001');
 await action('Save');await page.waitForFunction(()=>document.querySelector('.spreadsheet-content .app-status')?.textContent.includes('Saved on this device'));
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Example-measurements.codisheet')).data)));
 assert.equal(saved.sheets[0].data[1][1],'12');assert.equal(saved.sheets[0].data[4][1],'=AVERAGE(B2:B4)');
 await page.evaluate(()=>document.querySelector('.spreadsheet-content').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.spreadsheet-content'));
 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Example-measurements.codisheet'));
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]?.options.data[1]?.[1]==='12');
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[title="=AVERAGE(B2:B4)"]')?.textContent==='10.700000000000001');
 assert.equal(await page.$eval('[aria-label="Show full floating-point precision"]',e=>e.checked),true);
 const fresh=await browser.createBrowserContext(),other=await fresh.newPage();
 try{
  await other.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
  await other.goto(base);await other.waitForSelector('[aria-label=Username]');await other.type('[aria-label=Username]',username);await other.type('[aria-label=Password]','test1234');await other.click('.login-form button[type=submit]');
  await other.waitForFunction(()=>window.desktopLab?.session?.kind==='registered');
  await other.evaluate(async()=>{await(await mirrorFileContext()).files.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Example-measurements.codisheet')});
  await other.waitForFunction(()=>document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]?.options.data[1]?.[1]==='12');
  await other.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[title="=AVERAGE(B2:B4)"]')?.textContent==='10.7');
  assert.equal(await other.$eval('[aria-label="Show full floating-point precision"]',e=>e.checked),false);
 }finally{await fresh.close()}
 console.log('PASS measurement example, formula update, cancel, account sync and fresh-session reopen');
}finally{await context.close();await browser.disconnect()}
