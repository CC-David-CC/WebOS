/** Real desktop hosting of the independently owned Help view; disposable local account. */
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {createInterface} from 'node:readline';
import {randomBytes} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = process.env.WEBOS_TEST_OUTPUT && path.resolve(process.env.WEBOS_TEST_OUTPUT), python = process.env.WEBOS_TEST_PYTHON, wordcraftSite = process.env.WEBOS_WORDCRAFT_SITE;
assert(output && python && output !== root && !output.startsWith(root + path.sep), 'Set a new external output and explicit backend Python.');
await mkdir(output, {mode: 0o700}); const publicRoot = path.join(output, 'public');
const built = spawnSync(process.execPath, [path.join(root, 'scripts/build_development.mjs'), publicRoot, ...(wordcraftSite ? ['--wordcraft', wordcraftSite] : [])], {cwd: root, encoding: 'utf8'}); assert.equal(built.status, 0, built.stderr);
const server = spawn(python, ['-u', path.join(root, 'scripts/run_development.py'), '--public-root', publicRoot, '--private-root', path.join(output, 'state'), '--port', '0'], {stdio: ['ignore', 'pipe', 'pipe']});
const report = {scope: 'Actual Login/Desktop/Help UI; local synthetic account; not delegated agents or hosted deployment', status: 'FAIL'}, errors = [], serverErrors = [];
server.stderr.on('data', data => serverErrors.push(data)); let browser;
try {
  const origin = await new Promise((resolve, reject) => { const timer = setTimeout(() => reject(Error('Server startup timed out.')), 15000); createInterface({input: server.stdout}).once('line', line => {clearTimeout(timer); resolve(JSON.parse(line).origin);}); server.once('error', reject); server.once('exit', () => reject(Error('Server stopped.'))); });
  report.origin = origin;
  browser = await puppeteer.launch({executablePath: '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'], userDataDir: path.join(output, 'browser-profile')});
  const page = await browser.newPage(); page.setDefaultTimeout(30000); await page.setViewport({width: 1440, height: 1000}); page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin, {waitUntil: 'networkidle0'}); await page.waitForSelector('.login-gate[data-phase=ready]');
  const username = 'help' + randomBytes(6).toString('hex'), password = randomBytes(18).toString('base64url');
  await page.click('.login-toggle'); await page.type('[name=username]', username); await page.type('[name=password]', password); await page.type('[name=confirmation]', password); await page.click('[type=submit]'); await page.waitForSelector('.webos-desktop');
  const requests = []; page.on('request', request => requests.push(new URL(request.url()).pathname));
  async function launch() {
    const expected = (await page.$$('.webos-window[aria-label=Help]')).length + 1;
    await page.click('[aria-label=Applications]'); await page.click('[data-app-id=help]');
    await page.waitForFunction(expected => { const windows = [...document.querySelectorAll('.webos-window[aria-label=Help]')]; return windows.length === expected && windows.every(window => window.dataset.phase === 'ready'); }, {}, expected);
    return page.$$eval('.webos-window[aria-label=Help]', windows => windows.map(window => window.dataset.windowId));
  }
  const selector = id => '.webos-window[data-window-id="' + id + '"]';
  const selected = id => page.$eval(selector(id) + ' .webos-help article', node => node.dataset.topic);
  async function focus(id) { await page.click('.webos-task[data-window-id="' + id + '"]'); }
  const [first] = await launch(); const ids = await launch(), second = ids.find(id => id !== first); assert(second);
  await focus(first); await page.click(selector(first) + ' .webos-help button[data-topic=files]');
  await page.waitForFunction(selector => document.querySelector(selector + ' article')?.dataset.topic === 'files', {}, selector(first));
  await page.keyboard.press('Tab'); await page.keyboard.press('Enter');
  await page.waitForFunction(selector => document.querySelector(selector + ' article')?.dataset.topic === 'documents', {}, selector(first));
  assert.equal(await selected(second), 'desktop');
  await focus(second); await page.click(selector(second) + ' .webos-help button[data-topic=files]');
  await page.waitForFunction(selector => document.querySelector(selector + ' article')?.dataset.topic === 'files', {}, selector(second));
  assert.equal(await selected(first), 'documents');
  await focus(first); await page.screenshot({path: path.join(output, 'help-documents.png')});
  await page.click(selector(first) + ' [aria-label=Close]'); await page.waitForFunction(selector => !document.querySelector(selector), {}, selector(first));
  assert.equal(await selected(second), 'files');
  const reopened = (await launch()).find(id => id !== second); assert(reopened); assert.equal(await selected(reopened), 'desktop'); assert.equal(await selected(second), 'files');
  assert.deepEqual(errors, []); assert(!requests.some(name => name.startsWith('/gateway') || /v86|\/vm\//.test(name)));
  Object.assign(report, {status: 'PASS', mouseAndKeyboardSelection: true, twoIndependentInstances: true, closeRetainsOtherInstance: true, reopenStartsWithDesktopTopic: true, noFileOrGuestRequests: true, pageErrors: 0});
} catch (error) {
  report.error = {name: error.name, message: error.message}; report.pageErrors = errors;
  if (browser) for (const [index, page] of (await browser.pages()).entries()) await page.screenshot({path: path.join(output, 'failure-' + index + '.png')}).catch(() => {});
  throw error;
} finally {
  await browser?.close(); server.kill('SIGTERM'); await new Promise(resolve => {if (server.exitCode !== null || server.signalCode) resolve(); else server.once('exit', resolve);});
  await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n'); await writeFile(path.join(output, 'server-errors.log'), Buffer.concat(serverErrors));
}
console.log(JSON.stringify(report));
