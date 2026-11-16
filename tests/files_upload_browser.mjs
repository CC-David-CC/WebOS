/** Real file-picker and external-file drop regression over signed account storage. */
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import {randomBytes, createHash} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const origin = process.env.WEBOS_VIEWER_ORIGIN, output = process.env.WEBOS_TEST_OUTPUT;
assert(origin && output && path.isAbsolute(output), 'Explicit origin and new private output required.');
await mkdir(output, {mode: 0o700});
const credentials = {username: 'upload' + randomBytes(6).toString('hex'), password: randomBytes(12).toString('hex')};
await writeFile(path.join(output, 'test-credentials.json'), JSON.stringify(credentials), {mode: 0o600});
// Opaque binary payload with an MP4 filename: Files must preserve arbitrary
// bytes without requiring a media decoder. No user media is used in this test.
const bytes = Buffer.alloc(4 * 1024 * 1024);
for (let i = 0; i < bytes.length; i++) bytes[i] = (i * 31 + Math.floor(i / 65536)) & 255;
const expected = createHash('sha256').update(bytes).digest('hex');
const pickerPath = path.join(output, 'picker 4 MiB.mp4'), dropPath = path.join(output, 'drop 4 MiB.mp4');
await writeFile(pickerPath, bytes); await writeFile(dropPath, bytes);
const checks = [], errors = [], consoleErrors = [], responses = [];
let browser, page;
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
  await p.waitForSelector('.webos-files-view');
  await p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Showing account files'));
}
async function saved(p, filename, accountPath = filename) {
  await p.waitForFunction(name => [...document.querySelectorAll('.webos-files-browser [title]')].some(n => n.title === name), {timeout: 25000}, filename);
  const result = await p.evaluate(async accountPath => {
    const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView;
    const snapshot = await view.execute('snapshot', {path: accountPath});
    const value = await view.execute('download', {path: accountPath, expectedRevision: snapshot.sha256});
    return {bytes: value.data.length, sha256: [...new Uint8Array(await crypto.subtle.digest('SHA-256', value.data))].map(n => n.toString(16).padStart(2, '0')).join('')};
  }, accountPath);
  assert.deepEqual(result, {bytes: bytes.length, sha256: expected});
}
async function check(name, operation) {
  try { await operation(); checks.push({name, status: 'PASS'}); }
  catch (error) { checks.push({name, status: 'FAIL', error: error.message, visibleStatus: await page.$eval('.webos-files-status', n => n.textContent).catch(() => null)}); }
}
try {
  browser = await puppeteer.launch({executablePath: process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true,
    args: ['--disable-dev-shm-usage'], userDataDir: path.join(output, 'browser-profile')});
  page = await browser.newPage(); await page.setViewport({width: 1440, height: 1000}); page.setDefaultTimeout(10000);
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('response', response => { const pathname = new URL(response.url()).pathname; if (pathname.startsWith('/gateway/')) responses.push({path: pathname, status: response.status()}); });
  await login(page, true);
  await check('Upload button opens native picker and saves a 4 MiB binary file with exact bytes', async () => {
    const [chooser] = await Promise.all([page.waitForFileChooser({timeout: 5000}), button(page, 'Upload', '.webos-files ')]);
    await chooser.accept([pickerPath]); await saved(page, path.basename(pickerPath));
  });
  await check('External OS-file drop saves a 4 MiB binary file with exact bytes', async () => {
    const session = await page.createCDPSession(), bounds = await (await page.$('.webos-files-browser')).boundingBox();
    const data = {items: [], files: [dropPath], dragOperationsMask: 1}, x = bounds.x + bounds.width / 2, y = bounds.y + bounds.height - 40;
    for (const type of ['dragEnter', 'dragOver', 'drop']) await session.send('Input.dispatchDragEvent', {type, x, y, data});
    await saved(page, path.basename(dropPath)); await session.detach();
  });
  if (checks.every(c => c.status === 'PASS')) {
    await check('A late picker cancellation cannot overwrite a completed upload result', async () => {
      const before = await page.$eval('.webos-files-status', n => n.textContent);
      await page.$eval('.webos-files input[type=file]', input => input.dispatchEvent(new Event('cancel', {bubbles: true})));
      assert.equal(await page.$eval('.webos-files-status', n => n.textContent), before);
    });
    await check('Selecting an existing name reports the conflict and preserves its bytes', async () => {
      const [chooser] = await Promise.all([page.waitForFileChooser(), button(page, 'Upload', '.webos-files ')]);
      await chooser.accept([pickerPath]);
      await page.waitForFunction(() => /exists|conflict/i.test(document.querySelector('.webos-files-status')?.textContent));
      await saved(page, path.basename(pickerPath));
    });
    await check('Cancelling the picker permits the next upload attempt', async () => {
      const [chooser] = await Promise.all([page.waitForFileChooser(), button(page, 'Upload', '.webos-files ')]);
      await chooser.cancel(); await page.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent === 'Upload cancelled.');
      const [again] = await Promise.all([page.waitForFileChooser(), button(page, 'Upload', '.webos-files ')]);
      await again.cancel();
    });
    await check('Navigation while a picker is open refuses an upload to a different folder', async () => {
      const [chooser] = await Promise.all([page.waitForFileChooser(), button(page, 'Upload', '.webos-files ')]);
      await page.evaluate(async () => { const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView; await view.execute('list', {path: 'Documents'}); });
      await chooser.accept([dropPath]);
      await page.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('destination folder changed'));
      const state = await page.evaluate(async () => { const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView; const state = await view.inspect(); await view.execute('list', {path: ''}); return state; });
      assert.equal(state.directory, 'Documents'); assert.equal(state.entries.length, 0);
    });
    await check('Fresh browser context retrieves both account uploads', async () => {
      const context = await browser.createBrowserContext(), other = await context.newPage(); other.setDefaultTimeout(15000);
      await login(other, false); await saved(other, path.basename(pickerPath)); await saved(other, path.basename(dropPath)); await context.close();
    });
    await check('The My files breadcrumb returns from Documents to the account root', async () => {
      const navigate = directory => page.evaluate(async directory => {
        const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView;
        await view.execute('list', {path: directory});
      }, directory);
      try {
        await navigate('Documents');
        await page.waitForFunction(() => [...document.querySelectorAll('.webos-files-browser button')].some(n => n.textContent.trim() === 'My files' && !n.disabled));
        await button(page, 'My files', '.webos-files-browser ');
        await page.waitForFunction(async () => {
          const view = [...document.querySelectorAll('.window')].find(n => n.querySelector('.webos-files')).appView;
          const state = await view.inspect(); return state.directory === '' && !state.busy;
        });
      } finally { await navigate(''); }
    });
  }
  await page.screenshot({path: path.join(output, 'files-upload.png')});
  // The deliberate duplicate-name test returns HTTP409; retain its console
  // message without classifying an expected domain refusal as a UI failure.
  const unexpectedConsoleErrors = consoleErrors.filter(text => !text.includes('the server responded with a status of 409'));
  const report = {status: checks.every(c => c.status === 'PASS') && !errors.length && !unexpectedConsoleErrors.length ? 'PASS' : 'FAIL', checks, pageErrors: errors, consoleErrors, unexpectedConsoleErrors, gatewayResponses: responses,
    payload: {bytes: bytes.length, sha256: expected, mediaDecoding: false},
    scope: 'Actual toolbar file chooser and browser-protocol external file drop; server-backed byte/hash verification. No physical OS drag or media decoding claim.'};
  await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({status: report.status, checks: checks.map(c => ({name: c.name, status: c.status, error: c.error, visibleStatus: c.visibleStatus})), output}));
  assert.equal(report.status, 'PASS');
} finally { await browser?.close(); }
