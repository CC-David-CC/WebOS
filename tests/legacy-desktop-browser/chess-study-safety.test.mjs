import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19338'});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('dialog',dialog=>dialog.accept());
const click=label=>page.evaluate(label=>{
 const root=document.querySelector('.chess-study');
 const element=[...root.querySelectorAll('button')].find(node=>node.textContent===label);
 if(!element)throw Error('Missing button: '+label);
 element.click();
},label);
const tapSquare=async square=>{
 const col='abcdefgh'.indexOf(square[0]),row=8-Number(square[1]);
 const box=await(await page.$('.chess-board')).boundingBox();
 await page.mouse.click(box.x+(col+.5)*box.width/8,box.y+(row+.5)*box.height/8);
};

try{
 await page.setViewport({width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_CHESS_MANIFEST||'.build/chess-study-test/apps.json','utf8'));
 const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_CHESS_URL||'http://127.0.0.1:18338/')+'?app='+encodeURIComponent(entry));
 await page.waitForSelector('.chess-board',{timeout:30000});
 await page.select('[aria-label="Study mode"]','exercise');
 await page.select('[aria-label="Exercise"]','back-rank-a');
 await click('New game');await click('Resume');await tapSquare('a1');await tapSquare('a8');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Exercise solved'));
 await page.evaluate(()=>{
  document.querySelector('.chess-save').open=true;
  document.querySelector('[aria-label="Chess save path"]').value='/Before.game.json';
  window.holdWrites=true;window.writeStarted=false;
 });
 await click('Save to My files');
 await page.waitForFunction(()=>window.writeStarted);
 assert.equal(await page.evaluate(()=>window.instances[0].w.chessStudy.dirty),true,'an in-flight save keeps the close guard active');
 await page.$eval('[aria-label="Chess save path"]',node=>{node.value='/After.game.json'});
 await page.evaluate(()=>window.releaseWrite());
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('syncing with the server'));
 assert.equal(await page.evaluate(()=>window.fileStore.has('/Before.game.json')),true);
 assert.equal(await page.evaluate(()=>window.fileStore.has('/After.game.json')),false);
 assert.equal(await page.$eval('[aria-label="Chess save path"]',node=>node.value),'/After.game.json');
 assert.equal(await page.evaluate(()=>window.instances[0].w.chessStudy.dirty),false);
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/Before.game.json').data)));
 assert.equal(saved.appId,'chess-study');
 assert.equal(saved.payload.result,'exercise-solved');
 await page.evaluate(()=>{
  window.instances[0].app.dispose();
  window.instances[0].app.dispose();
  window.instances[0].element.remove();
 });
 assert.equal(await page.$$('.chess-board').then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 console.log('PASS delayed write preserves captured chess destination and idempotent disposal');
}finally{
 await context.close();await browser.disconnect();
}
