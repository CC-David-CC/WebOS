// Real WASM regression: dispatching bytes to a host is not a confirmed save.
// Usage: node tests/deckcraft_host_failure_browser.mjs PUBLIC_ROOT RESULT_JSON
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
  window.hostEvents.push({type:data.type,id:data.id??null,name:data.name??null,saveAs:data.saveAs??null,documentId:data.documentId??null,revision:data.revision??null,operation:data.operation??null,documentSave:data.documentSave??null,bytes:data.bytes?.byteLength??0});
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
  const ui = () => frame.evaluate(() => window.deckcraft.uiInspect());
  const doc = () => frame.evaluate(() => window.deckcraft.docInspect());
  const send = async data => {
    if (data.type === 'deckcraft:saved') observed.syntheticAcknowledgementsSent = (observed.syntheticAcknowledgementsSent || 0) + 1;
    await page.evaluate(data => document.getElementById('app').contentWindow.postMessage(data, location.origin), data);
    await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  };
  const waitSettled = id => frame.waitForFunction(async id => !(await window.deckcraft.uiInspect()).pendingSaves[id], {timeout: 30000, polling: 100}, id);
  let saves = 0;
  const save = async () => {
    await frame.evaluate(() => window.deckcraft.execute('file.save', {}));
    saves++;
    await page.waitForFunction(n => window.hostEvents.filter(e => e.type === 'deckcraft:save').length === n, {timeout: 30000}, saves);
    const event = await page.evaluate(() => window.hostEvents.filter(e => e.type === 'deckcraft:save').at(-1));
    const pending = (await ui()).pendingSaves[event.id];
    assert.ok(pending);
    assert.equal(event.documentId, pending.documentId, 'wire targets captured document');
    assert.equal(event.revision, pending.revision, 'wire targets captured editor revision');
    assert.equal(event.documentSave, true);
    assert.equal(event.operation, event.saveAs ? 'file.saveAs' : 'file.save');
    assert.ok(event.bytes > 0);
    return event;
  };
  await frame.evaluate(() => window.deckcraft.execute('shape.insert', {preset:'rect',rect:[100,100,200,100],text:'Failure protocol'}));
  observed.before = await doc();
  observed.failures = [];
  for (const outcome of ['failed', 'cancelled', 'conflict']) {
    const event = await save();
    assert.equal(event.saveAs, true);
    if (observed.failures.length === 0) {
      await send({type:'deckcraft:save-failed',id:event.id,error:'missing outcome'});
      await send({type:'deckcraft:save-failed',id:event.id,outcome:'timeout',error:'unrecognized'});
      await send({type:'deckcraft:save-failed',id:event.id,outcome:'failed',error:'x'.repeat(1025)});
      await send({type:'deckcraft:save-failed',id:'wrong-id',outcome:'failed',error:'wrong request'});
      assert.equal((await ui()).pendingSaves[event.id].state, 'pending', 'malformed and wrong-id replies do not settle a save');
    }
    await send({type:'deckcraft:save-failed',id:event.id,outcome,error:'Disposable '+outcome});
    await waitSettled(event.id);
    const after = await doc();
    assert.equal(after.dirty, true);
    assert.equal(after.path, null);
    assert.equal(after.documentId, observed.before.documentId);
    observed.failures.push({outcome,event,after});
  }
  const unknown = await save();
  await send({type:'deckcraft:save-failed',id:unknown.id,outcome:'unknown',error:'Confirmation lost'});
  await frame.waitForFunction(async id => (await window.deckcraft.uiInspect()).pendingSaves[id]?.state === 'unknown', {timeout:30000,polling:100}, unknown.id);
  observed.unknown = await ui();
  assert.equal((await doc()).dirty, true);
  const retry = await frame.evaluate(() => window.deckcraft.execute('file.save', {}).then(() => ({rejected:false}), () => ({rejected:true})));
  assert.equal(retry.rejected, true, 'unknown outcome blocks blind repetition');
  assert.equal(await page.evaluate(() => window.hostEvents.filter(e => e.type === 'deckcraft:save').length), saves);
  await frame.evaluate(() => window.deckcraft.execute('shape.insert', {preset:'rect',rect:[350,100,100,100],text:'Newer edit'}));
  await send({type:'deckcraft:saved',id:unknown.id});
  await waitSettled(unknown.id);
  observed.afterLateConfirmation = await doc();
  assert.equal(observed.afterLateConfirmation.dirty, true, 'confirmation must retain newer edits');
  assert.equal(typeof observed.afterLateConfirmation.path, 'string');
  const final = await save();
  assert.equal(final.saveAs, false);
  assert.equal(final.operation, 'file.save');
  await send({type:'deckcraft:saved',id:final.id});
  await waitSettled(final.id);
  assert.equal((await doc()).dirty, false);
  await page.screenshot({path:path.join(path.dirname(resultPath),'failure-recovery.png')});
  assert.equal(errors.length, 0);
  assert.equal(external.length, 0);
  observed.events = await page.evaluate(() => window.hostEvents);
  result = {status:'pass', observed, errors, external, requests, hostStoredBytes:false,
    scope:'Real WASM captured identity, malformed replies, failed/cancelled/conflict/unknown, blocked retry and late-confirmation tests using synthetic host responses; no account persistence proof'};

} catch (error) {
  result = { status: 'fail', error: String(error), observed, errors, external, requests, hostStoredBytes: false, hostSentAcknowledgement: !!observed.syntheticAcknowledgementsSent };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await writeFile(resultPath, JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ status: result.status, error: result.error, dirtyAfterDispatch: observed.afterDispatch?.dirty, saveId: observed.save?.id }) + '\n');
}
