/** Actual multi-selection gestures and revision-checked account deletion. */
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import {randomBytes} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const origin = process.env.WEBOS_VIEWER_ORIGIN, output = process.env.WEBOS_TEST_OUTPUT;
assert(origin && output && path.isAbsolute(output), 'Explicit origin and new private output required.');
await mkdir(output, {mode: 0o700});
const credentials = {username: 'delete' + randomBytes(6).toString('hex'), password: randomBytes(12).toString('hex')};
await writeFile(path.join(output, 'test-credentials.json'), JSON.stringify(credentials), {mode: 0o600});
const checks = [], errors = [], consoleErrors = [];
let browser, page, otherContext;
async function button(p, name, scope = '') {
  for (const handle of await p.$$(scope + 'button')) {
    if (await handle.evaluate((n, label) => (n.querySelector('.row-text') || n).textContent.trim() === label, name)) { await handle.click(); return; }
  }
  throw Error('Button unavailable: ' + name);
}
async function login(p, register) {
  await p.goto(origin, {waitUntil: 'networkidle0'}); await p.waitForSelector('.login-gate');
  if (register) await p.click('.login-toggle');
  await p.type('[aria-label="Username"]', credentials.username); await p.type('[aria-label="Password"]', credentials.password);
  if (register) await p.type('[aria-label="Confirm password"]', credentials.password);
  await button(p, register ? 'Register' : 'Sign in', '.login-gate ');
  await p.waitForFunction(() => !!window.desktopLab?.session && !document.querySelector('.login-gate'));
  await p.click('.app-menu-button'); await button(p, 'System Tools', '.menu-pane '); await button(p, 'Files', '.menu-pane ');
  await p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Showing account files'));
}
async function run(p, operation, args = {}) {
  return p.evaluate(async ({operation, args}) => {
    const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView;
    if (operation === 'import') args.blob = new Blob([args.contents]);
    return view.execute(operation, args);
  }, {operation, args});
}
async function names(p = page) {
  return p.evaluate(async () => {
    const state = await [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView.inspect();
    return state.entries.map(e => e.name).sort();
  });
}
async function seed(folder, files) {
  await run(page, 'list', {path: ''}); await run(page, 'mkdir', {name: folder}); await run(page, 'list', {path: folder});
  for (const name of files) await run(page, 'import', {name, contents: 'Disposable fixture: ' + name});
  await page.waitForSelector('[data-chonky-context-file-id="' + folder + '/' + files[0] + '"]');
}
async function clickItem(accountPath, modifier) {
  if (modifier) await page.keyboard.down(modifier);
  try { await page.click('[data-chonky-context-file-id="' + accountPath + '"]'); }
  finally { if (modifier) await page.keyboard.up(modifier); }
}
async function deletion(count, trigger = 'toolbar') {
  if (trigger === 'keyboard') await page.keyboard.press('Delete');
  else await button(page, 'Delete', '.webos-files ');
  await page.waitForSelector('.webos-files-dialog[open]', {timeout: 5000});
  assert.equal(await page.$$eval('.webos-files-dialog li', items => items.length), count);
}
async function confirm() {
  await button(page, 'Delete', '.webos-files-dialog ');
  await page.waitForFunction(() => !document.querySelector('.webos-files-dialog') && !document.querySelector('.webos-files-browser')?.getAttribute('aria-busy')?.includes('true'));
}
async function check(name, operation) {
  try { await operation(); checks.push({name, status: 'PASS'}); return true; }
  catch (error) {
    checks.push({name, status: 'FAIL', error: error.message, visibleStatus: await page.$eval('.webos-files-status', n => n.textContent).catch(() => null)}); return false;
  }
}
try {
  browser = await puppeteer.launch({executablePath: process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true,
    args: ['--disable-dev-shm-usage'], userDataDir: path.join(output, 'browser-profile')});
  page = await browser.newPage(); await page.setViewport({width: 1600, height: 1100}); page.setDefaultTimeout(15000);
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  await login(page, true);
  const baseline = await check('Ctrl-click selects two files; one confirmation lists both; Cancel preserves all three', async () => {
    await seed('ctrl-test', ['a.txt', 'b.txt', 'keep.txt']);
    await clickItem('ctrl-test/a.txt'); await clickItem('ctrl-test/b.txt', 'Control'); await deletion(2);
    assert.deepEqual(await page.$$eval('.webos-files-dialog li', nodes => nodes.map(n => n.textContent)), ['a.txt', 'b.txt']);
    await button(page, 'Cancel', '.webos-files-dialog '); await run(page, 'list');
    assert.deepEqual(await names(), ['a.txt', 'b.txt', 'keep.txt']);
  });
  if (baseline) {
    await check('Confirmed multi-delete removes only selected files and reports the server acknowledgement', async () => {
      await deletion(2); await confirm();
      assert.deepEqual(await names(), ['keep.txt']);
      assert.match(await page.$eval('.webos-files-status', n => n.textContent), /Deleted 2 items/);
    });
    await check('Ctrl-click toggles selection; Delete key confirms files and an empty folder', async () => {
      await seed('toggle-test', ['a.txt', 'b.txt', 'keep.txt']); await run(page, 'mkdir', {name: 'empty'});
      await clickItem('toggle-test/a.txt'); await clickItem('toggle-test/b.txt', 'Control'); await clickItem('toggle-test/empty', 'Control');
      // Toggling a selected row twice preserves the other selected rows.
      // Separate successive clicks on the same row from a double-click/open.
      await new Promise(resolve => setTimeout(resolve, 600)); await clickItem('toggle-test/b.txt', 'Control');
      await new Promise(resolve => setTimeout(resolve, 600)); await clickItem('toggle-test/b.txt', 'Control'); await deletion(3, 'keyboard'); await confirm();
      assert.deepEqual(await names(), ['keep.txt']);
    });
    await check('Shift-click selects a contiguous range without deleting the following file', async () => {
      await seed('shift-test', ['a.txt', 'b.txt', 'c.txt', 'keep.txt']);
      await clickItem('shift-test/a.txt'); await clickItem('shift-test/c.txt', 'Shift'); await deletion(3); await confirm();
      assert.deepEqual(await names(), ['keep.txt']);
    });
    await check('Revision change after confirmation stops the batch, preserves changed and remaining files, and reports 1 of 3', async () => {
      await seed('revision-test', ['a.txt', 'b.txt', 'c.txt']);
      otherContext = await browser.createBrowserContext(); const other = await otherContext.newPage(); await login(other, false);
      await run(other, 'list', {path: 'revision-test'});
      await clickItem('revision-test/a.txt'); await clickItem('revision-test/c.txt', 'Shift'); await deletion(3);
      const snapshot = await run(other, 'snapshot', {path: 'revision-test/b.txt'});
      await run(other, 'remove', {path: snapshot.path, expectedRevision: snapshot.sha256});
      await run(other, 'import', {name: 'b.txt', contents: 'New revision from another browser'});
      await confirm(); assert.deepEqual(await names(), ['b.txt', 'c.txt']);
      assert.match(await page.$eval('.webos-files-status', n => n.textContent), /Confirmed deletion of 1 of 3/);
      const current = await run(page, 'snapshot', {path: 'revision-test/b.txt'}); assert.notEqual(current.sha256, snapshot.sha256);
      await otherContext.close(); otherContext = null;
    });
    await check('Nonempty folder is refused without recursively deleting its children or remaining selection', async () => {
      await seed('folder-test', ['keep.txt']); await run(page, 'mkdir', {name: 'not-empty'}); await run(page, 'list', {path: 'folder-test/not-empty'});
      await run(page, 'import', {name: 'child.txt', contents: 'Must survive'}); await run(page, 'list', {path: 'folder-test'});
      await clickItem('folder-test/not-empty'); await clickItem('folder-test/keep.txt', 'Control'); await deletion(2); await confirm();
      assert.deepEqual(await names(), ['keep.txt', 'not-empty']);
      assert.match(await page.$eval('.webos-files-status', n => n.textContent), /Confirmed deletion of 0 of 2/);
      await run(page, 'list', {path: 'folder-test/not-empty'}); assert.deepEqual(await names(), ['child.txt']);
    });
    await check('Header omits redundant controls; existing breadcrumb arrow navigates up and is disabled at root', async () => {
      assert.deepEqual(await page.$$eval('.webos-files-bar button', nodes => nodes.map(n => n.textContent.trim())), ['Refresh']);
      await run(page, 'list', {path: 'folder-test/not-empty'});
      const arrow = await page.$('.webos-files-browser button'); assert(arrow);
      assert.equal(await arrow.evaluate(n => n.disabled), false); await arrow.click();
      await page.waitForFunction(async () => {
        const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView;
        return (await view.inspect()).directory === 'folder-test';
      });
      await (await page.$('.webos-files-browser button')).click();
      await page.waitForFunction(async () => {
        const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView;
        return (await view.inspect()).directory === '';
      });
      assert.equal(await page.$eval('.webos-files-browser button', n => n.disabled), true);
    });
    await check('Reload and a fresh signed-in browser agree on surviving account files', async () => {
      await page.reload({waitUntil: 'networkidle0'});
      await page.waitForSelector('.login-gate');
      await page.type('[aria-label="Username"]', credentials.username); await page.type('[aria-label="Password"]', credentials.password);
      await button(page, 'Sign in', '.login-gate ');
      await page.waitForSelector('.webos-files-view'); await run(page, 'list', {path: 'ctrl-test'}); assert.deepEqual(await names(), ['keep.txt']);
      otherContext = await browser.createBrowserContext(); const other = await otherContext.newPage(); await login(other, false);
      await run(other, 'list', {path: 'revision-test'}); assert.deepEqual(await names(other), ['b.txt', 'c.txt']);
      await run(other, 'list', {path: 'toggle-test'}); assert.deepEqual(await names(other), ['keep.txt']);
      await otherContext.close(); otherContext = null;
    });
  }
  await page.screenshot({path: path.join(output, 'files-delete.png')});
  // Exactly one conflict and one nonempty-folder refusal are deliberate.
  // Keep their console messages; extra or unrelated refusals still fail.
  const expected = new Map();
  if (checks.find(c => c.name.startsWith('Revision change'))?.status === 'PASS') expected.set(409, 1);
  if (checks.find(c => c.name.startsWith('Nonempty folder'))?.status === 'PASS') expected.set(403, 1);
  const unexpectedConsoleErrors = consoleErrors.filter(text => {
    const code = Number(text.match(/the server responded with a status of (\d+)/)?.[1]);
    if (!(expected.get(code) > 0)) return true;
    expected.set(code, expected.get(code) - 1); return false;
  });
  const report = {status: checks.length === 8 && checks.every(c => c.status === 'PASS') && !errors.length && !unexpectedConsoleErrors.length ? 'PASS' : 'FAIL', checks, pageErrors: errors, consoleErrors, unexpectedConsoleErrors,
    scope: 'Actual pointer/keyboard selection and confirmation UI over real signed account storage, including a second browser revision conflict. Disposable test account only.'};
  await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n'); console.log(JSON.stringify({...report, output}));
  assert.equal(report.status, 'PASS');
} finally { await otherContext?.close(); await browser?.close(); }
