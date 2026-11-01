import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser=await puppeteer.connect({
  browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',
  protocolTimeout:120000,
});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));

try {
  await page.setViewport({width:1366,height:900});
  const manifest=JSON.parse(await readFile(process.env.CODI_STACK_MANIFEST||'.build/stack-balance/apps.json','utf8'));
  const entry='/'+manifest.apps[0].path.replace(/^assets\/desktop\//,'');
  await page.goto((process.env.CODI_STACK_URL||'http://127.0.0.1:18345/')+'?app='+encodeURIComponent(entry));
  await page.waitForSelector('.stack-stage canvas',{timeout:60000});
  await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('build'));
  const click=label=>page.evaluate(label=>{
    const button=[...document.querySelectorAll('.stack-view button')]
      .find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
    if(!button)throw Error('Missing button: '+label);
    button.click();
  },label);
  await click('Run');
  for(let i=0;i<4;i++)await click('Release block');
  await page.waitForFunction(()=>document.querySelector('.stack-info')?.textContent.includes('won'),{timeout:10000});
  await page.evaluate(()=>{
    document.querySelector('.stack-save').open=true;
    document.querySelector('[aria-label="Stack save path"]').value='/Before.game.json';
    const files=window.test.files;
    const write=files.write.bind(files);
    window.releaseStackWrite=null;
    files.write=async(...args)=>{
      await new Promise(resolve=>{window.releaseStackWrite=resolve});
      files.write=write;
      return write(...args);
    };
  });
  await click('Save to My files');
  await page.waitForFunction(()=>typeof window.releaseStackWrite==='function');
  assert.equal(await page.evaluate(()=>window.test.host.w.stackBalance.dirty),true,'in-flight save keeps the close guard active');
  await page.$eval('[aria-label="Stack save path"]',node=>{node.value='/After.game.json'});
  await page.evaluate(()=>window.releaseStackWrite());
  await page.waitForFunction(()=>document.querySelector('.stack-view .app-status')?.textContent.includes('syncing with the server'));
  assert.equal(await page.evaluate(()=>window.test.store.has('/Before.game.json')),true);
  assert.equal(await page.evaluate(()=>window.test.store.has('/After.game.json')),false);
  assert.equal(await page.$eval('[aria-label="Stack save path"]',node=>node.value),'/After.game.json');
  assert.equal(await page.evaluate(()=>window.test.host.w.stackBalance.dirty),false);
  const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.test.store.get('/Before.game.json').data)));
  assert.equal(saved.appId,'stack-balance');
  assert.equal(saved.payload.phase,'won');
  await page.evaluate(()=>{
    window.test.dispose();
    window.test.dispose();
  });
  assert.deepEqual(errors,[]);
  console.log('PASS delayed save keeps captured destination and pending-close guard');
} finally {
  await context.close();
  await browser.disconnect();
}
