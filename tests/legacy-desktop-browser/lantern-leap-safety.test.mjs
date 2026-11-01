import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_LANTERN_URL||'http://127.0.0.1:18551/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19551'});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));

try{
  await page.setViewport({width:1366,height:900});
  const manifest=JSON.parse(await readFile(process.env.CODI_LANTERN_MANIFEST||'.build/lantern-leap-test/apps.json','utf8'));
  const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
  await page.goto(base+'?app='+encodeURIComponent(entry));
  await page.waitForFunction(()=>window.instances?.length===2);
  await page.waitForFunction(()=>document.querySelectorAll('.lantern-stage canvas').length===2,{timeout:30000});

  assert.equal(await page.$eval('.lantern-side details:not([open]) label',node=>getComputedStyle(node).display),'none');
  await page.evaluate(()=>{
    const view=document.querySelectorAll('.lantern-view')[0];
    view.querySelector('[aria-label=Resume]').click();
    view.querySelector('.lantern-stage').focus();
    view.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
  });
  await new Promise(resolve=>setTimeout(resolve,220));
  await page.evaluate(()=>window.instances[0].shell.classList.remove('focused'));
  await page.waitForFunction(()=>document.querySelectorAll('.lantern-status')[0].textContent.includes('lost attention'));
  await page.evaluate(()=>{
    window.instances[0].shell.classList.add('focused');
    document.querySelectorAll('.lantern-view')[0].querySelector('[aria-label=Resume]').click();
  });
  await page.waitForFunction(()=>document.querySelectorAll('.lantern-status')[0].textContent==='Lantern Leap running.');
  await page.evaluate(()=>{
    const instance=window.instances[0],view=document.querySelectorAll('.lantern-view')[0];
    view.querySelector('.lantern-save').open=true;
    view.querySelector('[aria-label="Lantern save path"]').value='/pending.game.json';
    window.delayWrites=true;
    view.querySelector('[aria-label="Save to My files"]').click();
  });
  await page.waitForFunction(()=>window.instances[0].windowState.dirty===true&&document.querySelectorAll('.lantern-view')[0].querySelector('[aria-label="Save to My files"]').disabled);
  await page.evaluate(()=>{
    const view=document.querySelectorAll('.lantern-view')[0];
    view.querySelector('[aria-label="Lantern save path"]').value='/later.game.json';
    window.delayWrites=false;
    window.releaseWrite();
  });
  await page.waitForFunction(()=>window.fileStore.has('/pending.game.json')&&!document.querySelectorAll('.lantern-view')[0].querySelector('[aria-label="Save to My files"]').disabled);
  assert.equal(await page.$eval('.lantern-view [aria-label="Lantern save path"]',node=>node.value),'/later.game.json');
  assert.equal(await page.evaluate(()=>window.fileStore.has('/later.game.json')),false);
  const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get('/pending.game.json').data)));
  assert.equal(saved.appId,'lantern-leap');
  assert.equal(saved.payload.levelId,0);

  await page.evaluate(()=>window.instances[0].app.dispose());
  assert.equal(await page.evaluate(()=>document.querySelectorAll('.lantern-stage canvas').length),1,'disposed window canvas must be removed');
  assert.deepEqual(errors,[]);
  console.log('PASS pending save close guard, destination snapshot, focus pause, disclosure hiding and disposal');
}finally{
  await context.close();
  await browser.disconnect();
}
