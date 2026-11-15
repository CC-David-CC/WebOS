import assert from "node:assert/strict";
import puppeteer from "puppeteer-core";

const base = process.env.CODI_TEST_URL || "http://127.0.0.1:18352/";
const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || "http://127.0.0.1:19262",
  protocolTimeout: 120000,
});
const username = process.env.CODI_TEST_USER || "relay" + Date.now().toString().slice(-9);
const contexts = [];
const errors = [];

async function login(page, register, user = username) {
  page.on("pageerror", error => errors.push(error.message));
  await page.evaluateOnNewDocument(() => {
    const original = window.fetch;
    window.fetch = (url, ...args) => String(url).endsWith("assets/terminal/v2/image.json")
      ? Promise.resolve(new Response("", {status: 404}))
      : original(url, ...args);
  });
  await page.goto(base);
  await page.waitForSelector(".login-toggle");
  if (register) await page.click(".login-toggle");
  await page.type("[aria-label=Username]", user);
  await page.type("[aria-label=Password]", "test1234");
  if (register) await page.type('[aria-label="Confirm password"]', "test1234");
  await page.click(".login-form button[type=submit]");
  await page.waitForFunction(() => window.desktopLab?.session?.kind === "registered", {timeout: 30000});
}

async function launch(page) {
  await page.evaluate(() => surfaces.get("Desktop").launch("kinetic-relay"));
  await page.waitForSelector(".relay-stage canvas", {timeout: 60000});
  await page.waitForFunction(() => document.querySelector(".relay-info")?.textContent.includes("BUILD"));
}

try{
 for(const phone of [false,true]){
  const context=await browser.createBrowserContext();contexts.push(context);const page=await context.newPage();await page.setViewport(phone?{width:412,height:915,isMobile:true,hasTouch:true}:{width:1366,height:900});await login(page,true,username+(phone?'b':'a'));await launch(page);
  const click=async label=>page.evaluate(label=>{const b=[...document.querySelectorAll('.relay-view button')].find(e=>e.getAttribute('aria-label')===label||e.textContent===label);if(!b)throw Error('Missing '+label);b.click()},label);
  await click('Launch marble');await page.evaluate(()=>document.querySelector('.relay-save').open=true);await click('Save to My files');await page.waitForFunction(()=>document.querySelector('.relay-view .app-status')?.textContent.includes('syncing with the server'));await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());const first=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Kinetic Relay.game.json')).data)));
  await click('Step');await page.evaluate(()=>document.querySelector('.relay-view').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForSelector('dialog.codi-confirm-dialog[open]');await page.click('dialog.codi-confirm-dialog .codi-confirm-actions button:first-child');assert.ok(await page.$('.relay-view'),'step must cause unsaved close warning');
  await page.evaluate(async()=>{const c=await mirrorFileContext(),f=await c.files.read('/Kinetic Relay.game.json');await c.files.remove('/Kinetic Relay.game.json',f.version);await c.files.sync()});await click('Save to My files');await page.waitForFunction(()=>document.querySelector('.relay-view .app-status')?.textContent.includes('saved relay was removed'));assert.equal(await page.evaluate(async()=>{try{await(await mirrorFileContext()).files.read('/Kinetic Relay.game.json');return true}catch{return false}}),false);
  await page.$eval('[aria-label="Kinetic Relay save path"]',e=>e.value='/Relay copy.game.json');await click('Save to My files');await page.waitForFunction(()=>document.querySelector('.relay-view .app-status')?.textContent.includes('syncing with the server'));await page.evaluate(async()=>await(await mirrorFileContext()).files.sync());const copy=await page.evaluate(async()=>JSON.parse(new TextDecoder().decode((await(await serverFileContext()).files.read('Relay copy.game.json')).data)));assert.ok(copy.payload.tick>first.payload.tick,'stepped state saved in copy');
  await page.evaluate(()=>document.querySelector('.relay-view').closest('.window').querySelector('[aria-label=Close]').click());await page.waitForFunction(()=>!document.querySelector('.relay-view'));await page.evaluate(()=>openMirrorDocument(surfaces.get('Desktop'),signedInSubject(),'/Relay copy.game.json'));await page.waitForFunction(()=>document.querySelector('.relay-view .app-status')?.textContent.includes('Relay loaded and paused'));assert.match(await page.$eval('.relay-info',e=>e.textContent),new RegExp('tick '+copy.payload.tick));
 }
 assert.deepEqual(errors,[]);console.log('PASS desktop and emulated phone step dirty, missing-file protection, copy sync and reopen');
}finally{for(const context of contexts)await context.close();await browser.disconnect()}
