// Against the local test harness prepared from the app bundle; see app README.
import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage();
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18160/test.html');
 await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
 await page.waitForSelector('[model-id="lamp"] .led');await page.waitForSelector('[model-id="a"] .btnface');
 const lamp=()=>page.$eval('[model-id="lamp"] .led',e=>e.getAttribute('fill'));
 await page.waitForFunction(()=>document.querySelector('[model-id="lamp"] .led')?.getAttribute('fill')==='#fc7c68');const initial=await lamp();await page.click('[model-id="a"] .btnface');await new Promise(r=>setTimeout(r,150));assert.equal(await lamp(),initial,'one input does not turn on AND');
 await page.click('[model-id="b"] .btnface');await page.waitForFunction(color=>document.querySelector('[model-id="lamp"] .led')?.getAttribute('fill')!==color,{},initial);
 await page.click('[model-id="a"] .btnface');await page.waitForFunction(color=>document.querySelector('[model-id="lamp"] .led')?.getAttribute('fill')===color,{},initial);
 await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Save to My files').click());
 await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Saved /Circuit.logic.json'));
 assert.ok(await page.evaluate(()=>window.test.store.has('/Circuit.logic.json')));
 await page.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Open from My files').click());
 await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
 await page.evaluate(()=>{const el=document.querySelector('[aria-label="Circuit JSON"]');el.value=JSON.stringify({devices:{a:{type:'Not',bits:1}},connectors:[{from:{id:'a',port:'out'},to:{id:'a',port:'in'}}]});[...document.querySelectorAll('.logic-toolbar button')].find(b=>b.textContent==='Run').click()});await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.includes('Feedback loops are not supported'));assert.ok(await page.$('[model-id="lamp"] .led'),'invalid run preserves the previous simulation');
 await page.evaluate(()=>{window.test.app.dispose();window.test.app.element.remove();window.test.app=window.test.mount()});await page.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));await page.evaluate(()=>{window.test.app.dispose();window.test.app.element.remove()});assert.equal(await page.$('.digital-logic'),null);
 assert.deepEqual(errors,[]);console.log('PASS AND truth table, save/open against mock host, disposal');
}finally{await context.close();await browser.disconnect()}
