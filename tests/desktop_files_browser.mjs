/** Actual assembled Login/Desktop/Files UI, actual signed backend; no editor acceptance claim. */
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {createInterface} from 'node:readline';
import {randomBytes} from 'node:crypto';
import {mkdir, writeFile, readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'), output = process.env.WEBOS_TEST_OUTPUT && path.resolve(process.env.WEBOS_TEST_OUTPUT), python = process.env.WEBOS_TEST_PYTHON;
assert(output && python && output !== root && !output.startsWith(root + path.sep), 'Use explicit private external test output and Python.');
await mkdir(output, {mode: 0o700});
const publicRoot = path.join(output, 'public'), built = spawnSync(process.execPath, [path.join(root, 'scripts/build_development.mjs'), publicRoot], {cwd: root, encoding: 'utf8'});
assert.equal(built.status, 0, built.stderr);
const server = spawn(python, ['-u', path.join(root, 'scripts/run_development.py'), '--public-root', publicRoot, '--private-root', path.join(output, 'state'), '--port', '0'], {stdio: ['ignore', 'pipe', 'pipe']});
const errors = [], requests = [], serverErrors = []; server.stderr.on('data', value => serverErrors.push(value));
let browser; const report = {scope: 'Assembled real Login/Desktop/Files UI with signed account storage; WordCraft/agents not qualified', status: 'FAIL'};
try {
 const origin = await new Promise((resolve, reject) => { const timer = setTimeout(() => reject(Error('Server startup timed out.')), 15000); createInterface({input: server.stdout}).once('line', line => {clearTimeout(timer); resolve(JSON.parse(line).origin)}); server.once('exit', () => {clearTimeout(timer); reject(Error('Server startup failed.'))}); server.once('error', reject); });
 browser = await puppeteer.launch({executablePath: process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'], userDataDir: path.join(output, 'browser-profile')});
 async function context() { const c = await browser.createBrowserContext(), p = await c.newPage(); await p.setViewport({width: 1280, height: 900}); p.on('pageerror', error => errors.push(error.message)); p.on('request', request => requests.push(new URL(request.url()).pathname)); await p.goto(origin, {waitUntil: 'networkidle0'}); await p.waitForSelector('.login-gate[data-phase=ready]'); return {c, p}; }
 const name = 'test' + randomBytes(6).toString('hex'), secret = randomBytes(16).toString('base64url');
 async function signin(p, register = false) { if (register) await p.click('.login-toggle'); await p.type('[name=username]', name); await p.type('[name=password]', secret); if (register) await p.type('[name=confirmation]', secret); await p.click('[type=submit]'); await p.waitForSelector('.webos-desktop'); }
 async function openFiles(p) { await p.click('[aria-label=Applications]'); await p.click('[data-app-id=files]'); await p.waitForSelector('.webos-window[data-phase=ready]'); await p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Showing account files')); }
 const first = await context(); await signin(first.p, true);
 async function openCalculator(p) { await p.click('[aria-label=Applications]'); await p.click('[data-app-id=calculator]'); await p.waitForFunction(() => [...document.querySelectorAll('.webos-window')].every(w => w.dataset.phase === 'ready')); }
 await openCalculator(first.p);
 const calculatorOne = await first.p.$eval('.webos-window', el => el.dataset.windowId);
 await first.p.type('.webos-calculator input', '18/3'); await first.p.keyboard.press('Enter');
 await first.p.waitForFunction(() => document.querySelector('.webos-calculator output')?.textContent === '6');
 await openCalculator(first.p);
 const calculatorWindows = await first.p.$$('.webos-window'); assert.equal(calculatorWindows.length, 2);
 const calculatorTwo = await calculatorWindows[1].evaluate(el => el.dataset.windowId);
 const secondCalculator = `.webos-window[data-window-id="${calculatorTwo}"]`;
 await first.p.type(secondCalculator + ' input', '7*8'); await first.p.keyboard.press('Enter');
 await first.p.waitForFunction(sel => document.querySelector(sel + ' output')?.textContent === '56', {}, secondCalculator);
 assert.equal(await first.p.$eval(`.webos-window[data-window-id="${calculatorOne}"] output`, el => el.textContent), '6');
 await first.p.click(`.webos-task[data-window-id="${calculatorOne}"]`);
 await first.p.click(`.webos-window[data-window-id="${calculatorOne}"] [aria-label=Close]`);
 await first.p.waitForFunction(() => document.querySelectorAll('.webos-window').length === 1);
 assert.equal(await first.p.$eval(secondCalculator + ' output', el => el.textContent), '56');
 await first.p.click(secondCalculator + ' [aria-label=Close]');
 await first.p.waitForFunction(() => !document.querySelector('.webos-window'));
 await openFiles(first.p);
 await writeFile(path.join(output, 'migration-proof.txt'), 'Synthetic browser upload to server-backed account storage.\n');
 await (await first.p.$('input[type=file]')).uploadFile(path.join(output, 'migration-proof.txt'));
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Saved to your account: migration-proof.txt'));
 await first.p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('migration-proof.txt'));
 const second = await context(); await signin(second.p); await openFiles(second.p);
 await second.p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('migration-proof.txt'));
 await actionButton(first.p, 'New folder'); await first.p.waitForSelector('.webos-files-dialog input');
 await first.p.type('.webos-files-dialog input', 'acceptance'); await first.p.click('.webos-files-dialog [type=submit]');
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Folder created on the server'));
 await selectFile(first.p, 'migration-proof.txt'); await actionButton(first.p, 'Move'); await first.p.waitForSelector('.webos-files-dialog input');
 await first.p.$eval('.webos-files-dialog input', input => {input.value = ''}); await first.p.type('.webos-files-dialog input', 'acceptance/migration-proof.txt'); await first.p.click('.webos-files-dialog [type=submit]');
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Moved on the server'));
 assert.equal(await first.p.$eval('.webos-files-browser', el => el.innerText.includes('migration-proof.txt')), false);
 async function enterFolder(p, name) { const handle = await p.evaluateHandle(name => [...document.querySelectorAll('.webos-files-browser [title]')].find(el => el.getAttribute('title') === name), name); await handle.asElement().click(); await handle.asElement().click(); await handle.dispose(); await p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('migration-proof.txt')); }
 await enterFolder(first.p, 'acceptance');
 const downloads = path.join(output, 'downloads'); await mkdir(downloads);
 const downloadSession = await first.p.createCDPSession(); await downloadSession.send('Page.setDownloadBehavior', {behavior: 'allow', downloadPath: downloads});
 await selectFile(first.p, 'migration-proof.txt'); await actionButton(first.p, 'Download');
 let downloaded; for (let i = 0; i < 100; i++) { try { downloaded = await readFile(path.join(downloads, 'migration-proof.txt'), 'utf8'); break; } catch (error) { if (error.code !== 'ENOENT') throw error; await new Promise(resolve => setTimeout(resolve, 50)); } }
 assert.equal(downloaded, 'Synthetic browser upload to server-backed account storage.\n'); await downloadSession.detach();
 await second.p.reload({waitUntil: 'networkidle0'}); await second.p.waitForSelector('.login-gate[data-phase=ready]'); await signin(second.p); await openFiles(second.p); await enterFolder(second.p, 'acceptance');
 await selectFile(first.p, 'migration-proof.txt'); await actionButton(first.p, 'Move'); await first.p.waitForSelector('.webos-files-dialog input');
 await first.p.$eval('.webos-files-dialog input', input => {input.value = ''}); await first.p.type('.webos-files-dialog input', 'migration-proof.txt'); await first.p.click('.webos-files-dialog [type=submit]');
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Moved on the server'));
 await first.p.click('[aria-label="Parent folder"]'); await first.p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('migration-proof.txt'));
 await second.p.click('[aria-label="Parent folder"]'); await second.p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('migration-proof.txt'));
 await first.p.click('[aria-label="Workspace 2"]'); assert.equal(await first.p.$eval('.webos-window', el => el.hidden), true);
 await first.p.click('[aria-label="Workspace 1"]'); assert.equal(await first.p.$eval('.webos-window', el => el.hidden), false);
 await first.p.click('[aria-label=Minimize]'); assert.equal(await first.p.$eval('.webos-window', el => el.hidden), true);
 await first.p.click('.webos-task'); assert.equal(await first.p.$eval('.webos-window', el => el.hidden), false);
 async function selectFile(p, name) { await p.evaluate(name => { const el = [...document.querySelectorAll('.webos-files-browser [title]')].find(el => el.getAttribute('title') === name); if (!el) throw Error('File row missing'); el.click(); }, name); }
 async function actionButton(p, name) { await p.evaluate(name => { const button = [...document.querySelectorAll('.webos-files-browser button')].find(el => el.textContent.trim() === name); if (!button || button.disabled) throw Error('Action unavailable: ' + name); button.click(); }, name); }
 await selectFile(first.p, 'migration-proof.txt'); await actionButton(first.p, 'Rename'); await first.p.waitForSelector('.webos-files-dialog input');
 await first.p.$eval('.webos-files-dialog input', input => {input.value = ''}); await first.p.type('.webos-files-dialog input', 'renamed-proof.txt'); await first.p.click('.webos-files-dialog [type=submit]');
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Renamed on the server'));
 await second.p.click('.webos-files-bar button'); await second.p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('renamed-proof.txt'));
 await selectFile(first.p, 'renamed-proof.txt'); await actionButton(first.p, 'Delete'); await first.p.waitForSelector('.webos-files-dialog');
 await first.p.click('.webos-files-dialog [type=button]'); await first.p.waitForFunction(() => !document.querySelector('.webos-files-dialog'));
 assert.equal(await first.p.$eval('.webos-files-browser', el => el.innerText.includes('renamed-proof.txt')), true);
 await actionButton(first.p, 'Delete'); await first.p.waitForSelector('.webos-files-dialog'); await first.p.click('.webos-files-dialog [type=submit]');
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Deleted from your account'));
 await second.p.click('.webos-files-bar button'); await second.p.waitForFunction(() => !document.querySelector('.webos-files-browser')?.innerText.includes('renamed-proof.txt'));
 await (await first.p.$('input[type=file]')).uploadFile(path.join(output, 'migration-proof.txt'));
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Saved to your account: migration-proof.txt'));
 await writeFile(path.join(output, 'uncertain-proof.txt'), 'Synthetic transport interruption, not a confirmed account save.');
 await first.p.setRequestInterception(true); const blockUpload = request => { if (request.url().endsWith('/gateway/upload')) request.abort('failed'); else request.continue(); }; first.p.on('request', blockUpload);
 await (await first.p.$('input[type=file]')).uploadFile(path.join(output, 'uncertain-proof.txt'));
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('server outcome is unknown'));
 first.p.off('request', blockUpload); await first.p.setRequestInterception(false);
 await first.p.click('.webos-files-bar button'); await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Showing account files'));
 await first.p.click('[aria-label=Maximize]'); await first.p.waitForSelector('.webos-window.webos-maximized');
 await first.p.screenshot({path: path.join(output, 'assembled-files.png')});
 await first.p.click('[aria-label=Close]'); await first.p.waitForFunction(() => !document.querySelector('.webos-window'));
 await openFiles(first.p); await first.p.waitForFunction(() => document.querySelector('.webos-files-browser')?.innerText.includes('migration-proof.txt'));
 await first.p.click('.webos-signout'); await first.p.waitForSelector('.login-gate[data-phase=ready]'); assert.equal(await first.p.$('.webos-files'), null);
 assert(!requests.some(value => /v86|\/vm\/|terminal/.test(value))); assert.deepEqual(errors, []);
 Object.assign(report, {status: 'PASS', realBrowserContexts: 2, authenticatedCalculatorInstances: true, folderCreatedOnServer: true, revisionCheckedMove: true, downloadedBytesVerified: true, reloadAndSecondContextRetrieveMovedFile: true, humanUploadConfirmedByServer: true, cleanSecondContextListsUpload: true, windowWorkspaceMinimizeMaximize: true, revisionCheckedRenameAndDelete: true, cancelledDeleteRetainsFile: true, interruptedUploadNeverClaimsSaved: true, closeAndReopenRetainsAccountFiles: true, signoutDisposesViews: true, noGuestRequests: true, pageErrors: 0});
} catch (error) {report.error = {name: error.name, message: error.message}; if (browser) { const pages = await browser.pages(); for (let i=0;i<pages.length;i++) { await pages[i].screenshot({path:path.join(output, 'failure-'+i+'.png')}).catch(()=>{}); } } throw error;}
finally { if (browser) await browser.close(); server.kill('SIGTERM'); await new Promise(resolve => { if (server.exitCode !== null || server.signalCode) resolve(); else server.once('exit', resolve); }); await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n'); await writeFile(path.join(output, 'server-errors.log'), Buffer.concat(serverErrors)); }
console.log(JSON.stringify(report));
