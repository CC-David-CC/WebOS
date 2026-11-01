import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || "http://127.0.0.1:19262",
  protocolTimeout: 120000,
});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [];
const external = [];
const origin = new URL(process.env.CODI_RELAY_URL || "http://127.0.0.1:18352/").origin;
page.on("pageerror", error => errors.push(error.message));
page.on("request", request => {
  if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== origin) external.push(request.url());
});

try {
  const phone = process.env.CODI_PHONE === "1";
  await page.setViewport(phone
    ? {width: 412, height: 915, isMobile: true, hasTouch: true, deviceScaleFactor: 2}
    : {width: 1366, height: 900});
  const manifest = JSON.parse(await readFile(
    process.env.CODI_RELAY_MANIFEST || ".build/kinetic-relay/apps.json",
    "utf8",
  ));
  const entry = "/" + manifest.apps[0].path.replace(/^assets\/desktop\//, "");
  const base = process.env.CODI_RELAY_URL || "http://127.0.0.1:18352/";
  await page.goto(base + "?app=" + encodeURIComponent(entry));
  await page.waitForSelector(".relay-stage canvas", {timeout: 60000});
  await page.waitForFunction(() => document.querySelector(".relay-info")?.textContent.includes("BUILD"));
  const layout = await page.evaluate(() => ({
    documentOverflow: document.documentElement.scrollWidth > innerWidth,
    appOverflow: document.querySelector(".kinetic-relay").scrollWidth > document.querySelector(".kinetic-relay").clientWidth,
    shortControls: [...document.querySelectorAll(".kinetic-relay button,.kinetic-relay select,.kinetic-relay input")]
      .filter(node => node.offsetParent !== null && node.getBoundingClientRect().height < (innerWidth <= 600 ? 43.5 : 39.5))
      .map(node => node.getAttribute("aria-label") || node.textContent),
  }));
  assert.equal(layout.documentOverflow, false);
  assert.equal(layout.appOverflow, false);
  assert.deepEqual(layout.shortControls, []);

  const click = async label => {
    const selector = `.relay-view [aria-label="${label}"]`;
    const element = await page.$(selector);
    assert.ok(element, selector);
    await element.scrollIntoView();
    await page.evaluate(target => target.click(), element);
  };

  await click("Add mechanism");
  await page.waitForFunction(() => /5 pieces/.test(document.querySelector(".relay-info")?.textContent || ""));
  await click("Launch marble");
  await page.waitForFunction(() => /RUNNING/.test(document.querySelector(".relay-info")?.textContent || ""));
  await page.waitForFunction(() => {
    const tick = Number(document.querySelector(".relay-info")?.textContent?.match(/tick (\d+)/)?.[1] || 0);
    return tick > 0;
  });
  await page.evaluate(() => window.dispatchEvent(new Event("blur")));
  await page.waitForFunction(() => /Paused/.test(document.querySelector(".relay-info")?.textContent || ""));
  await click("Save to My files");
  await page.waitForFunction(() => document.querySelector(".relay-view .app-status")?.textContent.includes("syncing with the server"));
  const saved = await page.evaluate(() => JSON.parse(
    new TextDecoder().decode(window.test.store.get("/Kinetic Relay.game.json").data),
  ));
  assert.equal(saved.appId, "kinetic-relay");
  assert.equal(saved.payload.phase, "running");
  assert.equal(saved.payload.paused, true);
  assert.equal(saved.payload.build.length, 5);

  await click("Reset puzzle");
  await page.waitForFunction(() => /BUILD/.test(document.querySelector(".relay-info")?.textContent || ""));
  await click("Open from My files");
  await page.waitForFunction(() => document.querySelector(".relay-view .app-status")?.textContent.includes("loaded and paused"));
  assert.equal(await page.$eval('[aria-label="Kinetic Relay save path"]', node => node.value), "/Kinetic Relay.game.json");
  await page.evaluate(() => {
    window.test.store.set("/bad.game.json", {
      data: new TextEncoder().encode("{broken"),
      version: "bad",
      status: "synced",
    });
    globalThis.target = "/bad.game.json";
  });
  await click("Open from My files");
  await page.waitForFunction(() => document.querySelector(".relay-view .app-status")?.textContent.includes("Could not open relay"));
  assert.match(await page.$eval(".relay-info", node => node.textContent), /5 pieces/);

  await page.evaluate(() => window.test.dispose());
  await page.waitForFunction(() => !document.querySelector(".relay-view"));
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log(`PASS ${phone ? "phone" : "desktop"} Kinetic Relay build, launch, focus pause, save/reopen, invalid recovery and disposal`);
} finally {
  await context.close();
  await browser.disconnect();
}
