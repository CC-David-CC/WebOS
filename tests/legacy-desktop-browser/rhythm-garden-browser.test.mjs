import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||"http://127.0.0.1:19262"});
const context=await browser.createBrowserContext(),page=await context.newPage(),errors=[],external=[];
page.on("pageerror",error=>errors.push(error.message));
page.on("dialog",dialog=>dialog.accept());

const click=label=>page.evaluate(label=>{
 const button=[...document.querySelectorAll(".rhythm-view button")].find(node=>node.getAttribute("aria-label")===label||node.textContent===label);
 if(!button)throw Error("Missing button: "+label);
 button.click();
},label);

try{
 const phone=process.env.CODI_PHONE==="1";
 await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true,deviceScaleFactor:2}:{width:1366,height:900});
 const manifest=JSON.parse(await readFile(process.env.CODI_RHYTHM_MANIFEST||".build/rhythm-garden-test/apps.json","utf8"));
 const entry="/"+manifest.apps[0].path.replace(/^assets\/desktop\//,"");
 const base=process.env.CODI_RHYTHM_URL||"http://127.0.0.1:18345/",origin=new URL(base).origin;
 page.on("request",request=>{if(/^https?:/.test(request.url())&&new URL(request.url()).origin!==origin)external.push(request.url())});
 await page.goto(base+"?app="+encodeURIComponent(entry));
 await page.waitForFunction(()=>window.instances?.length===2);
 await page.waitForFunction(()=>document.querySelectorAll(".rhythm-stage canvas").length===2,{timeout:30000});
 assert.match(await page.$$eval(".rhythm-coach",nodes=>nodes[0].textContent),/Rive artwork|rhythm-flowers\.riv/i);
 assert.match(await page.$eval(".rhythm-summary",node=>node.textContent),/Garden 1 · phrase 1\/4/);

 await click("Resume");
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Phrase 1 started"));
 await new Promise(resolve=>setTimeout(resolve,480));
 const firstLane=await page.$eval(".rhythm-note-list",node=>{
  const match=node.textContent.match(/0\.50s\s+lane ([1-4])/);
  return match?Number(match[1]):1;
 });
 if(phone){
  const pad=await page.$(`.rhythm-pads button:nth-child(${firstLane})`);const box=await pad.boundingBox();
  await page.touchscreen.tap(box.x+box.width/2,box.y+box.height/2);
 }else await page.click(`.rhythm-pads button:nth-child(${firstLane})`);
 await page.waitForFunction(()=>/score [1-9]/.test(document.querySelector(".rhythm-summary")?.textContent||""));
 assert.match(await page.$eval(".rhythm-summary",node=>node.textContent),/score [1-9]/);

 await click("Pause");
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Phrase 1 complete"));
 await page.evaluate(()=>document.querySelector(".rhythm-save").open=true);
 await page.$eval('[aria-label="Rhythm save path"]',node=>node.value="/Rhythm Garden.game.json");
 await click("Save to My files");
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("syncing with the server"));
 const saved=await page.evaluate(()=>JSON.parse(new TextDecoder().decode(window.fileStore.get("/Rhythm Garden.game.json").data)));
 assert.equal(saved.appId,"rhythm-garden");
 assert.ok(saved.payload.score>0);

 await page.evaluate(()=>window.fileStore.set("/bad.game.json",{data:new TextEncoder().encode('{"appId":"rhythm-garden"}'),version:"bad",status:"synced"}));
 await page.evaluate(()=>{window.targetPath="/bad.game.json";document.querySelector('[aria-label="Open from My files"]').click()});
 await page.waitForFunction(()=>document.querySelector(".rhythm-status")?.textContent.includes("Could not open checkpoint"));
 assert.ok((await page.$eval(".rhythm-summary",node=>node.textContent)).includes(`score ${saved.payload.score}`));
 await page.evaluate(()=>{window.launchInstance=window.makeRhythm("/Rhythm Garden.game.json")});
 await page.waitForFunction(()=>[...document.querySelectorAll(".rhythm-view")].at(-1)?.querySelector(".rhythm-status")?.textContent.includes("Checkpoint loaded at its phrase boundary"));
 assert.equal(await page.$$eval('[aria-label="Rhythm save path"]',nodes=>nodes.at(-1).value),"/Rhythm Garden.game.json");
 await page.evaluate(()=>{const launched=window.launchInstance;launched.controller.abort();launched.app.dispose();launched.app.element.remove()});

 await page.evaluate(()=>{
  const first=window.instances[0];first.controller.abort();first.app.dispose();first.app.dispose();first.app.element.remove();
 });
 assert.equal(await page.$$(".rhythm-stage canvas").then(nodes=>nodes.length),1);
 await click("Resume");
 assert.deepEqual(errors,[]);
 assert.deepEqual(external,[],"Rhythm Garden must not request external services");
 console.log(`PASS ${phone?"phone":"desktop"} Rhythm Garden timing, two instances, save, invalid recovery and disposal`);
}catch(error){
 console.error("FAIL",error.stack||error.message,"errors:",errors,"body:",await page.evaluate(()=>document.body.innerText.slice(0,1200)).catch(()=>""));
 process.exitCode=1;
}finally{
 await context.close();await browser.disconnect();
}
