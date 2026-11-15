import assert from "node:assert/strict";
import puppeteer from "puppeteer-core";

const base = process.env.CODI_TEST_URL || "http://127.0.0.1:18312/";
const browser = await puppeteer.connect({browserURL: process.env.CODI_TEST_CDP || "http://127.0.0.1:19262", protocolTimeout: 120000});
const username = process.env.CODI_TEST_USER || "memory" + Date.now().toString().slice(-9);
const contexts = [], errors = [];

async function login(page, register, user = username) {
  page.on("pageerror", error => errors.push(error.message));
  page.on("dialog", dialog => dialog.accept());
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
  await page.evaluate(() => surfaces.get("Desktop").launch("memory-garden"));
  await page.waitForSelector(".memory-garden .memory-board");
}

const clickText = (page, label) => page.evaluate(label => {
  const root = document.querySelector(".memory-garden");
  const button = [...root.querySelectorAll("button")].find(item => item.textContent === label);
  if (!button) throw Error("Missing button: " + label);
  button.click();
}, label);

try {
  const first = await browser.createBrowserContext();
  contexts.push(first);
  const page = await first.newPage();
  await page.setViewport({width: 1366, height: 900});
  await login(page, true);
  await launch(page);
  await clickText(page, "Resume");
  await page.click(".memory-garden .memory-tile:nth-child(1)");
  await page.evaluate(() => {
    document.querySelector(".memory-save").open = true;
    document.querySelector('[aria-label="Memory Garden save path"]').value = "/Memory Garden.game.json";
  });
  await clickText(page, "Save to My files");
  await page.waitForFunction(() => document.querySelector(".memory-garden .app-status")?.textContent.includes("syncing"));
  await page.evaluate(async () => await (await mirrorFileContext()).files.sync());
  const saved = await page.evaluate(async () => JSON.parse(new TextDecoder().decode(
    (await (await serverFileContext()).files.read("Memory Garden.game.json")).data,
  )));
  assert.equal(saved.appId, "memory-garden");
  assert.equal(saved.payload.revealed.length, 1);
  await page.evaluate(() => document.querySelector(".memory-garden").closest(".window").querySelector("[aria-label=Close]").click());
  await page.waitForFunction(() => !document.querySelector(".memory-garden"));
  await page.evaluate(() => openMirrorDocument(surfaces.get("Desktop"), signedInSubject(), "/Memory Garden.game.json"));
  await page.waitForFunction(() => document.querySelector(".memory-garden .app-status")?.textContent.includes("loaded and paused"), {timeout: 30000});
  assert.equal(await page.$eval('[aria-label="Memory Garden save path"]', node => node.value), "/Memory Garden.game.json");
  assert.equal(await page.$$eval(".memory-garden .memory-tile.revealed", nodes => nodes.length), 1);

  const fresh = await browser.createBrowserContext();
  contexts.push(fresh);
  const phone = await fresh.newPage();
  await phone.setViewport({width: 412, height: 915, isMobile: true, hasTouch: true});
  await login(phone, false);
  await phone.evaluate(async () => await (await mirrorFileContext()).files.sync());
  await launch(phone);
  await phone.evaluate(() => document.querySelector(".memory-save").open = true);
  await clickText(phone, "Open from My files");
  await phone.waitForSelector('[aria-label="Choose file Memory Garden.game.json"]', {visible: true});
  await phone.click('[aria-label="Choose file Memory Garden.game.json"]');
  await phone.waitForFunction(() => document.querySelector(".memory-garden .app-status")?.textContent.includes("loaded and paused"), {timeout: 30000});
  assert.equal(await phone.$$eval(".memory-garden .memory-tile.revealed", nodes => nodes.length), 1);

  const isolation = await browser.createBrowserContext();
  contexts.push(isolation);
  const other = await isolation.newPage();
  await login(other, true, username + "b");
  assert.equal(await other.evaluate(async () => {
    try {
      await (await mirrorFileContext()).files.read("/Memory Garden.game.json");
      return true;
    } catch {
      return false;
    }
  }), false);
  await phone.evaluate(async () => {
    const context = await mirrorFileContext(), file = await context.files.read("/Memory Garden.game.json");
    await context.files.remove("/Memory Garden.game.json", file.version);
    await context.files.sync();
  });
  assert.deepEqual(errors, []);
  console.log("PASS real account save, sync, Files route, phone paused reopen and isolation");
} finally {
  for (const context of contexts) await context.close();
  await browser.disconnect();
}
