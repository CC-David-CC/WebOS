import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262'});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
const base=process.env.CODI_PUPPET_URL||'http://127.0.0.1:18349/';

const click=label=>page.evaluate(label=>{
 const first=document.querySelectorAll('.puppet-view')[0];
 const button=[...first.querySelectorAll('button')].find(node=>node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 const phone=process.env.CODI_PHONE==='1';
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_PUPPET_MANIFEST||'.build/expression-puppet-test/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll('.puppet-face').length===2,{timeout:30000});
 assert.equal(await page.$$eval('.puppet-face',nodes=>nodes.length),2);
 assert.match(await page.$$eval('.puppet-rive-pending',nodes=>nodes[0].textContent),/artwork.*pending/i);
 await page.click('.puppet-settings summary');
 assert.equal(await page.$eval('[aria-label="Sound effects"]',node=>node.checked),false);

 await page.select('[aria-label="Expression challenge"]','0');
 const target=await page.$eval('.puppet-target-text',node=>node.textContent);
 const values={
  'Look X':Number(target.match(/Look (-?\d+\.\d+),/)[1]),
  'Look Y':Number(target.match(/Look -?\d+\.\d+, (-?\d+\.\d+)/)[1]),
  Smile:Number(target.match(/Smile (\d+\.\d+)/)[1]),
  Eyebrow:Number(target.match(/Brow (-?\d+\.\d+)/)[1]),
  Pose:Number(target.match(/Pose (\d+)/)[1]),
 };
 for(const [label,value] of Object.entries(values)){
  await page.evaluate(({label,value})=>{
   const input=document.querySelector(`.puppet-view [aria-label="${label}"]`);
   input.value=String(value);
   input.dispatchEvent(new Event('input',{bubbles:true}));
  },{label,value});
 }
 await click('Resume');
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 await page.waitForFunction(()=>document.querySelector('.puppet-view [aria-label="Resume"]'));
 await click('Resume');
 await page.evaluate(()=>window.instances[0].app.element.closest('.window').classList.remove('focused'));
 await page.waitForFunction(()=>document.querySelectorAll('.puppet-view')[0].querySelector('.puppet-status').textContent.includes('paused'));
 await page.evaluate(()=>window.instances[0].app.element.closest('.window').classList.add('focused'));
 await click('Resume');
 await click('Match pose');
 await page.waitForFunction(()=>document.querySelector('.puppet-score')?.textContent.includes('100/100'));
 await click('Save pose 1');
 assert.equal(await page.$eval('[data-slot="0"]',node=>node.dataset.saved),'true');

 await page.evaluate(()=>document.querySelector('.puppet-save').open=true);
 await page.$eval('[aria-label="Puppet save path"]',node=>node.value='/Puppet Test.game.json');
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.puppet-status')?.textContent.includes('syncing with the server'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Puppet Test.game.json').data)));
 assert.equal(saved.appId,'expression-puppet');
 assert.deepEqual(saved.payload.slots[0],{
  lookX:values['Look X'],
  lookY:values['Look Y'],
  smile:values.Smile,
  eyebrow:values.Eyebrow,
  pose:values.Pose,
 });

 await page.$eval('[aria-label="Puppet save path"]',node=>node.value='/Slow Puppet.game.json');
 await page.evaluate(()=>{window.__holdWrite=()=>new Promise(resolve=>window.__releaseWrite=resolve);});
 await click('Save to My files');
 await page.waitForFunction(()=>typeof window.__releaseWrite==='function');
 await page.evaluate(()=>{const input=document.querySelector('.puppet-view [aria-label="Smile"]');input.value='.1';input.dispatchEvent(new Event('input',{bubbles:true}));window.__releaseWrite();});
 await page.waitForFunction(()=>document.querySelector('.puppet-status')?.textContent.includes('newer edits remain unsaved'));
 const slow=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Slow Puppet.game.json').data)));
 assert.equal(slow.payload.slots[0].smile,values.Smile);
 assert.equal(slow.payload.values.smile,values.Smile);
 await page.evaluate(()=>{window.__holdWrite=null;window.__releaseWrite=null;});

 await page.evaluate(()=>{
  window.fileStore.set('/bad.game.json',{data:new TextEncoder().encode('{"format":"wrong"}'),version:'bad',status:'synced'});
  window.targetPath='/bad.game.json';
 });
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.puppet-status')?.textContent.includes('Could not open'));
 assert.equal(await page.$eval('.puppet-score',node=>node.textContent),'Match score: 100/100');

 await page.evaluate(()=>{
  const first=window.instances[0];
  first.controller.abort();
  first.app.dispose();
  first.app.dispose();
  first.app.element.remove();
 });
 assert.equal(await page.$$('.puppet-face').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 console.log(`PASS ${phone?'phone':'desktop'} two puppet instances, controls, challenge match, slots, save, invalid load and disposal`);
}finally{
 await context.close();
 await browser.disconnect();
}
