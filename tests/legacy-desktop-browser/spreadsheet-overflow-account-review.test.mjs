import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19468/',user='sheetoverflow'+Date.now().toString().slice(-8)+process.pid;
let fresh;
async function login(p,register){await p.evaluateOnNewDocument(()=>{const old=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):old(u,...a)});await p.goto(base);await p.waitForSelector('.login-toggle');if(register)await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');if(register)await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});}
const view=process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900};
try{
 await page.setViewport(view);await login(page,true);
 await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/Measurement.codisheet',JSON.stringify({format:'codi-spreadsheet/1',sheets:[{name:'Measurements',data:[['Measurement'],['1e309'],['1'],['=AVERAGE(A2:A3)']]}]}),null);await f.write('/Measurement.csv','previous result',null);await f.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Measurement.codisheet')});
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]?.getCell(0,3)?.textContent==='#ERROR!',{timeout:30000});
 await page.evaluate(()=>[...document.querySelectorAll('.spreadsheet-bar button')].find(x=>x.textContent==='Export current sheet CSV').click());
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-content .app-status')?.textContent.includes('unsupported or invalid formula'),{timeout:30000});
 assert.equal(await page.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Measurement.csv')).data)),'previous result');
 await page.evaluate(()=>document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0].setValueFromCoords(0,1,'9'));
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0].getCell(0,3)?.textContent==='5');
 await page.evaluate(()=>[...document.querySelectorAll('.spreadsheet-bar button')].find(x=>x.textContent==='Save').click());
 await page.waitForFunction(async()=>{try{const f=await(await mirrorFileContext()).files.read('/Measurement.codisheet');return f.status==='synced'&&new TextDecoder().decode(f.data).includes('AVERAGE')}catch{return false}},{timeout:45000});
 fresh=await browser.createBrowserContext();const other=await fresh.newPage();await other.setViewport(view);await login(other,false);await other.evaluate(async()=>{await(await mirrorFileContext()).files.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Measurement.codisheet')});await other.waitForFunction(()=>document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]?.getCell(0,3)?.textContent==='5',{timeout:30000});
 console.log('PASS overflowing measurement error, protected CSV, corrected average, account sync and fresh reopen');
}finally{if(fresh)await fresh.close();await context.close();await browser.disconnect()}
