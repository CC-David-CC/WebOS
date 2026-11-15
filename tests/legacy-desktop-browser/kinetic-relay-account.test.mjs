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

try {
  const first = await browser.createBrowserContext();
  contexts.push(first);
  const page = await first.newPage();
  await page.setViewport({width: 1366, height: 900});
  await login(page, true);
  await launch(page);
  await page.click('.relay-view [aria-label="Add mechanism"]');
  await page.click('.relay-view [aria-label="Launch marble"]');
  await page.evaluate(() => {
    document.querySelector('.relay-save').open = true;
    document.querySelector('[aria-label="Kinetic Relay save path"]').value = "/Kinetic Relay.game.json";
  });
  await page.$eval('.relay-view [aria-label="Save to My files"]', node => node.scrollIntoView({block: "center"}));
  await page.click('.relay-view [aria-label="Save to My files"]');
  await page.waitForFunction(() => document.querySelector(".relay-view .app-status")?.textContent.includes("syncing with the server"), {timeout: 30000});
  await page.evaluate(async () => (await mirrorFileContext()).files.sync());
  const saved = await page.evaluate(async () => JSON.parse(new TextDecoder().decode(
    (await (await serverFileContext()).files.read("Kinetic Relay.game.json")).data,
  )));
  assert.equal(saved.appId, "kinetic-relay");
  assert.equal(saved.payload.build.length, 5);
  await page.evaluate(() => document.querySelector(".kinetic-relay").closest(".window")
    .querySelector("[aria-label=Close]").click());
  await page.waitForFunction(() => !document.querySelector(".kinetic-relay"));
  await page.evaluate(() => openMirrorDocument(
    surfaces.get("Desktop"), signedInSubject(), "/Kinetic Relay.game.json"));
  await page.waitForFunction(() => document.querySelector(".relay-view .app-status")?.textContent.includes("loaded and paused"), {timeout: 30000});
  assert.equal(await page.$eval('[aria-label="Kinetic Relay save path"]', node => node.value), "/Kinetic Relay.game.json");

  const fresh = await browser.createBrowserContext();
  contexts.push(fresh);
  const phone = await fresh.newPage();
  await phone.setViewport({width: 412, height: 915, isMobile: true, hasTouch: true});
  await login(phone, false);
  await phone.evaluate(async () => (await mirrorFileContext()).files.sync());
  await launch(phone);
  await phone.evaluate(() => {
    document.querySelector(".relay-save").open = true;
    document.querySelector('.relay-view [aria-label="Open from My files"]').scrollIntoView({block: "center"});
  });
  await phone.click('.relay-view [aria-label="Open from My files"]');
  await phone.waitForSelector('[aria-label="Choose file Kinetic Relay.game.json"]', {visible: true});
  await phone.click('[aria-label="Choose file Kinetic Relay.game.json"]');
  await phone.waitForFunction(() => document.querySelector(".relay-view .app-status")?.textContent.includes("loaded and paused"), {timeout: 30000});
  assert.match(await phone.$eval(".relay-info", node => node.textContent), /5 pieces/);

  const isolation = await browser.createBrowserContext();
  contexts.push(isolation);
  const other = await isolation.newPage();
  await login(other, true, username + "b");
  assert.equal(await other.evaluate(async () => {
    try {
      await (await mirrorFileContext()).files.read("/Kinetic Relay.game.json");
      return true;
    } catch {
      return false;
    }
  }), false);

  await phone.evaluate(async () => {
    const context = await mirrorFileContext();
    const file = await context.files.read("/Kinetic Relay.game.json");
    await context.files.remove("/Kinetic Relay.game.json", file.version);
    await context.files.sync();
  });
  assert.deepEqual(errors, []);
  console.log("PASS real account save, sync, Files route, phone paused reopen and isolation");
} finally {
  for (const context of contexts) await context.close();
  await browser.disconnect();
}
