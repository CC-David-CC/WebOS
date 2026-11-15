import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const b=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255',protocolTimeout:120000}),ctx=await b.createBrowserContext(),p=await ctx.newPage(),base=process.env.CODI_TEST_URL||'http://127.0.0.1:18873/',user='logicui'+Date.now().toString().slice(-9);
try{
 await p.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 await p.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
 await p.goto(base);await p.waitForSelector('.login-toggle');await p.click('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.type('[aria-label="Confirm password"]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await p.evaluate(()=>surfaces.get('Desktop').launch('digital-logic'));await p.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'),{timeout:30000});
 assert.equal(await p.$eval('.logic-advanced',e=>e.open),false);assert.equal(await p.$eval('[aria-label="Circuit JSON"]',e=>e.checkVisibility({contentVisibilityAuto:true})),false);
 await p.click('.logic-advanced summary');assert.equal(await p.$eval('.logic-advanced',e=>e.open),true);assert.equal(await p.$eval('[aria-label="Circuit JSON"]',e=>e.checkVisibility({contentVisibilityAuto:true})),true);
 await p.evaluate(()=>{const e=document.querySelector('[aria-label="Circuit JSON"]'),x=JSON.parse(e.value);x.devices.lamp.label='Student output';e.value=JSON.stringify(x,null,2);e.dispatchEvent(new Event('input',{bubbles:true}))});
 await p.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(e=>e.textContent==='Run').click());await p.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
 await p.evaluate(()=>[...document.querySelectorAll('.logic-toolbar button')].find(e=>e.textContent==='Save to My files').click());await p.waitForFunction(()=>document.querySelector('.logic-status')?.textContent.startsWith('Saved /Circuit.logic.json'));
 await p.evaluate(async()=>{const c=await mirrorFileContext();await c.files.sync();const file=await c.files.read('/Circuit.logic.json');if(file.status!=='synced'||!new TextDecoder().decode(file.data).includes('Student output'))throw Error('Saved circuit did not sync')});
 console.log('PASS example-first layout, advanced editor, run and saved circuit sync');
}finally{await ctx.close();await b.disconnect()}
