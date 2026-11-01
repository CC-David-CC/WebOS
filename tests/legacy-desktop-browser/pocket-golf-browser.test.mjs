import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||process.env.CODI_BROWSER_URL||"http://127.0.0.1:19320",protocolTimeout:120000});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const base=process.env.CODI_TEST_URL||"http://127.0.0.1:18320/";
const errors=[],external=[];
page.on("pageerror",error=>errors.push(error.message));
page.on("dialog",dialog=>dialog.accept());
page.on("request",request=>{
  if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==new URL(base).origin)external.push(request.url());
});
const click=label=>page.evaluate(label=>{
  const button=[...document.querySelectorAll(".pocket-golf-view button")].find(node=>node.getAttribute("aria-label")===label||node.textContent===label);
  if(!button)throw Error("Missing button: "+label);
  button.click();
},label);

try{
  await page.setViewport(process.env.CODI_PHONE?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});
  const manifest=JSON.parse(await readFile(process.env.CODI_POCKET_GOLF_MANIFEST||".build/pocket-golf/apps.json","utf8"));
  const entry="/"+manifest.apps[0].path.replace(/^assets\/desktop\//,"");
  await page.goto(base+"?app="+encodeURIComponent(entry));
  await page.waitForSelector(".pocket-golf-stage canvas",{timeout:60000});
  await page.waitForFunction(()=>document.querySelector(".pocket-golf-status")?.textContent.includes("Press Start")||document.querySelector(".pocket-golf-status")?.textContent.includes("settled")||document.querySelector(".pocket-golf-status")?.textContent.includes("ready"),{timeout:60000});
  assert.ok(await page.$(".pocket-golf-rive-pending"));
  assert.match(await page.$eval(".pocket-golf-rive-pending",node=>node.textContent),/Rive artwork.*pending/i);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,"no document horizontal overflow");

  await click("Start / resume");
  await page.waitForFunction(()=>document.querySelector(".pocket-golf-status")?.textContent.includes("Putting"));
  await page.evaluate(()=>window.dispatchEvent(new Event("blur")));
  await page.waitForFunction(()=>document.querySelector(".pocket-golf-status")?.textContent.includes("paused"));
  await click("Start / resume");
  await click("Putt");
  await page.waitForFunction(()=>document.querySelector(".pocket-golf-status")?.textContent.includes("Ball rolling"),{timeout:30000});
  await click("Save to My files");
  await page.waitForFunction(()=>{
    const text=document.querySelector(".pocket-golf-status")?.textContent||"";
    return text.includes("Checkpoint saved")||text.includes("last settled checkpoint");
  },{timeout:30000});
  const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get("/Pocket Golf.game.json").data)));
  assert.equal(saved.appId,"pocket-golf");
  assert.equal(saved.format,"ksu.game.save");
  assert.ok(saved.payload.lastSafe);

  await page.evaluate(()=>window.fileStore.set("/Bad.game.json",{data:new TextEncoder().encode('{"format":"wrong"}'),version:"bad",status:"synced"}));
  await page.evaluate(()=>globalThis.target="/Bad.game.json");
  await click("Open from My files");
  await page.waitForFunction(()=>document.querySelector(".pocket-golf-status")?.textContent.includes("Could not open checkpoint"),{timeout:30000});
  assert.ok(await page.$(".pocket-golf-stage canvas"),"failed open keeps the current game");

  await page.evaluate(()=>{
    const instance=window.test.instance;
    instance.app.dispose();
    instance.app.dispose();
    instance.app.element.remove();
  });
  assert.equal(await page.$(".pocket-golf-view"),null);
  assert.deepEqual(errors,[]);
  assert.deepEqual(external,[]);
  console.log(`PASS ${process.env.CODI_PHONE?"phone":"desktop"} Pocket Golf Havok load, play, checkpoint save, invalid-file recovery and disposal`);
}catch(error){
  console.error("Diagnostics:",await page.evaluate(()=>({
    status:document.querySelector(".pocket-golf-status")?.textContent,
    body:document.body.innerText.slice(0,1800),
  })).catch(()=>null),errors,external);
  throw error;
}finally{
  await context.close();
  await browser.disconnect();
}
