import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base=process.env.CODI_TEST_URL||'http://127.0.0.1:18338/';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19262',protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||'chess'+Date.now().toString().slice(-9);
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
 await page.goto(base);await page.waitForSelector('.login-toggle');
 if(register)await page.click('.login-toggle');
 await page.type('[aria-label=Username]',user);await page.type('[aria-label=Password]','test1234');
 if(register)await page.type('[aria-label="Confirm password"]','test1234');
 await page.click('.login-form button[type=submit]');
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
}
async function launch(page){
 await page.evaluate(()=>surfaces.get('Desktop').launch('chess-study'));
 await page.waitForSelector('.chess-board',{timeout:30000});
}
const click=(page,label)=>page.evaluate(label=>{
 const root=document.querySelector('.chess-study');
 const element=[...root.querySelectorAll('button')].find(node=>node.textContent===label);
 if(!element)throw Error('Missing button: '+label);
 element.click();
},label);
async function tapSquare(page,square){
 const file='abcdefgh'.indexOf(square[0]),row=8-Number(square[1]);
 const box=await(await page.$('.chess-board')).boundingBox();
 await page.touchscreen.tap(box.x+(file+.5)*box.width/8,box.y+(row+.5)*box.height/8);
}

try{
 const first=await browser.createBrowserContext();contexts.push(first);
 const page=await first.newPage();await page.setViewport({width:1366,height:900});
 await login(page,true);await launch(page);
 await page.select('[aria-label="Study mode"]','exercise');
 await page.select('[aria-label="Exercise"]','back-rank-a');
 await click(page,'New game');await click(page,'Resume');
 await tapSquare(page,'a1');await tapSquare(page,'a8');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Exercise solved'));
 await page.evaluate(()=>{document.querySelector('.chess-save').open=true;document.querySelector('[aria-label="Chess save path"]').value='/Chess Study.game.json'});
 await click(page,'Save to My files');
 await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('syncing with the server'),{timeout:30000});
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode(
  (await (await serverFileContext()).files.read('Chess Study.game.json')).data,
 )));
 assert.equal(saved.appId,'chess-study');assert.equal(saved.payload.result,'exercise-solved');assert.equal(saved.payload.history.length,1);
 await page.evaluate(()=>document.querySelector('.chess-study').closest('.window').querySelector('[aria-label=Close]').click());
 await page.waitForFunction(()=>!document.querySelector('.chess-study'));

 if(process.env.CODI_TEST_FILES_ROUTE!=='0'){
  await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Chess Study.game.json'));
  await page.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Study loaded and paused'),{timeout:30000});
  assert.equal(await page.$eval('[aria-label="Chess save path"]',node=>node.value),'/Chess Study.game.json');
  await page.evaluate(()=>document.querySelector('.chess-study').closest('.window').querySelector('[aria-label=Close]').click());
  await page.waitForFunction(()=>!document.querySelector('.chess-study'));
 }

 const fresh=await browser.createBrowserContext();contexts.push(fresh);
 const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector('.chess-save').open=true);
 await click(phone,'Open from My files');
 await phone.waitForSelector('[aria-label="Choose file Chess Study.game.json"]',{visible:true});
 await phone.click('[aria-label="Choose file Chess Study.game.json"]');
 await phone.waitForFunction(()=>document.querySelector('.chess-status')?.textContent.includes('Study loaded and paused'),{timeout:30000});
 assert.equal(await phone.$eval('[aria-label="Chess save path"]',node=>node.value),'/Chess Study.game.json');

 const isolation=await browser.createBrowserContext();contexts.push(isolation);
 const other=await isolation.newPage();await login(other,true,username+'b');
 assert.equal(await other.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Chess Study.game.json');return true}catch{return false}}),false);
 await phone.evaluate(async()=>{const context=await mirrorFileContext(),file=await context.files.read('/Chess Study.game.json');await context.files.remove('/Chess Study.game.json',file.version);await context.files.sync()});
 assert.deepEqual(errors,[]);
 console.log('PASS real account save, sync, optional Files route, phone reload, paused restore and isolation');
}finally{
 for(const context of contexts)await context.close();
 await browser.disconnect();
}
