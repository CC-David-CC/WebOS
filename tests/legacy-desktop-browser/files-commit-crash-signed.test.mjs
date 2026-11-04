import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { randomBytes, createHash } from "node:crypto";
import { mkdtemp, rm } from "node:fs/promises";
import { once } from "node:events";
import path from "node:path";
const base = process.env.CODI_TEST_URL || "http://127.0.0.1:19967/";
if (!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(base)) throw Error("Disposable loopback fixture required");
const require2 = createRequire(process.env.PUPPETEER_CORE_PATH || "/tmp/codi-occt-release-control/node_modules/puppeteer-core");
const puppeteer = require2("puppeteer-core"), chrome = process.env.CHROME || "/snap/bin/chromium";
const profile = await mkdtemp("/home/dflanag3/snap/chromium/common/codi-commit-crash-");
const username = "crash" + randomBytes(5).toString("hex"), password = randomBytes(16).toString("base64url");
const first = "accepted before lost reply", later = "later local edit must survive";
const hash = (s) => createHash("sha256").update(s).digest("hex");
let browser, crashed = false;
async function launch() {
  return puppeteer.launch({ executablePath: chrome, userDataDir: profile, headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
}
async function login(page, register) {
  await page.goto(base);
  await page.waitForSelector(".login-toggle");
  if (register) await page.click(".login-toggle");
  await page.type("[aria-label=Username]", username);
  await page.type("[aria-label=Password]", password);
  if (register) await page.type('[aria-label="Confirm password"]', password);
  await page.click(".login-form button[type=submit]");
  await page.waitForFunction(() => window.desktopLab?.session?.kind === "registered", { timeout: 3e4 });
}
async function readRow(page) {
  return page.evaluate(async () => {
    const db = await new Promise((resolve, reject) => {
      const r = indexedDB.open("codi-mirrored-files-v1");
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
    try {
      return await new Promise((resolve, reject) => {
        const q = db.transaction("files").objectStore("files").getAll();
        q.onsuccess = () => {
          const rows = q.result.filter((x) => x.path === "/crash.txt");
          if (rows.length !== 1) return reject(Error("Expected exactly one local row"));
          const r = rows[0];
          resolve({ version: r.version, sha256: r.sha256, base: r.base, attempted: r.attempted, dirty: r.dirty, conflict: r.conflict, dataKind: r.data?.kind });
        };
        q.onerror = () => reject(q.error);
      });
    } finally {
      db.close();
    }
  });
}
try {
  browser = await launch();
  let page = await browser.newPage();
  await login(page, true);
  await page.evaluate(async () => {
    const f = (await mirrorFileContext()).files;
    await f.sync();
    await fetch("/gateway/__fixture_reset", { method: "POST" });
    const native = window.fetch;
    window.heldUpload = { requests: 0, receipts: 0 };
    window.fetch = async (input, options) => {
      const url = String(input);
      if (!url.endsWith("/gateway/upload")) return native(input, options);
      window.heldUpload.requests++;
      const response = await native(input, options);
      if (response.ok) {
        window.heldUpload.receipts++;
        return new Promise(() => {
        });
      }
      return response;
    };
  });
  const firstResult = await page.evaluate(async (text) => await (await mirrorFileContext()).files.write("/crash.txt", text, null), first);
  await page.waitForFunction(() => window.heldUpload?.receipts === 1, { timeout: 45e3 });
  const beforeRemote = await page.evaluate(async () => new TextDecoder().decode((await (await serverFileContext()).files.read("crash.txt")).data));
  assert.equal(beforeRemote, first);
  const secondResult = await page.evaluate(async ({ text, version }) => await (await mirrorFileContext()).files.write("/crash.txt", text, version), { text: later, version: firstResult.version });
  const before = await readRow(page), countsBefore = await page.evaluate(async () => await (await fetch("/gateway/__fixture_counts")).json());
  assert.deepEqual(countsBefore, { requests: 1, commits: 1 });
  assert.equal(firstResult.sha256, hash(first));
  assert.equal(secondResult.sha256, hash(later));
  assert.notEqual(firstResult.version, secondResult.version);
  assert.equal(before.version, secondResult.version);
  assert.equal(before.sha256, hash(later));
  assert.deepEqual(before.attempted, { base: null, sha256: hash(first) });
  assert.equal(before.dirty, true);
  assert.equal(before.conflict, false);
  assert.equal(before.dataKind, "codi-opfs-content/1");
  const process2 = browser.process();
  process2.kill("SIGKILL");
  await once(process2, "exit");
  crashed = true;
  browser = null;
  browser = await launch();
  page = await browser.newPage();
  await page.goto(base);
  const after = await readRow(page);
  assert.deepEqual(after, before, "durable version and attempt metadata survive process death");
  await login(page, false);
  await page.waitForFunction(async (expected) => {
    try {
      const c = await mirrorFileContext(), r = await c.files.stat("/crash.txt");
      return r.status === "synced" && r.sha256 === expected;
    } catch {
      return false;
    }
  }, { timeout: 6e4 }, hash(later));
  const result = await page.evaluate(async () => {
    const c = await mirrorFileContext(), local = await c.files.read("/crash.txt"), remote = await (await serverFileContext()).files.read("crash.txt"), counts = await (await fetch("/gateway/__fixture_counts")).json();
    return { local: new TextDecoder().decode(local.data), remote: new TextDecoder().decode(remote.data), version: local.version, status: local.status, counts };
  });
  assert.equal(result.local, later);
  assert.equal(result.remote, later);
  assert.equal(result.version, secondResult.version);
  assert.equal(result.status, "synced");
  assert.deepEqual(result.counts, { requests: 2, commits: 2 }, "one original commit and one later edit, no duplicate replay");
  const other = await browser.createBrowserContext();
  try {
    const q = await other.newPage();
    await q.goto(base);
    await q.waitForSelector(".login-toggle");
    await q.click(".login-toggle");
    await q.type("[aria-label=Username]", "other" + randomBytes(5).toString("hex"));
    await q.type("[aria-label=Password]", password);
    await q.type('[aria-label="Confirm password"]', password);
    await q.click(".login-form button[type=submit]");
    await q.waitForFunction(() => window.desktopLab?.session?.kind === "registered", { timeout: 3e4 });
    const denial = await q.evaluate(async () => {
      try {
        await (await serverFileContext()).files.read("crash.txt");
        return null;
      } catch (e) {
        return { name: e.name, status: e.status };
      }
    });
    assert.deepEqual(denial, { name: "FileRequestError", status: 404 });
  } finally {
    await other.close();
  }
  console.log("PASS signed commit\u2192newer local edit\u2192SIGKILL\u2192reopen and reconcile", JSON.stringify({ firstVersion: firstResult.version, laterVersion: secondResult.version, firstSHA: hash(first), laterSHA: hash(later), before, after, countsBefore, countsAfter: result.counts, otherAccount: 404 }));
} finally {
  if (browser) await browser.close().catch(() => {
  });
  if (crashed) await new Promise((r) => setTimeout(r, 250));
  await rm(profile, { recursive: true, force: true });
}
