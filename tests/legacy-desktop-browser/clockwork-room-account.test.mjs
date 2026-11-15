import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18344/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19282',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'clockwork'+Date.now().toString().slice(-8);
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
 await page.evaluate(()=>surfaces.get('Desktop').launch('clockwork-room'));
 await page.waitForSelector('.clockwork-stage-wrap canvas',{timeout:30000});
 await page.waitForFunction(()=>!document.querySelector('.clockwork-loading'),{timeout:30000});
}

const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll('.clockwork-view button')]
  .find(node=>node.getAttribute('aria-label')===label||node.textContent===label);
 if(!button)throw Error('Missing button: '+label);
 button.click();
},label);

try{
 const first=await browser.createBrowserContext();contexts.push(first);
 const page=await first.newPage();debugPage=page;await page.setViewport({width:1366,height:900});
 await login(page,true);await launch(page);
 await page.click('.clockwork-toolbar [aria-label=Run]');
 for(const label of ['Use Gear alignment','Use Chime sequence','Use Pendulum brake','Use Exit lock'])await click(page,label);
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('exit is open'));
 await page.evaluate(()=>document.querySelector('.clockwork-save').open=true);
 await page.$eval('[aria-label="Clockwork room save path"]',node=>node.value='/Clockwork Room.game.json');
 await click(page,'Save');
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room saved to My files'));
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode(
  (await (await serverFileContext()).files.read('Clockwork Room.game.json')).data,
 )));
 assert.equal(saved.appId,'clockwork-room');
 assert.deepEqual(saved.payload.solved,[true,true,true,true]);
 await page.evaluate(()=>document.querySelector('.clockwork-view').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.clockwork-view'));

 await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Clockwork Room.game.json'));
 await page.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room loaded and paused'),{timeout:30000});
 assert.equal(await page.$eval('[aria-label="Clockwork room save path"]',node=>node.value),'/Clockwork Room.game.json');
 await page.evaluate(()=>document.querySelector('.clockwork-view').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.clockwork-view'));

 const fresh=await browser.createBrowserContext();contexts.push(fresh);
 const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.clockwork-save').open=true);
 await click(phone,'Open');
 await phone.waitForSelector('[aria-label="Choose file Clockwork Room.game.json"]',{visible:true});
 await phone.click('[aria-label="Choose file Clockwork Room.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.clockwork-status')?.textContent.includes('Room loaded and paused'));
 assert.equal(await phone.$eval('[aria-label="Clockwork room save path"]',node=>node.value),'/Clockwork Room.game.json');
 assert.deepEqual(await phone.$$eval('.clockwork-objectives li',rows=>rows.map(row=>row.dataset.solved)),['true','true','true','true']);

 const isolation=await browser.createBrowserContext();contexts.push(isolation);
 const other=await isolation.newPage();await login(other,true,username+'b');
 assert.equal(await other.evaluate(async()=>{
  try{await(await mirrorFileContext()).files.read('/Clockwork Room.game.json');return true}catch{return false}
 }),false);
 await phone.evaluate(async()=>{
  const context=await mirrorFileContext(),file=await context.files.read('/Clockwork Room.game.json');
  await context.files.remove('/Clockwork Room.game.json',file.version);await context.files.sync();
 });
 assert.deepEqual(errors,[]);
 console.log('PASS real account save, sync, Files route, phone reload, paused restore and isolation');
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
