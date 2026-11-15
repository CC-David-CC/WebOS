import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
import {calculate} from '../apps/system/spreadsheet/formulas.mjs';
for (const [values,expected] of [[[1e16,1,-1e16],1], [[-1e16,-1,1e16],-1], [[1e16,1,1,-1e16],2], [[0.1,0.2,0.3],0.6]]) { const rows=values.map(value=>[value]);rows.push(['=SUM(A1:A'+values.length+')']);assert.equal(calculate(rows,values.length,0).value,expected); }
assert.equal(calculate([[1e308],[1e308],['=SUM(A1:A2)']],2,0).error,'#ERROR!');
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage();
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:19468/',user='sheetsum'+Date.now().toString().slice(-8)+process.pid;
if(!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(base))throw Error('This test requires an isolated loopback preview.');
let fresh;
async function login(p,register){await p.evaluateOnNewDocument(()=>{const old=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):old(u,...a)});await p.goto(base);await p.waitForSelector('.login-toggle');if(register)await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');if(register)await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});}
const view=process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900};
try{
 await page.setViewport(view);await login(page,true);
 await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/Measurement.codisheet',JSON.stringify({format:'codi-spreadsheet/1',sheets:[{name:'Measurements',data:[['Measurement'],['10000000000000000'],['1'],['-10000000000000000'],['=SUM(A2:A4)'],['=AVERAGE(A2:A4)']]}]}),null);await f.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Measurement.codisheet')});
 await page.waitForFunction(()=>{const s=document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0];return s?.getCell(0,4)?.textContent==='1'&&s?.getCell(0,5)?.textContent.startsWith('0.333333333333')},{timeout:30000});
 await page.evaluate(()=>document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0].setValueFromCoords(0,2,'2'));
 await page.waitForFunction(()=>{const s=document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0];return s?.getCell(0,4)?.textContent==='2'&&s?.getCell(0,5)?.textContent.startsWith('0.666666666667')},{timeout:30000});
 await page.evaluate(()=>[...document.querySelectorAll('.spreadsheet-bar button')].find(x=>x.textContent==='Save').click());
 await page.waitForFunction(async()=>{try{const f=await(await mirrorFileContext()).files.read('/Measurement.codisheet');return f.status==='synced'&&new TextDecoder().decode(f.data).includes('AVERAGE')}catch{return false}},{timeout:45000});
 await page.evaluate(()=>[...document.querySelectorAll('.spreadsheet-bar button')].find(x=>x.textContent==='Export current sheet CSV').click());
 await page.waitForFunction(()=>document.querySelector('.spreadsheet-content .app-status')?.textContent.includes('CSV saved'),{timeout:30000});
 const csv=await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.sync();return new TextDecoder().decode((await(await serverFileContext()).files.read('Measurement.csv')).data)});assert.match(csv,/(?:^|\r?\n)"2"(?:\r?\n)/);assert.match(csv,/0\.6666666666666666/);
 await page.evaluate(()=>document.querySelector('.spreadsheet-content').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.spreadsheet-content'),{timeout:30000});
 fresh=await browser.createBrowserContext();const other=await fresh.newPage();await other.setViewport(view);await login(other,false);await other.evaluate(async()=>{await(await mirrorFileContext()).files.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Measurement.codisheet')});await other.waitForFunction(()=>{const s=document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0];return s?.getCell(0,4)?.textContent==='2'&&s?.getCell(0,5)?.textContent.startsWith('0.666666666667')},{timeout:30000});
 assert.equal(await other.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Measurement.csv')).data)),csv);
 console.log('PASS compensated sum and average, edit, CSV export, server sync, close and fresh account reopen');
}finally{if(fresh)await fresh.close();await context.close();await browser.disconnect()}
