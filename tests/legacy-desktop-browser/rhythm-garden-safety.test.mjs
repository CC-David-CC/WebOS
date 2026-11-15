import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19262",protocolTimeout:120000});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[];
page.on("pageerror",error=>errors.push(error.message));
page.on("dialog",dialog=>dialog.accept());

try{
 await page.setViewport({width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_RHYTHM_MANIFEST||".build/rhythm-garden-test/apps.json","utf8"));
 const entry="/"+manifest.apps[0].path.replace(/^assets\/desktop\//,"");
 await page.goto((process.env.CODI_RHYTHM_URL||"http://127.0.0.1:18345/")+"?app="+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll(".rhythm-stage canvas").length===2,{timeout:30000});

 const first=".window:nth-of-type(1) .rhythm-view";
 assert.equal(await page.$eval(first+" .rhythm-save-fields",node=>getComputedStyle(node).display),"none","closed Save location must stay hidden");
 await page.click(first+' [aria-label="Resume"]');
 await page.waitForFunction(sel=>document.querySelector(sel+" .rhythm-status")?.textContent.includes("Phrase 1 started"),{},first);
 await page.evaluate(()=>document.querySelectorAll(".window")[0].classList.remove("focused"));
 await page.waitForFunction(sel=>document.querySelector(sel+" .rhythm-status")?.textContent.includes("lost attention"),{},first);
 assert.equal(await page.$eval(first+' [aria-label="Resume"]',node=>!node.disabled),true);

 await page.$eval(first+" .rhythm-save",node=>node.open=true);
 await page.$eval(first+' [aria-label="Rhythm save path"]',node=>node.value="/Rhythm Garden.game.json");
 await page.evaluate(()=>{window.delayNextWrite();document.querySelector(".window .rhythm-view").querySelector('[aria-label="Save to My files"]').click()});
 await page.waitForFunction(()=>window.writeWaiting);
 assert.equal(await page.evaluate(()=>window.instances[0].w.rhythmGarden.dirty),true,"pending save must keep the close guard active");
 await page.$eval(first+' [aria-label="Input calibration milliseconds"]',node=>{node.value="15";node.dispatchEvent(new Event("input",{bubbles:true}))});
 await page.evaluate(()=>window.releaseWrite());
 await page.waitForFunction(sel=>document.querySelector(sel+" .rhythm-status")?.textContent.includes("syncing with the server"),{},first);
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get("/Rhythm Garden.game.json").data)));
 assert.equal(saved.payload.calibrationMs,0,"save must use the snapshot captured before delayed storage");
 assert.equal(await page.evaluate(()=>window.instances[0].w.rhythmGarden.dirty),true,"newer edits remain unsaved");

 await page.evaluate(()=>{window.fileStore.set("/bad.game.json",{data:new TextEncoder().encode('{"appId":"rhythm-garden"}'),version:"bad",status:"synced"});window.targetPath="/bad.game.json"});
 await page.evaluate(()=>{window.instances[0].w.rhythmGarden.dirty=false});
 const before=await page.$eval(first+" .rhythm-summary",node=>node.textContent);
 await page.$eval(first+' [aria-label="Open from My files"]',node=>node.click());
 await new Promise(resolve=>setTimeout(resolve,500));
 assert.match(await page.$eval(first+" .rhythm-status",node=>node.textContent),/Could not open checkpoint/);
 assert.equal(await page.$eval(first+" .rhythm-summary",node=>node.textContent),before);

 await page.evaluate(()=>{const instance=window.instances[0];instance.controller.abort();instance.app.dispose();instance.app.dispose();instance.app.element.remove()});
 assert.equal(await page.$$(".rhythm-stage canvas").then(nodes=>nodes.length),1);
 assert.deepEqual(errors,[]);
 console.log("PASS focus pause, disclosure, pending-save close guard, captured save, invalid recovery and disposal");
}finally{
 await context.close();
 await browser.disconnect();
}
