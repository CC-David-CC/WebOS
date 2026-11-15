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
 const first=await browser.createBrowserContext();contexts.push(first);
 const page=await first.newPage();await page.setViewport({width:1366,height:900});
 await login(page,true);await launch(page);
 await click(page,"Resume");await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Phrase 1 started"));
 await new Promise(resolve=>setTimeout(resolve,480));
 const lane=await page.$eval(".rhythm-note-list",node=>Number(node.textContent.match(/0\.50s\s+lane ([1-4])/)?.[1]||1));
 await page.click(`.rhythm-pads button:nth-child(${lane})`);
 await click(page,"Pause");
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Phrase 1 complete"));
 await page.evaluate(()=>document.querySelector(".rhythm-save").open=true);
 await page.$eval('[aria-label="Rhythm save path"]',node=>node.value="/Rhythm Garden.game.json");
 await click(page,"Save to My files");
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("syncing with the server"));
 await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
 const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read("Rhythm Garden.game.json")).data)));
 assert.equal(saved.appId,"rhythm-garden");
 assert.ok(saved.payload.score>0);
 await page.evaluate(()=>document.querySelector(".rhythm-view").closest(".window").querySelector("[aria-label=Close]").click());
 await page.waitForFunction(()=>!document.querySelector(".rhythm-view"));

 await page.evaluate(()=>openMirrorDocument(surfaces.get("Desktop"),signedInSubject(),"/Rhythm Garden.game.json"));
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Checkpoint loaded at its phrase boundary"));
 assert.equal(await page.$eval('[aria-label="Rhythm save path"]',node=>node.value),"/Rhythm Garden.game.json");
 await page.evaluate(()=>document.querySelector(".rhythm-view").closest(".window").querySelector("[aria-label=Close]").click());
 await page.waitForFunction(()=>!document.querySelector(".rhythm-view"));

 const fresh=await browser.createBrowserContext();contexts.push(fresh);
 const phone=await fresh.newPage();await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
 await login(phone,false);await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());await launch(phone);
 await phone.evaluate(()=>document.querySelector(".rhythm-save").open=true);await click(phone,"Open from My files");
 await phone.waitForSelector('[aria-label="Choose file Rhythm Garden.game.json"]',{visible:true});
 await phone.click('[aria-label="Choose file Rhythm Garden.game.json"]');
 await phone.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Checkpoint loaded at its phrase boundary"));
 assert.equal(await phone.$eval('[aria-label="Rhythm save path"]',node=>node.value),"/Rhythm Garden.game.json");

 const isolation=await browser.createBrowserContext();contexts.push(isolation);
 const other=await isolation.newPage();await login(other,true,username+"b");
 assert.equal(await other.evaluate(async()=>{
  try{await(await mirrorFileContext()).files.read("/Rhythm Garden.game.json");return true}catch{return false}
 }),false);
 await phone.evaluate(async()=>{
  const context=await mirrorFileContext(),file=await context.files.read("/Rhythm Garden.game.json");
  await context.files.remove("/Rhythm Garden.game.json",file.version);await context.files.sync();
 });
 assert.deepEqual(errors,[]);
 console.log("PASS real account phrase save, sync, Files route, phone reload, paused restore and isolation");
}finally{
 for(const context of contexts)await context.close();
 await browser.disconnect();
}
