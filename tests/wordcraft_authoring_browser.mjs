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
const server = hostedOrigin ? null : spawn(python, ['-u', path.join(root, 'scripts/run_development.py'), '--public-root', publicRoot, '--private-root', path.join(output, 'state'), '--port', '0'], {stdio: ['ignore', 'pipe', 'pipe']});
let browser; const errors = [], requests = [], diagnostics = [], serverErrors = [], report = {scope: 'Fresh WordCraft authoring: real engine, formatting and account persistence; local test accounts', status: 'FAIL'};
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
 const first = await context(true); await launch(first.p, 'wordcraft');
 await first.p.waitForSelector('.webos-wordcraft iframe'); const handle = await first.p.$('.webos-wordcraft iframe'), frame = await handle.contentFrame();
 await first.p.waitForFunction(() => document.querySelector('.webos-wordcraft-status')?.textContent.startsWith('New document;'), {timeout:120000});
 await command(frame, 'para.heading1'); await command(frame, 'text.insert', {text:'WebOS authoring heading'});
 await command(frame, 'text.newParagraph'); await command(frame, 'para.normal'); await command(frame, 'text.insert', {text:'A paragraph saved through the shared account storage service.'});
 await command(frame, 'text.newParagraph'); await command(frame, 'para.bullets'); await command(frame, 'text.insert', {text:'First list item'}); await command(frame, 'text.newParagraph'); await command(frame, 'text.insert', {text:'Second list item'});
 async function structure(f) {return f.evaluate(async()=>{const d=await window.wordcraft.docInspect({text:true});return d.blocks.filter(b=>b.type==='paragraph').map(b=>({text:b.text,style:b.style,list:b.list||null}));});}
 const original=await structure(frame); assert.equal(original[0].text,'WebOS authoring heading'); assert.equal(original[0].style,'Heading1'); assert.equal(original[1].style,'Normal'); assert(original[2].list && original[3].list); assert.equal(original[2].text,'First list item'); assert.equal(original[3].text,'Second list item');
 await command(frame,'file.saveAs',{path:'Authored.docx'}); await waitSaved(first.p,frame);
 await first.p.click('.webos-window[aria-label=WordCraft] [aria-label=Close]'); await first.p.waitForFunction(()=>!document.querySelector('.webos-wordcraft'));
 async function openAuthored(p) { await files(p); const selector='.webos-files-browser [title="Documents"]';await p.waitForSelector(selector);await p.bringToFront();await p.click(selector,{count:2});return openDocument(p,'Authored.docx'); }
 const reopened=await openAuthored(first.p); assert.deepEqual(await structure(reopened),original);
 await first.p.reload({waitUntil:'networkidle0'});await first.p.waitForSelector('.login-gate[data-phase=ready]');await first.p.type('[name=username]',username);await first.p.type('[name=password]',password);await first.p.click('[type=submit]');await first.p.waitForSelector('.webos-desktop');
 const reloaded=await openAuthored(first.p);assert.deepEqual(await structure(reloaded),original);
 const second=await context();const remote=await openAuthored(second.p);assert.deepEqual(await structure(remote),original);
 await second.p.screenshot({path:path.join(output,'wordcraft-heading-paragraph-list.png')});assert.deepEqual(errors,[]);assert(!requests.some(name=>/v86|\/vm\/|terminal/.test(name)));
 Object.assign(report,{status:'PASS',createdInActualEngine:true,headingParagraphAndTwoListItems:true,savedToAccount:true,closeAndFilesReopenPreservesFormatting:true,reloadPreservesFormatting:true,secondCleanContextPreservesFormatting:true,noGuestRequests:true,pageErrors:0});
} catch (error) { report.error = {name: error.name, message: error.message}; report.pageErrors = errors; report.diagnostics = diagnostics; if(browser){let i=0;for(const p of await browser.pages())await p.screenshot({path:path.join(output,'failure-'+i+++'.png')}).catch(()=>{});} throw error; }
finally { if (browser) await browser.close(); if (server) { server.kill('SIGTERM'); await new Promise(resolve => {if (server.exitCode !== null || server.signalCode) resolve(); else server.once('exit', resolve)}); } await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n'); await writeFile(path.join(output, 'server-errors.log'), Buffer.concat(serverErrors)); await writeFile(path.join(output, 'diagnostics.json'), JSON.stringify({pageErrors:errors, events:diagnostics},null,2)+'\n'); }
console.log(JSON.stringify(report));
