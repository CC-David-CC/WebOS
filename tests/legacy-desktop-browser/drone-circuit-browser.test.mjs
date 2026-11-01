import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_DRONE_URL||'http://127.0.0.1:18345/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
const click=label=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.drone-view button')].find(node=>node.textContent===label);
 if(!button)throw Error('Missing button: '+label);button.click();
},label);
try{
 await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_DRONE_MANIFEST||'.build/drone-circuit/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto(base+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForSelector('.drone-stage-wrap canvas',{timeout:30000});
 assert.equal(await page.$$eval('.drone-stage-wrap canvas',nodes=>nodes.length),2);
 assert.match(await page.$eval('.drone-rive-pending',node=>node.textContent),/Rive artwork.*pending/i);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'no horizontal overflow');
 if(process.env.CODI_PHONE)assert.equal(await page.$$eval('.drone-toolbar button,.drone-phone-controls button',nodes=>nodes.every(node=>node.getBoundingClientRect().height>=44)),true,'phone controls are at least 44px high');
 await click('Run');
 await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('Flight active'));
 await new Promise(resolve=>setTimeout(resolve,500));
 await page.evaluate(()=>window.instances[0].win.classList.remove('focused'));
 await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('lost attention'));
 await page.evaluate(()=>window.instances[0].win.classList.add('focused'));
 await page.evaluate(()=>window.dispatchEvent(new Event('blur')));
 assert.equal(await page.$eval('.drone-view [aria-label="Run"]',node=>node.textContent),'Run','focus loss pauses');
 await click('Run');
 await page.evaluate(()=>document.querySelector('.drone-save').open=true);
 await page.$eval('[aria-label="Drone save path"]',node=>node.value='/Drone Circuit.game.json');
 await page.evaluate(()=>{const files=window.fileContext.files,write=files.write.bind(files);window.__restoreWrite=()=>files.write=write;files.write=async(...args)=>{await new Promise(resolve=>window.__releaseWrite=resolve);return write(...args)}});
 await click('Save to My files');
 await page.waitForFunction(()=>typeof window.__releaseWrite==='function');
 assert.equal(await page.evaluate(()=>window.instances[0].w.droneCircuit.dirty),true,'pending save keeps close protection');
 await page.evaluate(()=>window.__releaseWrite());
 await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('syncing with the server'));
 await page.evaluate(()=>window.__restoreWrite());
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Drone Circuit.game.json').data)));
 assert.equal(saved.appId,'drone-circuit');
 await page.evaluate(()=>{window.fileStore.set('/bad.game.json',{data:new TextEncoder().encode('{bad'),version:'bad',status:'synced'})});
 await page.evaluate(()=>window.target='/bad.game.json');
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.drone-status')?.textContent.includes('Could not open flight'));
 assert.match(await page.$eval('.drone-status',node=>node.textContent),/Could not open flight/);
 await page.evaluate(()=>{window.instances[0].controller.abort();window.instances[0].app.dispose();window.instances[0].app.dispose();window.instances[0].app.element.remove()});
 assert.equal(await page.$$('.drone-stage-wrap canvas').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 console.log('PASS two Babylon drone instances, run, focus pause, save, invalid recovery and disposal');
}catch(error){
 console.error('Diagnostics:',await page.evaluate(()=>({body:document.body.innerText.slice(0,1200),status:[...document.querySelectorAll('.drone-status')].map(node=>node.textContent)})).catch(()=>null));
 throw error;
}finally{await context.close();await browser.disconnect()}
