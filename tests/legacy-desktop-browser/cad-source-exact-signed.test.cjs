const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const puppeteer = require('puppeteer-core');
(async () => {
  const browser = await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:20085'});
  const contexts = [];
  try {
    const manifest = JSON.parse(fs.readFileSync(process.env.CODI_CAD_SOURCE_MANIFEST_FILE||'/var/lib/codi-cad-source-exact-test/manifest.json'));
    for (let i = 0; i < 2; i++) {
      const context = await browser.createBrowserContext(); contexts.push(context);
      const page = await context.newPage();
      await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:20080/', {waitUntil:'domcontentloaded'});
      const anonymous = await page.evaluate(async () => (await fetch('/gateway/use', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({resource:'cad-sources',operation:'cad-source',path:'JSKETCHER-LICENSE.txt'})})).status);
      assert.equal(anonymous,401);
      const user='cadexact'+crypto.randomBytes(8).toString('hex'), password=crypto.randomBytes(18).toString('base64url');
      await page.waitForSelector('.login-toggle'); await page.click('.login-toggle');
      await page.type('[aria-label=Username]',user); await page.type('[aria-label=Password]',password);
      await page.type('[aria-label="Confirm password"]',password); await page.click('.login-form button[type=submit]');
      await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:45000});
      for (const name of ['SOURCE-INDEX.html','JSKETCHER-LICENSE.txt','occt-worker-interpreter-source.zip']) {
        const result=await page.evaluate(async name=>{
          const r=await (await serverFileContext()).files.request('cad-source',{resource:'cad-sources',path:name},null,'blob');
          return {sha:r.sha256,size:r.data.size};
        },name);
        assert.deepEqual(result,{sha:manifest.files[name].sha256,size:manifest.files[name].bytes});
      }
    }
    console.log('PASS exact 67d inventory, two signed users: index, license and clean 8c source ZIP; anonymous 401');
  } finally { for(const c of contexts) await c.close(); browser.disconnect(); }
})().catch(e=>{console.error(e.stack);process.exitCode=1});
