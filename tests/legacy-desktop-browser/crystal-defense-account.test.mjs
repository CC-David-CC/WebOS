import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18348/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'crystal'+Date.now().toString().slice(-9);
const contexts=[],errors=[];let debugPage;

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
 await page.evaluate(()=>surfaces.get('Desktop').launch('crystal-defense'));
 await page.waitForSelector('.crystal-stage canvas',{timeout:60000});
 await page.waitForFunction(()=>document.querySelector('.crystal-view .crystal-note')?.textContent.includes('Wave 0/8'));
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.crystal-view button')]
  .find(node=>node.textContent===label||node.getAttribute('aria-label')===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 const first=await browser.createBrowserContext();contexts.push(first);
 const page=await first.newPage();debugPage=page;await page.setViewport({width:1366,height:900});
 await login(page,true);await launch(page);
 await click(page,'Socket 3');await click(page,'Build Spark');await click(page,'Resume');
 await page.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('Wave 1 started'),{timeout:30000});
 await page.waitForFunction(()=>document.querySelector('.crystal-view .crystal-note')?.textContent.includes('Wave 1/8'));
 await page.evaluate(()=>document.querySelector('.crystal-save').open=true);
 await page.$eval('[aria-label="Crystal Defense save path"]',input=>input.value='/Crystal Defense.game.json');
 await click(page,'Save to My files');
 await page.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('syncing with the server'),{timeout:30000});
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode(
  (await (await serverFileContext()).files.read('Crystal Defense.game.json')).data,
 )));
 assert.equal(saved.appId,'crystal-defense');
 assert.ok(saved.payload.towers.some(tower=>tower.role==='spark'));
 await page.evaluate(()=>document.querySelector('.crystal-view').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.crystal-view'));

 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Crystal Defense.game.json'));
 await page.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('Defense loaded and paused'),{timeout:30000});
 assert.equal(await page.$eval('[aria-label="Crystal Defense save path"]',input=>input.value),'/Crystal Defense.game.json');
 await page.evaluate(()=>document.querySelector('.crystal-view').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.crystal-view'));

 const fresh=await browser.createBrowserContext();contexts.push(fresh);
 const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.crystal-save').open=true);
 await click(phone,'Open from My files');
 await phone.waitForSelector('[aria-label="Choose file Crystal Defense.game.json"]',{visible:true});
 await phone.click('[aria-label="Choose file Crystal Defense.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.crystal-view .app-status')?.textContent.includes('Defense loaded and paused'),{timeout:30000});
 assert.match(await phone.$eval('.crystal-view .crystal-note',node=>node.textContent),/Wave 1\/8/);

 const isolation=await browser.createBrowserContext();contexts.push(isolation);
 const other=await isolation.newPage();await login(other,true,username+'b');
 assert.equal(await other.evaluate(async()=>{
  try{await(await mirrorFileContext()).files.read('/Crystal Defense.game.json');return true}catch{return false}
 }),false);

 await phone.evaluate(async()=>{
  const context=await mirrorFileContext(),file=await context.files.read('/Crystal Defense.game.json');
  await context.files.remove('/Crystal Defense.game.json',file.version);await context.files.sync();
 });
 assert.deepEqual(errors,[]);
 console.log('PASS real account save, sync, Files route, phone reload, paused restore and account isolation');
}catch(error){
 console.error('Diagnostics:',await debugPage?.evaluate(()=>({
  body:document.body.innerText.slice(0,1200),
  windows:[...document.querySelectorAll('.window')].map(node=>node.innerText.slice(0,180)),
 })).catch(()=>null));
 throw error;
}finally{
 for(const context of contexts)await context.close();
 await browser.disconnect();
}
