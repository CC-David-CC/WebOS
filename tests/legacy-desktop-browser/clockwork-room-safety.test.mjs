import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser=await puppeteer.connect({
  browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19282",
  protocolTimeout:120000,
});
const context=await browser.createBrowserContext();
const page=await context.newPage();
const base=process.env.CODI_CLOCKWORK_URL||"http://127.0.0.1:18343/";
const errors=[];
page.on("pageerror",error=>errors.push(error.message));

try{
  await page.setViewport({width:1366,height:900});
  const manifest=JSON.parse(await readFile(
    process.env.CODI_CLOCKWORK_MANIFEST||".build/clockwork-room/apps.json",
    "utf8",
  ));
  const entry="/"+manifest.apps[0].path.replace(/^assets\/desktop\//,"");
  await page.goto(base+"?app="+encodeURIComponent(entry));
  await page.waitForFunction(()=>window.instances?.length===2);
  await page.waitForSelector(".clockwork-stage-wrap canvas",{timeout:30000});
  await page.waitForFunction(()=>document.querySelectorAll(".clockwork-loading").length===0,{timeout:30000});

  await page.evaluate(()=>document.querySelector('.clockwork-toolbar [aria-label="Run"]').click());
  await page.waitForFunction(()=>document.querySelector(".clockwork-status")?.textContent.includes("Room running"));
  await page.evaluate(()=>window.instances[0].wrapper.classList.remove("focused"));
  await page.waitForFunction(()=>document.querySelector(".clockwork-status")?.textContent.includes("paused"));

  await page.evaluate(()=>{
    const instance=window.instances[0];
    instance.wrapper.classList.add("focused");
    document.querySelector('.clockwork-toolbar [aria-label="Run"]').click();
    document.querySelector(".clockwork-save").open=true;
    document.querySelector('[aria-label="Clockwork room save path"]').value="/Pending.game.json";
    const files=window.clockworkContext.files;
    const write=files.write.bind(files);
    window.__releaseClockworkWrite=null;
    files.write=async(...args)=>{
      await new Promise(resolve=>{window.__releaseClockworkWrite=resolve});
      files.write=write;
      return write(...args);
    };
    [...document.querySelectorAll('.clockwork-toolbar button')].find(button=>button.textContent==="Save").click();
  });
  await page.waitForFunction(()=>typeof window.__releaseClockworkWrite==="function");
  assert.equal(await page.evaluate(()=>window.instances[0].w.clockworkRoom.dirty),true,"in-flight save must guard close");
  await page.evaluate(()=>window.__releaseClockworkWrite());
  await page.waitForFunction(()=>document.querySelector(".clockwork-status")?.textContent.includes("syncing with the server"));
  assert.deepEqual(errors,[]);
  console.log("PASS focus-loss pause and pending-save close protection");
}finally{
  await context.close();
  await browser.disconnect();
}
