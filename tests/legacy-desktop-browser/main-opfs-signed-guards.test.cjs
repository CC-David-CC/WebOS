const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const puppeteer = require('puppeteer-core');
(async () => {
 const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP});
 const context=await browser.createBrowserContext();
 try {
  const page=await context.newPage(), id=crypto.randomBytes(8).toString('hex'), password=crypto.randomBytes(18).toString('base64url');
  await page.goto(process.env.CODI_TEST_URL,{waitUntil:'domcontentloaded'});await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]','guard'+id);await page.type('[aria-label=Password]',password);await page.type('[aria-label="Confirm password"]',password);await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:45000});
  const result=await page.evaluate(async()=>{
   let c=await (await fetch('/config.json')).json(), catalog=await (await fetch('/assets/desktop/apps.json')).json();
   const desktop=surfaces.get('Desktop');let launch=desktop.launch('chess-study');let rejected=false;try{desktop.open('chess-study',{})}catch{rejected=true}
   const m=(await mirrorFileContext()).files;let written=await m.write('/opfs-check.txt',new Blob(['opfs main fixture']));await m.sync();
   const db=await new Promise((resolve,reject)=>{const q=indexedDB.open('codi-mirrored-files-v1');q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)});
   const rows=await new Promise((resolve,reject)=>{let tx=db.transaction('files','readonly'),q=tx.objectStore('files').getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)});db.close();
   let row=rows.find(x=>x.path==='/opfs-check.txt');return {fileStorage:c.fileStorage,ids:catalog.apps.map(x=>x.id).sort(),launch:launch??null,rejected,kind:row?.data?.kind,revision:written.version};
  });
  assert.deepEqual(result.fileStorage,{version:'codi-browser-file-content/1',backend:'opfs',databaseVersion:2});assert.deepEqual(result.ids,['calculator','codemirror','files','help','terminal','text']);assert.equal(result.launch,null);assert.equal(result.rejected,true);assert.equal(result.kind,'codi-opfs-content/1');
  console.log('PASS actual configured issuer OPFS v2, stored content kind, restricted catalog and blocked launch/open',JSON.stringify(result));
 }finally{await context.close();browser.disconnect()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
