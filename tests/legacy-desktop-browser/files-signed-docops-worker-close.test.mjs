import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
const require = createRequire(process.env.PUPPETEER_CORE_PATH || "/tmp/codi-occt-release-control/node_modules/puppeteer-core");
const puppeteer = require("puppeteer-core");
const base = process.env.CODI_TEST_URL || "http://127.0.0.1:19967/";
if (!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(base)) throw Error("Requires isolated loopback fixture");
const browser = await puppeteer.connect({ browserURL: process.env.CODI_TEST_CDP || "http://127.0.0.1:19296", protocolTimeout: 12e4 });
try {
  for (const phone of [false, true]) {
    const ctx = await browser.createBrowserContext();
    const page = await ctx.newPage();
    const errors = [];
    const dir = await mkdtemp(path.join(os.homedir(), "codi-files-docops-download-"));
    const user = (phone ? "opsphone" : "opsdesk") + Date.now().toString().slice(-9);
    page.on("pageerror", (e) => errors.push(e.message));
    try {
      await page.setViewport(phone ? { width: 412, height: 915, isMobile: true, hasTouch: true } : { width: 1366, height: 900 });
      await page.goto(base);
      await page.waitForSelector(".login-toggle");
      await page.click(".login-toggle");
      await page.type("[aria-label=Username]", user);
      await page.type("[aria-label=Password]", "test1234");
      await page.type('[aria-label="Confirm password"]', "test1234");
      await page.click(".login-form button[type=submit]");
      await page.waitForFunction(() => window.desktopLab?.session?.kind === "registered", { timeout: 3e4 });
      await page._client().send("Page.setDownloadBehavior", { behavior: "allow", downloadPath: dir });
      const expected = await page.evaluate(async () => {
        const a = new Uint8Array(8 * 1024 * 1024 + 7);
        for (let i = 0; i < a.length; i++) a[i] = i % 251;
        const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", a))].map((x) => x.toString(16).padStart(2, "0")).join("");
        const f = (await mirrorFileContext()).files;
        await f.write("/large.bin", new Blob([a]), null);
        await f.sync();
        surfaces.get("Desktop").launch("files");
        return hash;
      });
      await page.waitForSelector('[data-chonky-file-id="/large.bin"]', { timeout: 6e4 });
      await page.evaluate(() => {
        window.copyEvidence = { progress: 0, terminated: 0, closed: false, urls: 0 };
        const Native = window.Worker, create = URL.createObjectURL.bind(URL);
        window.restoreCopyEvidence = () => {
          window.Worker = Native;
          URL.createObjectURL = create;
        };
        URL.createObjectURL = (value) => {
          window.copyEvidence.urls++;
          return create(value);
        };
        window.Worker = class extends Native {
          postMessage(message, ...rest) {
            this.copy = message?.action === "copy";
            return super.postMessage(message, ...rest);
          }
          set onmessage(fn) {
            super.onmessage = (event) => {
              if (this.copy && event.data?.progress !== void 0) {
                window.copyEvidence.progress++;
                if (!window.copyEvidence.closed) {
                  window.copyEvidence.closed = true;
                  document.querySelector(".files-content").closest("[data-window]").querySelector("[aria-label=Close]").click();
                }
              }
              fn(event);
            };
          }
          terminate() {
            if (this.copy) window.copyEvidence.terminated++;
            return super.terminate();
          }
        };
      });
      if (phone) await page.tap('[data-chonky-file-id="/large.bin"]');
      else await page.click('[data-chonky-file-id="/large.bin"]');
      await page.waitForSelector('.codi-chonky button[aria-label="Download"]:not([disabled])');
      if (phone) await page.tap('.codi-chonky button[aria-label="Download"]');
      else await page.click('.codi-chonky button[aria-label="Download"]');
      await page.waitForFunction(() => window.copyEvidence.closed && window.copyEvidence.terminated > 0, { timeout: 45e3 });
      await page.waitForFunction(() => !document.querySelector(".files-content"));
      await page.waitForFunction(async () => !(await navigator.locks.query()).held.some((x) => x.name.startsWith("codi-content:")), { timeout: 1e4 });
      const first = await page.evaluate(() => ({ ...window.copyEvidence }));
      assert.ok(first.progress > 0);
      assert.equal(first.terminated, 1);
      assert.equal(first.urls, 0, "close during actual worker does not start download");
      await page.evaluate(() => window.restoreCopyEvidence());
      await page.evaluate(() => surfaces.get("Desktop").launch("files"));
      await page.waitForSelector('[data-chonky-file-id="/large.bin"]');
      const downloads = await browser.target().createCDPSession();
      await downloads.send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath: dir, eventsEnabled: true });
      let guid = null, closeFinished = false, completedBeforeCloseFinished = false, closeResult = null;
      let acceptResolve, completeResolve;
      const accepted = new Promise((r) => acceptResolve = r), completed = new Promise((r) => completeResolve = r);
      // CDP event delivery and the page close command are asynchronous. Record
      // their observed order; it does not prove the instant bytes reached disk.
      downloads.on("Browser.downloadWillBegin", (event) => {
        if (guid) return;
        guid = event.guid;
        acceptResolve();
        closeResult = page.evaluate(() => document.querySelector(".files-content").closest("[data-window]").querySelector("[aria-label=Close]").click()).then(() => {
          closeFinished = true;
        });
      });
      downloads.on("Browser.downloadProgress", (event) => {
        if (event.guid !== guid) return;
        if (event.state === "completed") {
          if (!closeFinished) completedBeforeCloseFinished = true;
          completeResolve(event.state);
        } else if (event.state === "canceled") completeResolve(event.state);
      });
      if (phone) await page.tap('[data-chonky-file-id="/large.bin"]');
      else await page.click('[data-chonky-file-id="/large.bin"]');
      await page.waitForSelector('.codi-chonky button[aria-label="Download"]:not([disabled])');
      if (phone) await page.tap('.codi-chonky button[aria-label="Download"]');
      else await page.click('.codi-chonky button[aria-label="Download"]');
      await Promise.race([accepted, new Promise((_, reject) => setTimeout(() => reject(Error("Chromium did not accept the download")), 15e3))]);
      await closeResult;
      await page.waitForFunction(() => !document.querySelector(".files-content"));
      const downloadState = await Promise.race([completed, new Promise((_, reject) => setTimeout(() => reject(Error("Chromium did not finish the download")), 3e4))]);
      assert.equal(downloadState, "completed", "accepted download completes despite the Files close request");
      await downloads.detach();
      console.log("DOWNLOAD_HANDOFF", JSON.stringify({ phone, accepted: true, completedObservedBeforeCloseFinished: completedBeforeCloseFinished, closed: true, downloadState }));
      let bytes;
      for (let i = 0; i < 150; i++) {
        try {
          bytes = await readFile(path.join(dir, "large.bin"));
          break;
        } catch {
        }
        await new Promise((r) => setTimeout(r, 100));
      }
      assert.ok(bytes, "download missing");
      assert.equal(bytes.length, 8 * 1024 * 1024 + 7);
      assert.equal(createHash("sha256").update(bytes).digest("hex"), expected);
      const remote = await page.evaluate(async () => {
        const v = await (await serverFileContext()).files.version("large.bin");
        return v.sha256;
      });
      assert.equal(remote, expected);
      assert.deepEqual(errors, []);
      console.log("PASS signed real OPFS copy close, lease release, reopen/download/server hash", phone ? "phone-sized" : "desktop", JSON.stringify(first));
    } catch (e) {
      console.error("DETAIL", phone ? "phone" : "desktop", await page.evaluate(() => document.body.innerText.slice(-1e3)).catch(() => ""), errors);
      throw e;
    } finally {
      await ctx.close();
      await rm(dir, { recursive: true, force: true });
    }
  }
} finally {
  await browser.disconnect();
}
