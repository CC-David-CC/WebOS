import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';
const b=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255',protocolTimeout:120000}),c=await b.createBrowserContext(),p=await c.newPage();
const pause=ms=>new Promise(r=>setTimeout(r,ms));
try{
 const phone=process.env.CODI_PHONE==='1';await p.setViewport(phone?{width:412,height:915,deviceScaleFactor:2,isMobile:true,hasTouch:true}:{width:1200,height:900});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18163/test.html');
 const frame=await(await p.waitForSelector('iframe')).contentFrame();await frame.waitForFunction(()=>window.Module?.FS&&document.querySelector('#status').hidden,{timeout:120000});
 await p.evaluate(()=>[...document.querySelectorAll('.electronics-design-bar button')].find(b=>b.textContent==='Open from My files').click());
 await p.waitForFunction(()=>document.querySelector('.electronics-design-status')?.textContent.startsWith('Opening'));await pause(1500);
 if(!phone){await frame.click('#canvas',{offset:{x:410,y:225}});await pause(1200)}
 // SDL samples keyboard state on animation frames; hold the key long enough for one frame.
 await frame.click('#canvas',{offset:{x:200,y:160}});await p.keyboard.down('Control');await p.keyboard.down('Shift');await p.keyboard.down('s');await pause(250);await p.keyboard.up('s');await p.keyboard.up('Shift');await p.keyboard.up('Control');
 await p.waitForFunction(()=>document.querySelector('.electronics-design-status')?.textContent.startsWith('Editor output ready'),{timeout:30000});
 await p.evaluate(()=>[...document.querySelectorAll('.electronics-design-bar button')].find(b=>b.textContent==='Save to My files').click());
 await p.waitForFunction(()=>document.querySelector('.electronics-design-status')?.textContent.startsWith('Saved '));
 const result=await p.evaluate(()=>{const saved=[...window.test.store].find(([k])=>k!=='/sample.dez');const project=JSON.parse(new TextDecoder().decode(saved[1].data));return {key:saved[0],title:project.title,pcb:project.wires.filter(w=>w.view==='pcb').length}});
 assert.equal(result.title,'LED with battery');if(!phone)assert.equal(result.pcb,3,'editor autorouted all three PCB connections');
 await p.evaluate(()=>{window.test.app.dispose();window.test.app.element.remove()});assert.equal(await p.$('iframe'),null);assert.deepEqual(errors,[]);
 console.log('PASS real WASM editor, example open, '+(phone?'phone capture':'PCB autoroute')+', captured project saved through mock My files',result);
}finally{await c.close();await b.disconnect()}
