import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser=await puppeteer.connect({
  browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19262",
  protocolTimeout:120000,
});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const errors=[],external=[];
const base=process.env.CODI_CLOCKWORK_QUEST_URL||"http://127.0.0.1:18364/";
page.on("pageerror",error=>errors.push(error.message));
page.on("dialog",dialog=>dialog.accept());
page.on("request",request=>{
  if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==new URL(base).origin)external.push(request.url());
});

const click=label=>page.evaluate(label=>{
  const first=document.querySelectorAll(".clockwork-quest-view")[0];
  const button=[...first.querySelectorAll("button")].find(node=>node.getAttribute("aria-label")===label||node.textContent===label);
  if(!button)throw Error("Missing button: "+label);
  button.click();
},label);

async function useInteraction(id){
  await page.select(".clockwork-quest-view [aria-label=Interaction]",id);
  await click("Interact");
}

try{
  await page.setViewport(process.env.CODI_PHONE
    ?{width:412,height:915,isMobile:true,hasTouch:true}
    :{width:1366,height:900});
  const manifest=JSON.parse(await readFile(
    process.env.CODI_CLOCKWORK_QUEST_MANIFEST||".build/clockwork-quest-test/apps.json",
    "utf8",
  ));
  const entry="/"+manifest.apps[0].path.replace(/^assets\/desktop\//,"");
  await page.goto(base+"?app="+encodeURIComponent(entry));
  await page.waitForFunction(()=>window.instances?.length===2);
  await page.waitForFunction(()=>document.querySelectorAll(".clockwork-quest-stage canvas").length===2,{timeout:30000});
  assert.equal(await page.$$eval(".clockwork-quest-view",nodes=>nodes.length),2);
  assert.match(await page.$eval(".clockwork-quest-note",node=>node.textContent),/glTF.*quest-faces\.riv.*pending/);
  assert.match(await page.$eval(".clockwork-quest-status",node=>node.textContent),/Press Run/);
  assert.deepEqual(await page.evaluate(()=>{
    const view=document.querySelector(".clockwork-quest-view");
    const viewport=view.getBoundingClientRect();
    const visible=[...view.querySelectorAll("button,select,input")].filter(node=>{
      if(node.closest("details:not([open])"))return false;
      const rect=node.getBoundingClientRect();
      return rect.bottom>viewport.top&&rect.top<viewport.bottom&&rect.right>viewport.left&&rect.left<viewport.right;
    });
    const covered=visible.filter(node=>{
      const rect=node.getBoundingClientRect();
      if(!rect.width||!rect.height)return false;
      const top=document.elementFromPoint(rect.left+rect.width/2,rect.top+rect.height/2);
      return top!==node&&!node.contains(top);
    }).map(node=>node.getAttribute("aria-label")||node.textContent);
    return {
      covered,
      overflow:document.documentElement.scrollWidth>innerWidth,
      minHeight:Math.min(...visible.filter(node=>node.getBoundingClientRect().height).map(node=>node.getBoundingClientRect().height)),
    };
  }), {covered:[],overflow:false,minHeight:process.env.CODI_PHONE?44:40});

  await click("Run");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("Adventure running"));
  await click("Move to Workbench");
  await useInteraction("inspect-gear");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-inventory")?.textContent.includes("brass-key"));
  await useInteraction("turn-crank");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("clock hall"));
  await click("Move to Clock door");
  await click("Move to Enter Clock Hall");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Clock Hall"));
  await click("Move to Hand controls");
  await useInteraction("set-minute");
  await useInteraction("set-hour");
  await useInteraction("take-mainspring");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-inventory")?.textContent.includes("mainspring"));
  await click("Move to Conservatory door");
  await click("Move to Enter Conservatory");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Conservatory"));
  await click("Move to Rescue cage");
  await useInteraction("unlock-cage");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-room-title")?.textContent.includes("Adventure complete"));
  assert.equal(await page.$eval(".clockwork-quest-face",node=>node.dataset.state),"cheer");

  await page.evaluate(()=>document.querySelector(".clockwork-quest-save").open=true);
  await page.$eval("[aria-label='Clockwork Quest save path']",node=>node.value="/Clockwork Quest.game.json");
  await click("Save to My files");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("syncing with the server"));
  const saved=JSON.parse(await page.evaluate(()=>new TextDecoder().decode(window.fileStore.get("/Clockwork Quest.game.json").data)));
  assert.equal(saved.appId,"clockwork-quest");
  assert.equal(saved.payload.flags.companionFreed,true);
  assert.equal(saved.payload.interactions.length,6);

  await click("Restart");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("Adventure reset"));
  await page.evaluate(()=>window.target="/Clockwork Quest.game.json");
  await click("Open from My files");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("loaded and paused"));
  assert.equal(await page.$eval(".clockwork-quest-inventory",node=>node.textContent), "Carrying: brass-key, mainspring");

  await page.evaluate(()=>{
    window.fileStore.set("/Bad.game.json",{data:new TextEncoder().encode('{"format":"wrong"}'),version:"bad",status:"synced"});
    window.target="/Bad.game.json";
  });
  const before=await page.$eval(".clockwork-quest-room-title",node=>node.textContent);
  await click("Open from My files");
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("Could not open"));
  assert.equal(await page.$eval(".clockwork-quest-room-title",node=>node.textContent),before);

  await click("Resume");
  await page.evaluate(()=>window.dispatchEvent(new Event("blur")));
  await page.waitForFunction(()=>document.querySelector(".clockwork-quest-status")?.textContent.includes("lost focus"));
  assert.equal(await page.$eval(".clockwork-quest-toolbar button",node=>node.textContent),"Resume");

  await page.evaluate(()=>{
    const first=window.instances[0];
    first.controller.abort();
    first.app.dispose();
    first.app.dispose();
    first.app.element.remove();
  });
  assert.equal(await page.$$(".clockwork-quest-stage canvas").then(nodes=>nodes.length),1);
  assert.deepEqual(errors,[]);
  assert.deepEqual(external,[]);
  console.log(`PASS ${process.env.CODI_PHONE?"phone":"desktop"} Clockwork Quest adventure, save/reopen, invalid-file recovery, focus pause and disposal`);
}catch(error){
  console.error("FAIL",error.stack||error.message,"errors:",errors,"body:",await page.evaluate(()=>document.body.innerText.slice(0,1800)).catch(()=>""));
  throw error;
}finally{
  await context.close();
  await browser.disconnect();
}
