import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262'});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
const phone=process.env.CODI_PHONE==='1';
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
page.on('request',request=>{if(/^https?:/.test(request.url())&&new URL(request.url()).hostname!=='127.0.0.1')external.push(request.url())});
const click=label=>page.evaluate(label=>{
 const root=document.querySelector('.chess-study');
 const element=[...root.querySelectorAll('button')].find(node=>node.textContent===label);
 if(!element)throw Error('Missing button: '+label);
 element.click();
},label);
const tapSquare=async(square)=>{
 const file='abcdefgh'.indexOf(square[0]),rank=Number(square[1]),col=file,row=8-rank;
 const box=await (await page.$('.chess-board')).boundingBox();
 if(phone)await page.touchscreen.tap(box.x+(col+.5)*box.width/8,box.y+(row+.5)*box.height/8);
 else await page.mouse.click(box.x+(col+.5)*box.width/8,box.y+(row+.5)*box.height/8);
};
try{
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_CHESS_MANIFEST||'.build/chess-study-test/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_CHESS_URL||'http://127.0.0.1:18339/')+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForSelector('.chess-board',{timeout:30000});
 assert.equal(await page.$$eval('.chess-board',nodes=>nodes.length),2);
 assert.match(await page.$eval('.chess-guide',node=>node.textContent),/Rive artwork pending/);
 assert.equal(await page.$eval('[aria-label="Sound effects"]',node=>node.checked),false);

 await page.select('[aria-label="Study mode"]','exercise');
 await page.select('[aria-label="Exercise"]','back-rank-a');
 await click('New game');
 await click('Resume');
 await tapSquare('a1');await tapSquare('a8');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Exercise solved'));

 await page.evaluate(()=>document.querySelector('.chess-save').open=true);
 await page.$eval('[aria-label="Chess save path"]',node=>node.value='/Chess Study.game.json');
 await click('Save to My files');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('syncing with the server'));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Chess Study.game.json').data)));
 assert.equal(saved.appId,'chess-study');
 assert.equal(saved.payload.result,'exercise-solved');
 assert.equal(saved.payload.history.length,1);

 await page.select('[aria-label="Study mode"]','game');
 await page.select('[aria-label="AI difficulty"]','1');
 await click('New game');
 await click('Resume');
 await tapSquare('e2');await tapSquare('e4');
 await page.waitForFunction(()=>!document.querySelector('.chess-history')?.textContent.includes('Moves: —'),{timeout:30000});
 await page.waitForFunction(()=>document.querySelector('.chess-history')?.textContent.trim().split(/\s+/).length>=3,{timeout:30000});
 assert.match(await page.$eval('.chess-info',node=>node.textContent),/White to move/);
 await page.evaluate(()=>window.instances[0].element.classList.remove('focused'));
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent==='Game paused.');
 assert.equal(await page.$eval('.chess-toolbar [aria-label="Resume"]',node=>node.textContent),'Resume');
 await page.evaluate(()=>window.instances[0].element.classList.add('focused'));
 await click('Resume');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Resume play'));

 await page.evaluate(()=>{window.fileStore.set('/Bad.game.json',{data:new TextEncoder().encode('{"format":"wrong"}'),version:'bad',status:'synced'});window.targetPath='/Bad.game.json'});
 await click('Open from My files');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Could not open'));
 await page.evaluate(()=>{const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove()});
 assert.equal(await page.$$('.chess-board').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 console.log('PASS two independent chess views, exercise, local AI worker, save, focus pause, invalid recovery and disposal');
}finally{
 await context.close();await browser.disconnect();
}
