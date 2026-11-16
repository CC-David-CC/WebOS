// Real WASM regression: an explicit document target must not follow focus.
// Usage: node tests/deckcraft_document_target_browser.mjs PUBLIC_ROOT RESULT_JSON
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
  observed.first = await frame.evaluate(() => window.deckcraft.docInspect());
  await frame.evaluate(() => window.deckcraft.execute('file.new', {}));
  observed.activeBefore = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.notEqual(observed.activeBefore.documentId, observed.first.documentId);
  observed.dispatch = await frame.evaluate(documentId => window.deckcraft.request('engine.execute', {
    documentId, command:'shape.insert', params:{preset:'rect',rect:[100,100,200,100],text:'Must not land in another document'},
  }).then(value => ({rejected:false,value}),error => ({rejected:true,error:String(error)})), observed.first.documentId);
  observed.activeAfter = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.equal(observed.dispatch.rejected, true, 'A stale explicit document target must not edit the currently focused document');
  assert.equal(observed.activeAfter.documentId, observed.activeBefore.documentId);
  assert.equal(observed.activeAfter.revision, observed.activeBefore.revision);
  assert.deepEqual(observed.activeAfter.slides, observed.activeBefore.slides);
  const active = observed.activeAfter.documentId;
  for (const documentId of ['', null, 7, 'not-an-id', active+'0', 'x'.repeat(4096)]) {
    const result = await frame.evaluate(documentId => window.deckcraft.request('document.inspect', {documentId}).then(() => ({rejected:false}),() => ({rejected:true})), documentId);
    assert.equal(result.rejected, true, 'Malformed or nonexistent explicit targets are rejected');
  }
  const current = await frame.evaluate(documentId => window.deckcraft.request('document.inspect', {documentId}), active);
  assert.equal(current.documentId, active);
  await frame.evaluate(documentId => window.deckcraft.request('engine.execute', {documentId,command:'shape.insert',params:{preset:'rect',rect:[100,100,200,100],text:'Exact target'}}), active);
  observed.targetedEdit = await frame.evaluate(() => window.deckcraft.docInspect());
  assert.notEqual(observed.targetedEdit.revision, observed.activeBefore.revision);
  const inspected = await frame.evaluate(() => window.deckcraft.uiInspect());
  observed.documents = inspected.documents;
  assert.equal(inspected.documentTargeting, 'active-precondition-v1');
  assert.equal(inspected.documentId, active);
  assert.ok(inspected.documents.some(d => d.documentId === active && d.revision === observed.targetedEdit.revision));
  assert.ok(inspected.documents.some(d => d.documentId === observed.first.documentId));
  assert.equal(inspected.documents.find(d => d.documentId === observed.first.documentId).revision, observed.first.revision, 'Rejected targeting must not mutate the originating document either');
  assert.equal(errors.length,0); assert.equal(external.length,0);
  await page.screenshot({path:path.join(path.dirname(resultPath),'targeted-operation.png')});
  result={status:'pass',observed,errors,external,requests,hostStoredBytes:false,
    scope:'Real native control dispatch stale/malformed target rejection and exact-document execution/inspection; not authenticated agent transport or account storage proof'};

} catch (error) {
  result = { status: 'fail', error: String(error), observed, errors, external, requests, hostStoredBytes: false, hostSentAcknowledgement: !!observed.syntheticAcknowledgementsSent };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await writeFile(resultPath, JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ status: result.status, error: result.error, dirtyAfterDispatch: observed.afterDispatch?.dirty, saveId: observed.save?.id }) + '\n');
}
