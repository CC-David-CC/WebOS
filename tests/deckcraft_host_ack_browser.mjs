// Real WASM regression: dispatching bytes to a host is not a confirmed save.
// Usage: node tests/deckcraft_host_ack_browser.mjs PUBLIC_ROOT RESULT_JSON
import http from 'node:http';
import { readFile, realpath, writeFile } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const [publicArgument, resultPath] = process.argv.slice(2);
if (!publicArgument || !resultPath) throw Error('PUBLIC_ROOT and RESULT_JSON required');
const publicRoot = await realpath(publicArgument);
const fixture = `<!doctype html><meta charset="utf-8"><title>Disposable host fixture</title>
<style>body{margin:0}iframe{width:100vw;height:100vh;border:0}</style>
<iframe id="app" src="/?host=parent&blank&webgl"></iframe><script>
window.hostEvents=[];
window.addEventListener('message', event => {
  const frame=document.getElementById('app');
  if(event.origin!==location.origin || event.source!==frame.contentWindow) return;
  const data=event.data;
  if(!data || typeof data.type!=='string') return;
  if(data.type==='deckcraft:ready') frame.contentWindow.postMessage({type:'deckcraft:host',version:'1'},location.origin);
  window.hostEvents.push({type:data.type,id:data.id??null,name:data.name??null,saveAs:data.saveAs??null,bytes:data.bytes?.byteLength??0});
  // Deliberately neither store the document nor send a saved acknowledgement.
});</script>`;
const requests = [], errors = [], external = [];
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.wasm': 'application/wasm', '.ico': 'image/x-icon' };
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://127.0.0.1');
    if (url.pathname === '/__host__') {
      response.writeHead(200, { 'content-type': 'text/html' }); response.end(fixture); return;
    }
    if (url.pathname === '/favicon.ico') { response.writeHead(204); response.end(); return; }
    const file = await realpath(path.join(publicRoot, decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname)));
    if (!file.startsWith(publicRoot + '/')) throw Error('Outside public root');
    const bytes = await readFile(file);
    requests.push({ path: url.pathname, status: 200, bytes: bytes.length });
    response.writeHead(200, { 'content-type': mime[path.extname(file)] || 'application/octet-stream' }); response.end(bytes);
  } catch {
    requests.push({ path: request.url, status: 404 }); response.writeHead(404); response.end();
  }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser, result, observed = {};
try {
  browser = await puppeteer.launch({
    executablePath: process.env.CHROMIUM_PATH || '/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless: true, protocolTimeout: 180000,
    args: ['--no-sandbox', '--disable-gpu-sandbox', '--disable-dev-shm-usage', '--use-gl=angle',
      '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-background-networking', '--no-first-run'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  page.on('pageerror', error => errors.push(error.message));
  await page.setRequestInterception(true);
  page.on('request', request => {
    const url = request.url();
    if (url.startsWith(origin + '/') || url.startsWith('blob:') || url.startsWith('data:')) request.continue();
    else { external.push(url); request.abort(); }
  });
  await page.goto(origin + '/__host__', { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForFunction(() => window.hostEvents.some(e => e.type === 'deckcraft:ready'), { timeout: 180000 });
  const frame = page.frames().find(frame => frame.url().startsWith(origin + '/?host=parent'));
  assert.ok(frame);
  await frame.evaluate(() => window.deckcraft.execute('shape.insert', {
    preset: 'roundRect', rect: [100, 100, 360, 120], text: 'Unconfirmed save regression',
  }));
  observed.before = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.equal(observed.before.dirty, true);
  // Observe the document while Save is in flight, whether the API returns pending
  // immediately or resolves its promise only when the save settles.
  await frame.evaluate(() => {
    window.__saveObservation = { state: 'pending' };
    window.deckcraft.execute('file.save', {}).then(
      value => { window.__saveObservation = { state: 'resolved', value }; },
      error => { window.__saveObservation = { state: 'rejected', error: String(error) }; },
    );
  });
  await page.waitForFunction(() => window.hostEvents.some(e => e.type === 'deckcraft:save'), { timeout: 30000 });
  observed.afterDispatch = await frame.evaluate(() => window.deckcraft.docInspect());
  observed.saveResult = await frame.evaluate(() => window.__saveObservation);
  observed.events = await page.evaluate(() => window.hostEvents);
  observed.save = observed.events.find(e => e.type === 'deckcraft:save');
  assert.ok(observed.save.bytes > 0);
  assert.equal(errors.length, 0);
  assert.equal(external.length, 0);
  assert.equal(observed.afterDispatch.dirty, true, 'Posting bytes without durable acknowledgement must retain unsaved changes');
  assert.equal(typeof observed.save.id, 'string', 'A save needs a correlation identity before acknowledgement');
  assert.ok(observed.save.id.length > 0);
  await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.screenshot({ path: path.join(path.dirname(resultPath), 'pending-save.png') });
  const sendAck = async id => {
    await page.evaluate(id => document.getElementById('app').contentWindow.postMessage({ type: 'deckcraft:saved', id }, location.origin), id);
    observed.syntheticAcknowledgementsSent = (observed.syntheticAcknowledgementsSent || 0) + 1;
    await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  };
  await sendAck('wrong-save-id');
  assert.equal((await frame.evaluate(() => window.deckcraft.docInspect())).dirty, true);
  await sendAck(observed.save.id);
  await frame.waitForFunction(async () => !(await window.deckcraft.docInspect()).dirty, { timeout: 30000, polling: 100 });
  observed.confirmed = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.equal(observed.confirmed.documentId, observed.before.documentId);
  assert.equal(typeof observed.confirmed.path, 'string');
  await page.screenshot({ path: path.join(path.dirname(resultPath), 'confirmed-save.png') });
  await frame.evaluate(() => window.deckcraft.execute('shape.insert', { preset: 'rect', rect: [450, 100, 100, 100], text: 'Later edit' }));
  await sendAck(observed.save.id);
  assert.equal((await frame.evaluate(() => window.deckcraft.docInspect())).dirty, true, 'duplicate acknowledgement cannot confirm a later edit');
  await frame.evaluate(() => window.deckcraft.execute('file.save', {}));
  await page.waitForFunction(() => window.hostEvents.filter(event => event.type === 'deckcraft:save').length === 2);
  const second = await page.evaluate(() => window.hostEvents.filter(event => event.type === 'deckcraft:save').at(-1));
  assert.notEqual(second.id, observed.save.id);
  await frame.evaluate(() => window.deckcraft.execute('shape.insert', { preset: 'rect', rect: [450, 250, 100, 100], text: 'Edit after dispatch' }));
  const later = await frame.evaluate(() => window.deckcraft.docInspect());
  await sendAck(second.id);
  await frame.waitForFunction(async revision => (await window.deckcraft.docInspect()).revision !== revision, { timeout: 30000, polling: 100 }, later.revision);
  observed.afterLaterAck = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.equal(observed.afterLaterAck.dirty, true, 'later edits remain unsaved');
  await frame.evaluate(() => window.deckcraft.execute('edit.undo', {}));
  observed.undoToSaved = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.equal(observed.undoToSaved.dirty, false, 'undo returns to the exact acknowledged snapshot');
  await frame.evaluate(() => window.deckcraft.execute('shape.insert', { preset: 'rect', rect: [450, 400, 100, 100], text: 'Origin A' }));
  await frame.evaluate(() => window.deckcraft.execute('file.save', {}));
  await page.waitForFunction(() => window.hostEvents.filter(event => event.type === 'deckcraft:save').length === 3);
  const third = await page.evaluate(() => window.hostEvents.filter(event => event.type === 'deckcraft:save').at(-1));
  await frame.evaluate(() => window.deckcraft.execute('file.new', {}));
  const other = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.notEqual(other.documentId, observed.before.documentId);
  await sendAck(third.id);
  await frame.waitForFunction(async firstPath => (await window.deckcraft.uiInspect()).documents.some(doc => doc.path === firstPath && !doc.dirty), { timeout: 30000, polling: 100 }, observed.confirmed.path);
  observed.afterSwitchAck = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.equal(observed.afterSwitchAck.documentId, other.documentId);
  assert.equal(observed.afterSwitchAck.path, null);
  assert.equal(errors.length, 0);
  assert.equal(external.length, 0);
  result = { status: 'pass', observed, errors, external, requests, hostStoredBytes: false,
    syntheticHostAcknowledgements: observed.syntheticAcknowledgementsSent,
    scope: 'Real WASM pending/correlated/wrong/duplicate/newer-edit/document-switch protocol tests with synthetic host acknowledgements; no account persistence proof' };

} catch (error) {
  result = { status: 'fail', error: String(error), observed, errors, external, requests, hostStoredBytes: false, hostSentAcknowledgement: !!observed.syntheticAcknowledgementsSent };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await writeFile(resultPath, JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ status: result.status, error: result.error, dirtyAfterDispatch: observed.afterDispatch?.dirty, saveId: observed.save?.id }) + '\n');
}
