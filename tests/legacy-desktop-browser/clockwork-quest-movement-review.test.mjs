import assert from "node:assert/strict";
import puppeteer from "puppeteer-core";

const base=process.env.CODI_TEST_URL||"http://127.0.0.1:18976/";
const browser=await puppeteer.connect({
  browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19255",
  protocolTimeout:120000,
});
const username=process.env.CODI_TEST_USER||"quest"+Date.now().toString().slice(-9);
const contexts=[],errors=[];
let debugPage;

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
  await page.evaluate(()=>surfaces.get("Desktop").launch("clockwork-quest"));
  await page.waitForSelector(".clockwork-quest-stage canvas",{timeout:60000});
}

const click=(page,label)=>page.evaluate(label=>{
  const button=[...document.querySelectorAll(".clockwork-quest-view button")]
    .find(node=>node.getAttribute("aria-label")===label||node.textContent===label);
  if(!button)throw Error("Missing button: "+label);
  button.click();
},label);

async function interact(page,id){
  await page.select(".clockwork-quest-view [aria-label=Interaction]",id);
  await click(page,"Interact");
}

async function solve(page){
  await click(page,"Run");
  await click(page,"Move to Workbench");
  await interact(page,"inspect-gear");
  await interact(page,"turn-crank");
  await page.focus(".clockwork-quest-stage canvas");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowUp");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Clock Hall"));
  await page.keyboard.press("d");
  await interact(page,"set-minute");
  await interact(page,"set-hour");
  await interact(page,"take-mainspring");
  await page.focus(".clockwork-quest-stage canvas");
  await page.keyboard.press("w");
  await page.keyboard.press("w");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Conservatory"));
  await page.keyboard.press("d");
  await interact(page,"unlock-cage");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Adventure complete"));
}

try{
  const first=await browser.createBrowserContext();
  contexts.push(first);
  const page=await first.newPage();
  debugPage=page;
  await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
  await login(page,true);
  await launch(page);
  await click(page,"Run");
  await page.focus(".clockwork-quest-stage canvas");
  await page.keyboard.press("ArrowUp");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Workbench"));
  assert.equal(await page.evaluate(()=>surfaces.get("Desktop").windows.find(w=>w.app==="clockwork-quest").clockworkQuest.dirty),true);
  await page.evaluate(()=>document.querySelector(".clockwork-quest-view").closest(".window").querySelector("[aria-label=Close]").click());
  await page.waitForSelector("dialog.codi-confirm-dialog[open]");
  await page.evaluate(()=>document.querySelector(".codi-confirm-actions button:first-child").click());
  assert.ok(await page.$(".clockwork-quest-view"));
  await page.focus(".clockwork-quest-stage canvas");
  await page.keyboard.press("ArrowDown");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Entrance"));
  await page.keyboard.press("d");await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Workbench"));
  await page.keyboard.press("d");await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Clock door"));
  await page.keyboard.press("a");await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Workbench"));
  await page.keyboard.press("s");await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Entrance"));
  await click(page,"Pause");
  await click(page,"Restart");
  await page.waitForSelector("dialog.codi-confirm-dialog[open]");
  await page.evaluate(()=>document.querySelector(".codi-confirm-danger").click());
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("Adventure reset"));
  await solve(page);
  await page.evaluate(()=>document.querySelector(".clockwork-quest-save").open=true);
  await page.$eval("[aria-label='Clockwork Quest save path']",node=>node.value="/Clockwork Quest.game.json");
  await click(page,"Save to My files");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("syncing with the server"),{timeout:30000});
  await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());
  const saved=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode(
    (await(await serverFileContext()).files.read("Clockwork Quest.game.json")).data,
  )));
  assert.equal(saved.appId,"clockwork-quest");
  assert.equal(saved.payload.dialogue,"rescue");
  assert.equal(saved.payload.flags.companionFreed,true);

  await page.evaluate(()=>document.querySelector(".clockwork-quest-view").closest(".window").querySelector("[aria-label=Close]").click());
  await page.waitForFunction(()=>!document.querySelector(".clockwork-quest-view"));
  await page.evaluate(()=>openMirrorDocument(surfaces.get("Desktop"),signedInSubject(),"/Clockwork Quest.game.json"));
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("loaded and paused"),{timeout:30000});
  assert.equal(await page.$eval(".clockwork-quest-room-title",node=>node.textContent), "Adventure complete · Pip rescued");
  await page.evaluate(()=>document.querySelector(".clockwork-quest-view").closest(".window").querySelector("[aria-label=Close]").click());
  await page.waitForFunction(()=>!document.querySelector(".clockwork-quest-view"));

  const fresh=await browser.createBrowserContext();
  contexts.push(fresh);
  const phone=await fresh.newPage();
  await phone.setViewport({width:412,height:915,isMobile:true,hasTouch:true});
  await login(phone,false);
  await phone.evaluate(async()=>await(await mirrorFileContext()).files.sync());
  await launch(phone);
  await phone.evaluate(()=>document.querySelector(".clockwork-quest-save").open=true);
  await click(phone,"Open from My files");
  await phone.waitForSelector("[aria-label='Choose file Clockwork Quest.game.json']",{visible:true});
  await phone.click("[aria-label='Choose file Clockwork Quest.game.json']");
  await phone.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("loaded and paused"),{timeout:30000});
  assert.equal(await phone.$eval(".clockwork-quest-room-title",node=>node.textContent), "Adventure complete · Pip rescued");

  const isolation=await browser.createBrowserContext();
  contexts.push(isolation);
  const other=await isolation.newPage();
  await login(other,true,username+"b");
  assert.equal(await other.evaluate(async()=>{
    try {await(await mirrorFileContext()).files.read("/Clockwork Quest.game.json");return true} catch {return false}
  }),false);
  if(process.env.CODI_CLEANUP==="1")await phone.evaluate(async()=>{
    const context=await mirrorFileContext(),file=await context.files.read("/Clockwork Quest.game.json");
    await context.files.remove("/Clockwork Quest.game.json",file.version);
    await context.files.sync();
  });
  assert.deepEqual(errors,[]);
  console.log("PASS movement dirty guard, keyboard navigation, complete quest, sync and fresh phone reopen/isolation");
}catch(error){
  console.error("Diagnostics:",await debugPage?.evaluate(()=>({
    body:document.body.innerText.slice(0,1600),
    windows:[...document.querySelectorAll(".window")].map(node=>node.innerText.slice(0,220)),
  })).catch(()=>null));
  throw error;
}finally{
  for(const context of contexts)await context.close();
  await browser.disconnect();
}
