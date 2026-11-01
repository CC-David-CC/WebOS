import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),phone=!!process.env.CODI_PHONE,base=process.env.CODI_TEST_URL||'http://127.0.0.1:18303/',user='tsvfiles'+Date.now().toString().slice(-8)+process.pid,errors=[];
page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>{errors.push('Unexpected browser dialog: '+d.message());d.dismiss()});
try {
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await page.evaluateOnNewDocument(()=>{const fetch0=window.fetch;window.fetch=(u,...args)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):fetch0(u,...args)});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});console.log('Test account',user,await page.evaluate(()=>signedInSubject()));
 await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/Measurements.TSV','name\tvalue\nvoltage\t12\n',null);await f.sync();surfaces.get('Desktop').launch('files')});
 await page.waitForSelector('[data-chonky-file-id="/Measurements.TSV"]',{timeout:30000});
 if(phone){await page.tap('[data-chonky-file-id="/Measurements.TSV"]');await page.waitForFunction(()=>[...document.querySelectorAll('.codi-chonky button')].some(b=>b.textContent.trim()==='Open'&&!b.disabled));const handle=await page.evaluateHandle(()=>[...document.querySelectorAll('.codi-chonky button')].find(b=>b.textContent.trim()==='Open'&&!b.disabled));await handle.asElement().tap();await handle.dispose();}
 else {await page.click('[data-chonky-file-id="/Measurements.TSV"]');await page.click('[data-chonky-file-id="/Measurements.TSV"]',{clickCount:2});}
 await page.waitForFunction(()=>document.querySelector('.data-explorer .app-status')?.textContent.startsWith('Ready.'),{timeout:120000});
 assert.deepEqual(await page.evaluate(async()=>await(await document.querySelector('perspective-viewer').getView()).to_json()),[{name:'voltage',value:12}]);
 assert.equal(await page.$eval('[aria-label="Data file path"]',e=>e.value),'/Measurements.TSV');assert.deepEqual(errors.filter(e=>!e.includes('RemoveHostedTablesUpdateReq')),[]);
 console.log('PASS Files opens uppercase TSV in Data Explorer with correct columns and values');
} finally {await context.close();await browser.disconnect()}
