import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {calculate} from '../apps/system/spreadsheet/formulas.mjs';
const cases=[['=-2^2',-4],['=(-2)^2',4],['=2^-2',0.25],['=2^3^2',512],['=2^-2^2',0.0625],['=-2^-2',-0.25],['=2*-3^2',-18],['=(-2)^3',-8]];
for(const [formula,value] of cases)assert.equal(calculate([[formula]],0,0).value,value,formula);
for(const formula of ['=0^-1','=(-1)^0.5','=1e999^0'])assert.equal(calculate([[formula]],0,0).error,'#ERROR!',formula);
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],user='sheetpow'+Date.now().toString().slice(-8)+process.pid,base=process.env.CODI_TEST_URL||'http://127.0.0.1:18591/';page.on('pageerror',e=>errors.push(e.message));
const button=label=>page.evaluate(label=>[...document.querySelectorAll('.spreadsheet-bar button')].find(e=>e.textContent===label).click(),label);
async function login(p,register){await p.goto(base);await p.waitForSelector('.login-toggle');if(register)await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');if(register)await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered')}
try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(page,true);console.log('Test account',user,await page.evaluate(()=>signedInSubject()));
 await page.evaluate(()=>surfaces.get('Desktop').launch('spreadsheet'));await page.waitForFunction(()=>document.querySelector('.spreadsheet-grid')?.spreadsheet?.worksheets?.[0]);
 await page.$eval('[aria-label="Spreadsheet file path"]',e=>e.value='/Power.codisheet');
 await page.evaluate(formulas=>{const sheet=document.querySelector('.spreadsheet-grid').spreadsheet.worksheets[0];for(const [i,formula] of formulas.entries())sheet.setValueFromCoords(i,0,formula)},cases.map(([formula])=>formula));
 await page.waitForFunction(values=>values.every((v,i)=>document.querySelector(`.spreadsheet-grid td[data-x="${i}"][data-y="0"]`)?.textContent===String(v)),{timeout:30000},cases.map(([,value])=>value));
 await button('Save');await page.waitForFunction(()=>document.querySelector('.spreadsheet-content .app-status')?.textContent.includes('Saved on this device'));await button('Export current sheet CSV');await page.waitForFunction(()=>document.querySelector('.spreadsheet-content .app-status')?.textContent.includes('CSV saved on this device'),{timeout:30000});
 const saved=await page.evaluate(async()=>{await(await mirrorFileContext()).files.sync();const server=(await serverFileContext()).files;return {sheet:new TextDecoder().decode((await server.read('Power.codisheet')).data),csv:new TextDecoder().decode((await server.read('Power.csv')).data)}});
 assert.equal(saved.csv,cases.map(([,value])=>'"'+value+'"').join(',')+'\r\n');assert.match(saved.sheet,/-2\^2/);
 const fresh=await browser.createBrowserContext();try{const q=await fresh.newPage();await login(q,false);await q.evaluate(async()=>{await(await mirrorFileContext()).files.sync();openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Power.codisheet')});await q.waitForFunction(()=>document.querySelector('.spreadsheet-grid td[data-x="0"][data-y="0"]')?.textContent==='-4',{timeout:30000})}finally{await fresh.close()}
 assert.deepEqual(errors,[]);console.log('PASS mathematical exponent precedence, CSV/server sync and fresh-session reopen');
}finally{await context.close();await browser.disconnect()}
