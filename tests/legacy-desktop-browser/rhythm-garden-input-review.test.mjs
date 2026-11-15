import assert from "node:assert/strict";
import puppeteer from "puppeteer-core";

const base=process.env.CODI_TEST_URL||"http://127.0.0.1:18345/";
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19262",protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||"rhythm"+Date.now().toString().slice(-9);
const contexts=[],errors=[];

async function login(page,register,user=username){
 page.on("pageerror",error=>errors.push(error.message));
 page.on("dialog",dialog=>dialog.accept());
 await page.evaluateOnNewDocument(()=>{
  const original=window.fetch;
  window.fetch=(url,...args)=>String(url).endsWith("assets/terminal/v2/image.json")
   ?Promise.resolve(new Response("",{status:404}))
   :original(url,...args);
 });
 await page.goto(base);await page.waitForSelector(".login-toggle");
 if(register)await page.click(".login-toggle");
 await page.type("[aria-label=Username]",user);await page.type("[aria-label=Password]","test1234");
 if(register)await page.type('[aria-label="Confirm password"]',"test1234");
 await page.click(".login-form button[type=submit]");
 await page.waitForFunction(()=>window.desktopLab?.session?.kind==="registered",{timeout:30000});
}
async function launch(page){
 await page.evaluate(()=>surfaces.get("Desktop").launch("rhythm-garden"));
 await page.waitForSelector(".rhythm-stage canvas",{timeout:30000});
}
const click=(page,label)=>page.evaluate(label=>{
 const button=[...document.querySelectorAll(".rhythm-view button")].find(node=>node.getAttribute("aria-label")===label||node.textContent===label);
 if(!button)throw Error("Missing button: "+label);button.click();
},label);

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900,hasTouch:true});await login(p,true,username+(phone?'b':'a'));await launch(p);await click(p,'Resume');
  const count=await p.evaluate(()=>{const status=document.querySelector('.rhythm-status'),observer=new MutationObserver(()=>{});observer.observe(status,{childList:true,subtree:true,characterData:true});document.querySelector('.rhythm-pads button').click();const n=observer.takeRecords().length;observer.disconnect();return n});assert.equal(count,1,'keyboard/accessibility click judges exactly once');
  const repeat=await p.evaluate(()=>{const el=document.querySelector('.rhythm-view'),status=document.querySelector('.rhythm-status'),observer=new MutationObserver(()=>{});observer.observe(status,{childList:true,subtree:true,characterData:true});el.dispatchEvent(new KeyboardEvent('keydown',{key:'d',bubbles:true,cancelable:true,repeat:true}));el.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true,repeat:true}));const n=observer.takeRecords().length;observer.disconnect();return n});assert.equal(repeat,0,'held-key repeats do not judge or pause');assert.ok(await p.$('.rhythm-view [aria-label=Pause]'));
  const pad=await p.$('.rhythm-pads button');await pad.evaluate(e=>e.scrollIntoView({block:'center'}));const box=await pad.boundingBox(),point={x:box.x+box.width/2,y:box.y+box.height/2,id:1},cdp=await p.createCDPSession();await p.evaluate(()=>{window.rhythmMutations=0;const status=document.querySelector('.rhythm-status');window.rhythmObserver=new MutationObserver(records=>window.rhythmMutations+=records.length);window.rhythmObserver.observe(status,{childList:true,subtree:true,characterData:true})});await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});const touchCount=await p.evaluate(()=>{window.rhythmObserver.disconnect();return window.rhythmMutations});assert.equal(touchCount,1,'a touch judges exactly once');
  await click(p,'Pause');await p.evaluate(()=>document.querySelector('.rhythm-save').open=true);await click(p,'Save to My files');await p.waitForFunction(()=>document.querySelector('.rhythm-status')?.textContent.includes('syncing with the server'));await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Rhythm Garden.game.json')).data)));assert.equal(saved.appId,'rhythm-garden');
  await p.evaluate(()=>document.querySelector('.rhythm-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForFunction(()=>!document.querySelector('.rhythm-view'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Rhythm Garden.game.json'));await p.waitForFunction(()=>document.querySelector('.rhythm-status')?.textContent.includes('Checkpoint loaded'));assert.ok(await p.$('.rhythm-view [aria-label=Resume]'));
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone single activation, repeat guard and account save/sync/reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
