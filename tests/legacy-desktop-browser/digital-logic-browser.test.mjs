// Against the local test harness prepared from the app bundle; see app README.
import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2});else if(process.env.CODI_4K==='1')await page.setViewport({width:3840,height:2160});
 const errors=[];let dismissNext=false;page.on('pageerror',error=>errors.push(error.message));page.on('dialog',d=>{if(dismissNext){dismissNext=false;return d.dismiss()}return d.accept()});
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18160/test.html');
 await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
 await page.waitForSelector('[model-id="lamp"] .led');await page.waitForSelector('[model-id="a"] .btnface');
 const lamp=()=>page.$eval('[model-id="lamp"] .led',e=>e.getAttribute('fill'));
 await page.waitForFunction(()=>document.querySelector('[model-id="lamp"] .led')?.getAttribute('fill')==='#fc7c68');const initial=await lamp();await page.click('[model-id="a"] .btnface');await new Promise(r=>setTimeout(r,150));assert.equal(await lamp(),initial,'one input does not turn on AND');
 await page.click('[model-id="b"] .btnface');await page.waitForFunction(color=>document.querySelector('[model-id="lamp"] .led')?.getAttribute('fill')!==color,{},initial);const on=await lamp();
 await page.click('[model-id="a"] .btnface');await page.waitForFunction(color=>document.querySelector('[model-id="lamp"] .led')?.getAttribute('fill')===color,{},initial);
 await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Save to My files').click());
 await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Saved /Circuit.logic.json'));
 assert.ok(await page.evaluate(()=>window.test.store.has('/Circuit.logic.json')));
 await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Open from My files').click());
 await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
 const tables={AND:[0,0,1,0],OR:[0,1,1,1],XOR:[0,1,0,1],NAND:[1,1,0,1],NOR:[1,0,0,0],XNOR:[1,0,1,0],NOT:[1,0]};
 for(const [name,expected] of Object.entries(tables)){
  await page.select('[aria-label="Gate example"]',name);await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Load example').click());
  await page.waitForFunction(n=>JSON.parse(document.querySelector('[aria-label="Circuit JSON"]').value).devices.gate.type.toUpperCase()===n,{},name);
  for(let i=0;i<expected.length;i++){
   if(i===1||i===3)await page.click('[model-id="a"] .btnface');else if(i===2)await page.click('[model-id="b"] .btnface');
   await new Promise(r=>setTimeout(r,150));assert.equal(await lamp(),expected[i]?on:initial,`${name} truth table row ${i}`);
  }
 }
 const before=await page.$eval('[aria-label="Circuit JSON"]',e=>e.value);await page.select('[aria-label="Gate example"]','AND');dismissNext=true;await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Load example').click());assert.equal(await page.$eval('[aria-label="Circuit JSON"]',e=>e.value),before,'declining replacement preserves the draft');
 await page.evaluate(()=>{const el=document.querySelector('[aria-label="Circuit JSON"]');el.value=JSON.stringify({devices:{a:{type:'Not',bits:1}},connectors:[{from:{id:'a',port:'out'},to:{id:'a',port:'in'}}]});[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Run').click()});await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.includes('Feedback loops are not supported'));assert.ok(await page.$('[model-id="lamp"] .led'),'invalid run preserves the previous simulation');
 await page.evaluate(()=>{window.test.app.dispose();window.test.app.element.remove();window.test.app=window.test.mount()});await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));await page.evaluate(()=>{window.test.app.dispose();window.test.app.element.remove()});assert.equal(await page.$('.digital-logic'),null);
 assert.deepEqual(errors,[]);console.log('PASS seven gate truth tables, replacement cancellation, save/open against mock host, disposal');
}finally{await context.close();await browser.disconnect()}
