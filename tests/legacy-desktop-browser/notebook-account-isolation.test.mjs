import puppeteer from 'puppeteer-core';
import assert from 'node:assert/strict';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18143/';
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255',protocolTimeout:180000});
const context=await browser.createBrowserContext();let page=await context.newPage();
const suffix=Date.now().toString(36),users=['notebooka'+suffix,'notebookb'+suffix];
async function register(user){
  await page.waitForSelector('.login-toggle');await page.click('.login-toggle');
  await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');
  await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:45000});
  console.log('Signed in:',user);
}
async function notebook(){
  await page.evaluate(()=>[...surfaces.values()][0].launch('notebook'));
  await page.waitForFunction(()=>document.querySelector('.notebook-app .app-status')?.textContent.includes('Browser Python notebook ready'),{timeout:120000});
  console.log('Notebook ready');
  return page.evaluate(async()=>{
    const frame=document.querySelector('.notebook-app iframe'),app=frame.contentWindow.jupyterapp;
    const listing=await Promise.race([app.serviceManager.contents.get('',{content:true}),new Promise((_,reject)=>setTimeout(()=>reject(Error('Notebook contents listing timed out')),15000))]);
    return {owner:new URL(frame.src).searchParams.get('codi_owner'),path:app.shell.currentWidget.context.path,files:listing.content.map(f=>f.name)};
  });
}
try {
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(base);await register(users[0]);const first=await notebook();
  assert.match(first.path,/^codi-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\.ipynb$/);
  await page.evaluate(async()=>{const c=await mirrorFileContext();await c.files.write('/private-check.txt','only account A');await c.files.sync();});
  console.log('Account A file saved');
  page=await context.newPage();
  await page.evaluateOnNewDocument(()=>{const f=window.fetch;window.fetch=(u,...a)=>String(u).endsWith('assets/terminal/v2/image.json')?Promise.resolve(new Response('',{status:404})):f(u,...a)});
  await page.goto(base);await register(users[1]);
  const second=await notebook();assert.notEqual(first.owner,second.owner);assert.notEqual(first.path,second.path);
  assert(!second.files.includes(first.path),'Second account sees the first account notebook in JupyterLite');
  const privateFile=await page.evaluate(async()=>{try{return !!(await(await mirrorFileContext()).files.read('/private-check.txt'));}catch{return false;}});
  assert.equal(privateFile,false,'Second account can read the first account file');
  page.on('dialog',dialog=>dialog.accept());
  await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:45000}),page.evaluate(()=>{void endSession();})]);
  await page.waitForSelector('.login-form');await page.type('[aria-label=Username]',users[0]);await page.type('[aria-label=Password]','test1234');
  await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:45000});
  const switched=await notebook();assert.equal(switched.owner,first.owner);assert(!switched.files.includes(second.path));
  const saved=await page.evaluate(async()=>new TextDecoder().decode((await(await mirrorFileContext()).files.read('/private-check.txt')).data));
  assert.equal(saved,'only account A');
  console.log('PASS same browser: simultaneous and switched accounts, per-account notebook storage, random names, and separate My files');
} finally {await context.close();await browser.disconnect();}
