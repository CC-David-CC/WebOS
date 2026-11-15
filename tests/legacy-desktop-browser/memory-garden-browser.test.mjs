import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import puppeteer from "puppeteer-core";

const browser = await puppeteer.connect({browserURL: process.env.CODI_TEST_CDP || "http://127.0.0.1:19262"});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [], external = [];
page.on("pageerror", error => errors.push(error.message));
page.on("dialog", dialog => dialog.accept());
page.on("request", request => {
  if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== "http://127.0.0.1:18362") external.push(request.url());
});
const first = ".memory-garden";
const second = () => `.memory-garden:nth-of-type(2)`;
const tile = (index, scope = first) => `${scope} .memory-tile:nth-child(${index + 1})`;
const clickText = (label, scope = first) => page.evaluate((label, scope) => {
  const root = document.querySelector(scope);
  const button = [...root.querySelectorAll("button")].find(item => item.textContent === label);
  if (!button) throw Error("Missing button: " + label);
  button.click();
}, label, scope);
const tileState = async (index, scope = first) => page.$eval(tile(index, scope), node => ({
  disabled: node.disabled,
  motif: node.dataset.riveMotif,
  state: node.dataset.state,
  matched: node.classList.contains("matched"),
}));
const revealTile = (index, scope = first) => page.$eval(tile(index, scope), node => node.click());
const boardState = (scope = first) => page.evaluate(scope => {
  const root = document.querySelector(scope);
  return {
    count: root.querySelectorAll(".memory-tile").length,
    revealed: [...root.querySelectorAll(".memory-tile.revealed")].length,
    matched: [...root.querySelectorAll(".memory-tile.matched")].length,
    status: root.querySelector(".app-status")?.textContent,
    timer: root.querySelector(".memory-rive-state")?.textContent,
  };
}, scope);

try {
  await page.setViewport(process.env.CODI_PHONE ? {width: 412, height: 915, isMobile: true, hasTouch: true} : {width: 1366, height: 900});
  const manifest = JSON.parse(await readFile(process.env.CODI_MEMORY_MANIFEST || ".build/memory-garden-test/apps.json", "utf8"));
  const entry = "/" + manifest.apps[0].path.replace(/^assets\/desktop\//, "");
  await page.goto((process.env.CODI_MEMORY_URL || "http://127.0.0.1:18362/") + "?app=" + encodeURIComponent(entry));
  await page.waitForFunction(() => window.instances?.length === 2 && document.querySelectorAll(".memory-garden").length === 2);
  assert.equal((await boardState()).count, 12);
  assert.match((await boardState()).status, /paused/i);
  const layout = await page.evaluate(() => {
    const app = document.querySelector(".memory-garden");
    const buttons = [...app.querySelectorAll("button")].filter(button => button.offsetParent !== null);
    return {
      sizes: [...app.querySelectorAll("select option")].map(option => option.value),
      overflow: document.documentElement.scrollWidth > innerWidth || app.scrollWidth > app.clientWidth,
      shortest: Math.min(...buttons.map(button => button.getBoundingClientRect().height)),
    };
  });
  assert.deepEqual(layout.sizes, ["practice", "garden", "grand"]);
  assert.equal(layout.overflow, false);
  if (process.env.CODI_PHONE) assert.ok(layout.shortest >= 44, "phone controls must have 44px targets");

  await clickText("Resume");
  await page.evaluate(() => document.querySelector(".memory-garden .memory-tile:not(:disabled)").focus());
  const focusedBefore = await page.evaluate(() => document.activeElement?.getAttribute("aria-label"));
  await page.keyboard.press("ArrowRight");
  assert.notEqual(await page.evaluate(() => document.activeElement?.getAttribute("aria-label")), focusedBefore, "arrow keys move board focus");
  const firstMotifs = await page.evaluate(() => window.instances[0].host.w.memoryGarden.session.tiles.map(tile => tile.motif));
  const left = 0, right = firstMotifs.findIndex((motif, index) => index > 0 && motif !== firstMotifs[0]);
  assert.ok(right > 0);
  await revealTile(0);
  await revealTile(right);
  await page.evaluate(() => window.instances[0].windowElement.classList.remove("focused"));
  await new Promise(resolve => setTimeout(resolve, 120));
  const pausedMismatch = await boardState();
  assert.match(pausedMismatch.timer, /mismatch/);
  await new Promise(resolve => setTimeout(resolve, 450));
  assert.equal((await boardState()).timer, pausedMismatch.timer, "mismatch timer pauses with the window");
  await page.evaluate(() => window.instances[0].windowElement.classList.add("focused"));
  await clickText("Resume");
  await page.waitForFunction(scope => document.querySelector(scope).querySelectorAll(".memory-tile.revealed").length === 0, {timeout: 3000}, first);

  const beforeCancel = await boardState();
  await page.evaluate(() => { window.confirmAnswer = false; document.querySelector(".memory-garden select").value = "garden"; document.querySelector(".memory-garden select").dispatchEvent(new Event("change", {bubbles: true})); });
  await new Promise(resolve => setTimeout(resolve, 250));
  assert.equal((await boardState()).count, beforeCancel.count);
  await page.evaluate(() => { window.confirmAnswer = true; document.querySelector(".memory-garden select").value = "garden"; document.querySelector(".memory-garden select").dispatchEvent(new Event("change", {bubbles: true})); });
  await page.waitForFunction(scope => document.querySelector(scope).querySelectorAll(".memory-tile").length === 16, {}, first);

  await clickText("Resume");
  const gardenMotifs = await page.evaluate(() => window.instances[0].host.w.memoryGarden.session.tiles.map(tile => tile.motif));
  const saveRight = gardenMotifs.findIndex((motif, index) => index > 0 && motif !== gardenMotifs[0]);
  assert.ok(saveRight > 0);
  await revealTile(0);
  await revealTile(saveRight);
  await page.evaluate(() => {
    document.querySelector(".memory-save").open = true;
    document.querySelector('[aria-label="Memory Garden save path"]').value = "/Memory Garden.game.json";
  });
  await clickText("Save to My files");
  await page.waitForFunction(scope => document.querySelector(scope).querySelector(".app-status")?.textContent.includes("syncing"), {}, first);
  const saved = await page.evaluate(() => JSON.parse(new TextDecoder().decode(window.fileStore.get("/Memory Garden.game.json").data)));
  assert.equal(saved.appId, "memory-garden");
  assert.equal(saved.payload.size, "garden");
  assert.equal(saved.payload.revealed.length, 2);
  assert.ok(saved.payload.pendingMismatchMs > 0);

  await page.evaluate(() => {
    window.fileStore.set("/bad.game.json", {data: new TextEncoder().encode("{bad"), version: "bad"});
    window.targetPath = "/bad.game.json";
  });
  await clickText("Open from My files");
  await page.waitForFunction(scope => document.querySelector(scope).querySelector(".app-status")?.textContent.includes("Could not open"), {}, first);
  assert.equal((await boardState()).count, 16);
  await page.evaluate(() => { window.confirmAnswer = true; });
  await clickText("New garden");
  await page.waitForFunction(scope => document.querySelector(scope).querySelector(".app-status")?.textContent.includes("New garden ready"), {}, first);
  assert.equal((await boardState()).revealed, 0);
  await clickText("Resume");
  await revealTile(0);
  await new Promise(resolve => setTimeout(resolve, 1050));
  assert.equal((await boardState()).revealed, 1, "restart cancels the prior mismatch cycle");
  await page.evaluate(() => window.instances[0].view.dispose());
  await page.evaluate(() => window.instances[0].view.dispose());
  await page.evaluate(() => window.instances[0].view.element.remove());
  assert.equal(await page.$$(".memory-garden").then(nodes => nodes.length), 1);
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log("PASS seeded board, mismatch pause, save during mismatch, invalid recovery, independent instances and idempotent disposal");
} finally {
  await context.close();
  await browser.disconnect();
}
