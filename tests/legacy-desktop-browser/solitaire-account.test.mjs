import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18345/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'solitaire'+Date.now().toString().slice(-9);
const contexts=[],errors=[];

async function login(page,register,user=username){
 page.on('pageerror',error=>errors.push(error.message));
 page.on('dialog',dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{
  const original=window.fetch;
  window.fetch=(url,...args)=>String(url).endsWith('assets/terminal/v2/image.json')
   ?Promise.resolve(new Response('',{status:404}))
   :original(url,...args);
 });
 await page.goto(base);
 await page.waitForSelector('.login-toggle');
 if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);
 await page.type('[aria-label=Password]','test1234');
 if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}

async function launch(page){
 await page.evaluate(()=>surfaces.get('Desktop').launch('solitaire'));
 await page.waitForSelector('.solitaire-board',{timeout:30000});
}

const click=(page,label)=>page.evaluate(label=>document.querySelector(`.solitaire-view [aria-label="${label}"]`)?.click(),label);

try{
 const first=await browser.createBrowserContext();contexts.push(first);
 const page=await first.newPage();await page.setViewport({width:1366,height:900});
 await login(page,true);await launch(page);
 await click(page,'Start game');
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Playing'));
 await click(page,'Draw');await click(page,'Undo');
 await page.evaluate(()=>{document.querySelector('.solitaire-save').open=true;document.querySelector('[aria-label="Solitaire save path"]').value='/Solitaire.game.json'});
 await click(page,'Save to My files');
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('syncing with the server'),{timeout:30000});
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode(
  (await (await serverFileContext()).files.read('Solitaire.game.json')).data,
 )));
 assert.equal(saved.appId,'solitaire');
 assert.equal(saved.payload.paused,true);
 await page.evaluate(()=>document.querySelector('.solitaire-app').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.solitaire-app'));
 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Solitaire.game.json'));
 await page.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Game loaded and paused'),{timeout:30000});
 assert.equal(await page.$eval('[aria-label="Solitaire save path"]',input=>input.value),'/Solitaire.game.json');
 await page.evaluate(()=>document.querySelector('.solitaire-app').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.solitaire-app'));

 const fresh=await browser.createBrowserContext();contexts.push(fresh);
 const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.solitaire-save').open=true);
 await click(phone,'Open from My files');
 await phone.waitForSelector('[aria-label="Choose file Solitaire.game.json"]',{visible:true});
 await phone.click('[aria-label="Choose file Solitaire.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.solitaire-view .app-status')?.textContent.includes('Game loaded and paused'),{timeout:30000});
 assert.equal(await phone.$eval('[aria-label="Solitaire save path"]',input=>input.value),'/Solitaire.game.json');
 assert.match(await phone.$eval('.solitaire-view .app-status',node=>node.textContent),/paused/i);

 const isolation=await browser.createBrowserContext();contexts.push(isolation);
 const other=await isolation.newPage();await login(other,true,username+'b');
 assert.equal(await other.evaluate(async()=>{
  try{await(await mirrorFileContext()).files.read('/Solitaire.game.json');return true}catch{return false}
 }),false);
 await phone.evaluate(async()=>{
  const context=await mirrorFileContext(),file=await context.files.read('/Solitaire.game.json');
  await context.files.remove('/Solitaire.game.json',file.version);await context.files.sync();
 });
 assert.deepEqual(errors,[]);
 console.log('PASS real account save, sync, phone reload, paused restore and isolation');
}finally{
 for(const context of contexts)await context.close();
 await browser.disconnect();
}
