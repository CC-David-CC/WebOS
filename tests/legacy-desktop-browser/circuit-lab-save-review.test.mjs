import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18403/';
if(new URL(base).hostname!=='127.0.0.1')throw Error('Loopback only');
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19266'}),context=await browser.createBrowserContext(),p=await context.newPage();
const username='circ'+crypto.randomUUID().replaceAll('-','').slice(0,12);
const click=label=>p.evaluate(x=>[...document.querySelectorAll('.circuit-lab button')].find(b=>b.textContent===x).click(),label);
const status=()=>p.$eval('.circuit-status',e=>e.textContent);
try{
 await p.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');
 await p.type('[aria-label=Username]',username);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');
 await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/existing.cir','* Existing\nV1 a 0 1\nR1 a 0 1k\n.op\n.end\n',null);await c.files.sync()});
 await p.evaluate(()=>[...surfaces.values()][0].launch('arduino-simulator'));await p.waitForSelector('.circuit-source');
 await p.$eval('[aria-label="Circuit file path"]',e=>e.value='/existing.cir');await click('Save to My files');await p.waitForSelector('dialog.codi-confirm-dialog[open]');
 await p.click('.codi-confirm-actions button:first-child');await p.waitForFunction(()=>document.querySelector('.circuit-status').textContent.includes('save cancelled'));
 let content=await p.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/existing.cir')).data));assert.match(content,/Existing/);
 await click('Save to My files');await p.waitForSelector('dialog.codi-confirm-dialog[open]');
 await p.$eval('.circuit-source',e=>{e.value+='\n* newer change';e.dispatchEvent(new Event('input',{bubbles:true}))});
 await p.click('.codi-confirm-danger');await p.waitForFunction(()=>document.querySelector('.circuit-status').textContent.includes('newer edits remain unsaved'));
 await click('Save to My files');await p.waitForFunction(()=>document.querySelector('.circuit-status').textContent.startsWith('Saved on this device'));
 content=await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();return new TextDecoder().decode((await c.files.read('/existing.cir')).data)});assert.match(content,/newer change/);
 await click('Run');await p.waitForFunction(()=>/Simulation finished|Simulation failed/.test(document.querySelector('.circuit-status').textContent),{timeout:35000});assert.match(await status(),/Simulation finished/);assert.match(await p.$eval('.circuit-results',e=>e.textContent),/v\(out\): 5\.00000/);
 await p.$eval('[aria-label="Circuit file path"]',e=>e.value='/other.cir');await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/other.cir','external original',null)});
 await click('Save to My files');await p.waitForSelector('dialog.codi-confirm-dialog[open]');
 await p.evaluate(async()=>{const c=await mirrorFileContext(),f=await c.files.read('/other.cir');await c.files.write('/other.cir','external newer',f.version)});await p.click('.codi-confirm-danger');await p.waitForFunction(()=>document.querySelector('.circuit-status').textContent.startsWith('Could not save'));
 content=await p.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/other.cir')).data));assert.equal(content,'external newer');
 const c2=await browser.createBrowserContext(),q=await c2.newPage();
 try {
  await q.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
  await q.goto(base);await q.waitForSelector('.login-toggle');await q.type('[aria-label=Username]',username);await q.type('[aria-label=Password]','test1234');await q.click('.login-form button[type=submit]');await q.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
  await q.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync()});await q.evaluate(()=>[...surfaces.values()][0].launch('arduino-simulator'));await q.waitForSelector('.circuit-source');
  await q.evaluate(()=>[...document.querySelectorAll('.circuit-lab button')].find(b=>b.textContent==='Open My files').click());await q.waitForSelector('[aria-label="Choose file existing.cir"]');await q.click('[aria-label="Choose file existing.cir"]');await q.waitForFunction(()=>document.querySelector('.circuit-status').textContent.startsWith('Opened'));
  assert.match(await q.$eval('.circuit-source',e=>e.value),/newer change/);
 }finally{await c2.close()}
 console.log('PASS account-backed Circuit Lab confirmation, edit-during-save, stale overwrite protection and real ngspice run');
}finally{await context.close();await browser.disconnect()}
