import assert from "node:assert/strict";
import puppeteer from "puppeteer-core";

const base=process.env.CODI_TEST_URL||"http://127.0.0.1:18320/";
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19320",protocolTimeout:120000});
const username=process.env.CODI_TEST_USER||"golf"+Date.now().toString().slice(-8);
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
  await page.goto(base);
  await page.waitForSelector(".login-toggle");
  if(register)await page.click(".login-toggle");
  await page.type("[aria-label=Username]",user);
  await page.type("[aria-label=Password]","test1234");
  if(register)await page.type('[aria-label="Confirm password"]',"test1234");
  await page.click(".login-form button[type=submit]");
  await page.waitForFunction(()=>window.desktopLab?.session?.kind==="registered",{timeout:30000});
}

async function launch(page){
  await page.evaluate(()=>surfaces.get("Desktop").launch("pocket-golf"));
  await page.waitForSelector(".pocket-golf-stage canvas",{timeout:60000});
  await page.waitForFunction(()=>document.querySelector(".pocket-golf-status")?.textContent.includes("Press Start")||document.querySelector(".pocket-golf-status")?.textContent.includes("settled"),{timeout:60000});
}

const click=(page,label)=>page.evaluate(label=>{
  const button=[...document.querySelectorAll(".pocket-golf-view button")].find(node=>node.getAttribute("aria-label")===label||node.textContent===label);
  if(!button)throw Error("Missing button: "+label);
  button.click();
},label);

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const p=await context.newPage();await p.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(p,true,username+(phone?'b':'a'));await launch(p);
  await click(p,'Start / resume');await p.evaluate(()=>{const root=document.querySelector('.pocket-golf-view');[...root.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Putt'||b.textContent==='Putt').click();[...root.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Save to My files'||b.textContent==='Save to My files').click()});await p.waitForFunction(()=>document.querySelector('.pocket-golf-status')?.textContent.includes('last settled checkpoint'),{timeout:30000});await p.evaluate(async()=>await(await mirrorFileContext()).files.sync());const saved=await p.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Pocket Golf.game.json')).data)));assert.equal(saved.payload.strokes[0],0,'in-flight stroke is not in settled checkpoint');
  await p.evaluate(()=>document.querySelector('.pocket-golf-view').closest('.window').querySelector('[aria-label=Close]').click());await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('.codi-confirm-danger');await p.waitForFunction(()=>!document.querySelector('.pocket-golf-view'));await p.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Pocket Golf.game.json'));await p.waitForFunction(()=>document.querySelector('.pocket-golf-status')?.textContent.includes('Checkpoint loaded and paused'));assert.match(await p.$eval('.pocket-golf-view',e=>e.textContent),/0 strokes/);await click(p,'Reset lie (+1)');await p.select('[aria-label="Golf hole"]','1');await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('dialog.codi-confirm-dialog .codi-confirm-actions button:first-child');await p.waitForFunction(()=>document.querySelector('[aria-label="Golf hole"]').value==='0');assert.match(await p.$eval('.pocket-golf-view',e=>e.textContent),/1 strokes/);await p.select('[aria-label="Golf hole"]','1');await p.waitForSelector('dialog.codi-confirm-dialog[open]');await p.click('.codi-confirm-danger');await p.waitForFunction(()=>document.querySelector('[aria-label="Golf hole"]').value==='1');
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone in-flight save warns on close, reopens settled checkpoint, and confirms hole switch');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
