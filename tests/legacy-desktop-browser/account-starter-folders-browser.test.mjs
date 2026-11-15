import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'});
const context=await browser.createBrowserContext(),page=await context.newPage(),user='folders'+Date.now().toString().slice(-9),base=process.env.CODI_TEST_URL||'http://127.0.0.1:18286/';
const expected=['3D Objects','Audio','Digital Projects','Documents','Games','Pictures','Video'];
try{
 if(process.env.CODI_PHONE==='1')await page.setViewport({width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2});
 await page.goto(base);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const entries=await page.evaluate(async()=>(await(await mirrorFileContext()).files.list('/')).entries);
 assert.deepEqual(entries.map(e=>e.name).sort(),expected);assert.ok(entries.every(e=>e.directory&&e.status==='synced'));
 await page.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/Digital Projects/test.txt','saved',null);await f.sync()});
 assert.equal(await page.evaluate(async()=>new TextDecoder().decode((await(await serverFileContext()).files.read('Digital Projects/test.txt')).data)),'saved');
 const another=await browser.createBrowserContext();try{const p=await another.newPage();await p.goto(base);await p.waitForSelector('.login-toggle');await p.type('[aria-label=Username]',user);await p.type('[aria-label=Password]','test1234');await p.click('.login-form button[type=submit]');await p.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());assert.equal(await p.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/Digital Projects/test.txt')).data)),'saved');}finally{await another.close()}
 if(process.env.CODI_CLEANUP==='1'){
  const subject=await page.evaluate(()=>signedInSubject());
  await page.evaluate(async()=>{const f=(await mirrorFileContext()).files, item=await f.stat('/Digital Projects/test.txt');await f.remove('/Digital Projects/test.txt',item.version);await f.sync();for(const dir of (await f.list('/')).entries){await f.remove(dir.path,dir.version);await f.sync()} });
  console.log('TEST ACCOUNT',user,subject);
 }
 console.log('PASS starter folders sync and reopen in a fresh browser session');
}finally{await context.close();await browser.disconnect()}
