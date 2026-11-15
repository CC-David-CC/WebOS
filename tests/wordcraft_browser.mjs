/** Real assembled first-slice browser proof. Delegated-agent and production-user gates remain separate. */
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {createInterface} from 'node:readline';
import {randomBytes} from 'node:crypto';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';
const hostedOrigin = process.env.WEBOS_TEST_ORIGIN;
assert(!hostedOrigin || hostedOrigin === 'https://ksu.codes', 'Only the user-designated ksu.codes test target is allowed.');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'), output = process.env.WEBOS_TEST_OUTPUT && path.resolve(process.env.WEBOS_TEST_OUTPUT), python = process.env.WEBOS_TEST_PYTHON, site = process.env.WEBOS_WORDCRAFT_SITE;
assert(output && python && (hostedOrigin || site) && output !== root && !output.startsWith(root + path.sep), 'Set new external WEBOS_TEST_OUTPUT, WEBOS_TEST_PYTHON and verified WEBOS_WORDCRAFT_SITE.');
await mkdir(output, {mode: 0o700}); const publicRoot = path.join(output, 'public');
const built = hostedOrigin ? {status: 0} : spawnSync(process.execPath, [path.join(root, 'scripts/build_development.mjs'), publicRoot, '--wordcraft', site], {cwd: root, encoding: 'utf8'}); assert.equal(built.status, 0, built.stderr);
const fixture = spawnSync(python, ['-c', `import sys,zipfile
with zipfile.ZipFile(sys.argv[1],'x',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
 z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
 z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>WebOS integration baseline.</w:t></w:r></w:p><w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>')
`, path.join(output, 'Integration.docx')], {encoding: 'utf8'}); assert.equal(fixture.status, 0, fixture.stderr);
const server = hostedOrigin ? null : spawn(python, ['-u', path.join(root, 'scripts/run_development.py'), '--public-root', publicRoot, '--private-root', path.join(output, 'state'), '--port', '0'], {stdio: ['ignore', 'pipe', 'pipe']});
let browser; const errors = [], requests = [], diagnostics = [], serverErrors = [], report = {scope: 'Real assembled Login/Desktop/Files/WordCraft with synthetic account persistence; not delegated agents or hosted deployment', status: 'FAIL'};
server?.stderr.on('data', data => serverErrors.push(data));
try {
 const origin = hostedOrigin || await new Promise((resolve, reject) => { const timer = setTimeout(() => reject(Error('Development startup timed out.')), 15000); createInterface({input: server.stdout}).once('line', line => {clearTimeout(timer); resolve(JSON.parse(line).origin)}); server.once('exit', () => {clearTimeout(timer); reject(Error('Development startup failed.'))}); server.once('error', reject); });
 report.origin = origin;
 browser = await puppeteer.launch({executablePath: process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'], userDataDir: path.join(output, 'browser-profile')});
 const username = 'test' + randomBytes(6).toString('hex'), password = randomBytes(16).toString('base64url');
 async function context(register = false) {
   const c = await browser.createBrowserContext(), p = await c.newPage(); p.setDefaultTimeout(120000); await p.setViewport({width: 1440, height: 1000});
   p.on('console', message => { const text = message.text(); if (['error', 'warn'].includes(message.type()) && /WebGL|WebAssembly|CompileError|RuntimeError|GPU|context lost|memory/i.test(text)) diagnostics.push({kind:'console',type:message.type(),text:text.slice(0,1000)}); });
   p.on('requestfailed', request => diagnostics.push({kind:'requestfailed',path:new URL(request.url()).pathname,error:request.failure()?.errorText}));
   p.on('response', response => { const pathname = new URL(response.url()).pathname; if (pathname.endsWith('.wasm')) diagnostics.push({kind:'wasm-response',status:response.status(),path:pathname,time:Date.now()}); });
   p.on('pageerror', error => errors.push(error.message)); p.on('request', request => requests.push(new URL(request.url()).pathname)); await p.goto(origin, {waitUntil: 'networkidle0'}); await p.waitForSelector('.login-gate[data-phase=ready]');
   if (register) await p.click('.login-toggle'); await p.type('[name=username]', username); await p.type('[name=password]', password); if (register) await p.type('[name=confirmation]', password); await p.click('[type=submit]'); await p.waitForSelector('.webos-desktop'); return {c, p};
 }
 async function launch(p, app) { await p.click('[aria-label=Applications]'); await p.click('[data-app-id=' + app + ']'); }
 async function files(p) { await launch(p, 'files'); await p.waitForSelector('.webos-files-browser'); await p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Showing account files')); }
 async function openDocument(p, name = 'Integration.docx') {
   const selector = '.webos-files-browser [title=' + JSON.stringify(name) + ']'; await p.waitForSelector(selector); await p.bringToFront(); await p.click(selector, {count: 2});
   await p.waitForSelector('.webos-wordcraft iframe'); const handle = await p.$('.webos-wordcraft iframe'), frame = await handle.contentFrame();
   await frame.waitForFunction(() => window.wordcraft?.uiInspect, {timeout: 120000});
   await p.waitForFunction(() => document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('Opened account file:'), {timeout: 120000});
   return frame;
 }
 const inspect = frame => frame.evaluate(() => window.wordcraft.uiInspect());
 const text = frame => frame.evaluate(async () => JSON.stringify(await window.wordcraft.docInspect({text: true})));
 const command = (frame, name, args = {}) => frame.evaluate(async (name, args) => { const state = await window.wordcraft.uiInspect(); return window.wordcraft.request('engine.execute', {command: name, params: args, doc: state.document}); }, name, args);
 async function waitSaved(p, frame) {
   await p.waitForFunction(() => document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('Saved to your account:'), {timeout: 120000});
   await frame.waitForFunction(async () => { const state = await window.wordcraft.uiInspect(); return !state.dirty && state.pendingSaves === 0; });
 }
 const first = await context(true); await files(first.p); await (await first.p.$('input[type=file]')).uploadFile(path.join(output, 'Integration.docx'));
 await first.p.waitForFunction(() => document.querySelector('.webos-files-status')?.textContent.includes('Saved to your account: Integration.docx'));
 const a = await openDocument(first.p); assert((await text(a)).includes('WebOS integration baseline.'));
 const second = await context(); await files(second.p); const b = await openDocument(second.p); assert((await text(b)).includes('WebOS integration baseline.'));
 await command(a, 'text.insert', {text: ' Programmatic live edit '}); assert((await text(a)).includes('Programmatic live edit'));
 await command(a, 'edit.undo'); assert(!(await text(a)).includes('Programmatic live edit')); await command(a, 'edit.redo');
 // Ordinary browser pointer/keyboard input edits the same native document inspected above.
 await a.waitForFunction(async () => (await window.wordcraft.uiInspect()).pages.length > 0);
 const state = await inspect(a), box = await (await a.$('#wordcraft_canvas')).boundingBox(); assert(box && state.pages[0]);
 await first.p.bringToFront(); await first.p.mouse.click(box.x + state.pages[0][0] + 110, box.y + state.pages[0][1] + 110); await first.p.keyboard.down('Control'); await first.p.keyboard.press('End'); await first.p.keyboard.up('Control'); await first.p.keyboard.type(' Human keyboard edit ');
 await a.waitForFunction(async () => JSON.stringify(await window.wordcraft.docInspect({text: true})).includes('Human keyboard edit'));
 await first.p.keyboard.down('Control'); await first.p.keyboard.press('s'); await first.p.keyboard.up('Control'); await waitSaved(first.p, a);
 assert((await text(a)).includes('Programmatic live edit'));
 // Stale browser still has the original exact saved revision: its overwrite must fail.
 await command(b, 'text.insert', {text: ' Stale overwrite must not win '}); await command(b, 'file.save');
 await second.p.waitForFunction(() => { const value = document.querySelector('.webos-wordcraft-status')?.textContent || ''; return value && !value.startsWith('Saving') && !value.startsWith('Opened') && !value.startsWith('Saved to'); });
 await b.waitForFunction(async () => { const state = await window.wordcraft.uiInspect(); return state.dirty && state.pendingSaves === 0; });
 const third = await context(); await files(third.p); const c = await openDocument(third.p); const durable = await text(c); assert(durable.includes('Human keyboard edit') && durable.includes('Programmatic live edit')); assert(!durable.includes('Stale overwrite must not win'));
 // Files is a view. Closing it must not revoke the editor's Storage service.
 await first.p.click('.webos-window[aria-label=Files] [aria-label=Close]'); await first.p.waitForFunction(() => !document.querySelector('.webos-files'));
 await command(a, 'text.insert', {text: ' Save after closing Files '}); await command(a, 'file.save'); await waitSaved(first.p, a);
 await command(a, 'text.insert', {text: ' Copy-only change '}); await command(a, 'file.saveAs', {path: 'Copy.docx'}); await waitSaved(first.p, a);
 assert((await inspect(a)).documents.some(document => document.path === 'Copy.docx'));
 await command(a, 'file.exportPdf'); await first.p.waitForFunction(() => document.querySelector('.webos-wordcraft-status')?.textContent.includes('Copy.pdf'));
 await a.waitForFunction(async () => (await window.wordcraft.uiInspect()).pendingSaves === 0); assert((await inspect(a)).documents.some(document => document.path === 'Copy.docx'));
 // Cancel close preserves the stale live engine; failed Save from close must preserve it too.
 await second.p.click('.webos-window[aria-label=WordCraft] [aria-label=Close]'); await second.p.waitForSelector('.webos-wordcraft-close');
 await second.p.evaluate(() => [...document.querySelectorAll('.webos-wordcraft-close button')].find(button => button.textContent === 'Cancel').click()); assert(await second.p.$('.webos-wordcraft iframe'));
 await second.p.click('.webos-window[aria-label=WordCraft] [aria-label=Close]'); await second.p.waitForSelector('.webos-wordcraft-close');
 await second.p.evaluate(() => [...document.querySelectorAll('.webos-wordcraft-close button')].find(button => button.textContent === 'Save').click());
 await second.p.waitForFunction(() => document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('The editor stays open:')); assert(await second.p.$('.webos-wordcraft iframe'));
 await first.p.screenshot({path: path.join(output, 'assembled-wordcraft.png')});
 assert(!requests.some(name => /v86|\/vm\/|terminal/.test(name))); assert.deepEqual(errors, []);
 Object.assign(report, {status: 'PASS', realBrowserContexts: 3, actualWasmEngine: true, importedAccountDOCX: true, browserKeyboardAndNativeCommandsShareDocument: true, nativeUndoRedo: true,
   humanSaveDurablyReopenedInCleanContext: true, staleSaveRejectedAndPreservesEdits: true, filesCloseDoesNotStopEditorSave: true, saveAsAndPdfKeepDistinctIdentities: true,
   cancelledCloseAndFailedSaveKeepEditor: true, noGuestRequests: true, pageErrors: 0});
} catch (error) { report.error = {name: error.name, message: error.message}; report.pageErrors = errors; report.diagnostics = diagnostics; if(browser){let i=0;for(const p of await browser.pages())await p.screenshot({path:path.join(output,'failure-'+i+++'.png')}).catch(()=>{});} throw error; }
finally { if (browser) await browser.close(); if (server) { server.kill('SIGTERM'); await new Promise(resolve => {if (server.exitCode !== null || server.signalCode) resolve(); else server.once('exit', resolve)}); } await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n'); await writeFile(path.join(output, 'server-errors.log'), Buffer.concat(serverErrors)); await writeFile(path.join(output, 'diagnostics.json'), JSON.stringify({pageErrors:errors, events:diagnostics},null,2)+'\n'); }
console.log(JSON.stringify(report));
