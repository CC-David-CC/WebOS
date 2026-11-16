// Real WASM regression: completed file adoption returns its own native document identity.
// Usage: node tests/deckcraft_correlated_open_browser.mjs PUBLIC_ROOT RESULT_JSON
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
  window.hostEvents.push({type:data.type,id:data.id??null,name:data.name??null,saveAs:data.saveAs??null,openResult:data.openResult??null,sourceRetained:data.sourceRetained??null,documentId:data.documentId??null,revision:data.revision??null,operation:data.operation??null,documentSave:data.documentSave??null,bytes:data.bytes?.byteLength??0});
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
  const inspect = () => frame.evaluate(() => window.deckcraft.docInspect());
  const ui = () => frame.evaluate(() => window.deckcraft.uiInspect());
  const postOpen = async (id,name,encoded) => {
    await page.evaluate(({id,name,encoded}) => {
      const raw=atob(encoded),bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
      document.getElementById('app').contentWindow.postMessage({type:'deckcraft:open',id,name,bytes:bytes.buffer},location.origin,[bytes.buffer]);
    },{id,name,encoded});
  };
  const tick = () => frame.evaluate(() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  observed.before = await inspect();
  const snapshot = await frame.evaluate(() => window.deckcraft.execute('file.saveBytes',{format:'deckcraft'}));
  assert.equal(typeof snapshot.data,'string');
  await postOpen('load-account-1','Account presentation.deckcraft',snapshot.data);
  await frame.waitForFunction(async()=> (await window.deckcraft.docInspect()).path === 'Account presentation.deckcraft',{timeout:30000,polling:100});
  await tick();
  observed.afterOpen = await inspect();
  observed.events = await page.evaluate(()=>window.hostEvents);
  observed.opened = observed.events.find(e=>e.type==='deckcraft:opened'&&e.id==='load-account-1');
  assert.ok(observed.opened,'Opening bytes must return correlated native document identity');
  assert.equal(observed.opened.documentId,observed.afterOpen.documentId);
  assert.equal(observed.opened.revision,observed.afterOpen.revision);
  assert.equal(observed.opened.sourceRetained,true);
  assert.equal(observed.events.find(e=>e.type==='deckcraft:ready').openResult,true);
  assert.equal((await ui()).documents.length,1,'Only the untouched initial host blank is replaced');
  observed.created = await frame.evaluate(()=>window.deckcraft.execute('file.new',{}));
  const later = await inspect();
  assert.equal(observed.created.documentId,later.documentId);
  assert.equal(observed.created.revision,later.revision);
  assert.equal(observed.created.path,null);
  assert.notEqual(later.documentId,observed.opened.documentId);
  assert.ok((await ui()).documents.some(d=>d.documentId===observed.opened.documentId&&d.path==='Account presentation.deckcraft'),'Correlated identity remains the loaded document after focus changes');
  await page.evaluate(encoded => {
    for(const [id,name] of [['load-parallel-a','Parallel A.deckcraft'],['load-parallel-b','Parallel B.deckcraft']]) {
      const raw=atob(encoded),bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
      document.getElementById('app').contentWindow.postMessage({type:'deckcraft:open',id,name,bytes:bytes.buffer},location.origin,[bytes.buffer]);
    }
  },snapshot.data);
  await page.waitForFunction(()=>['load-parallel-a','load-parallel-b'].every(id=>window.hostEvents.some(e=>e.type==='deckcraft:opened'&&e.id===id)),{timeout:30000});
  const pairedEvents=await page.evaluate(()=>window.hostEvents.filter(e=>e.type==='deckcraft:opened'&&e.id.startsWith('load-parallel-')));
  const pairedState=await ui();
  assert.equal(pairedEvents.length,2);
  assert.notEqual(pairedEvents[0].documentId,pairedEvents[1].documentId);
  for(const [id,name] of [['load-parallel-a','Parallel A.deckcraft'],['load-parallel-b','Parallel B.deckcraft']]) {
    const event=pairedEvents.find(e=>e.id===id);
    assert.ok(event&&event.sourceRetained);
    assert.ok(pairedState.documents.some(d=>d.documentId===event.documentId&&d.path===name),'Back-to-back opens retain their own document/resource identity');
  }
  observed.pairedOpenEvents=pairedEvents;
  const outline = Buffer.from('# Imported one\n\n# Imported two\n').toString('base64');
  await postOpen('load-outline-2','Outline.md',outline);
  await frame.waitForFunction(async()=> (await window.deckcraft.docInspect()).slides.length===2,{timeout:30000,polling:100});
  await tick();
  const imported = await inspect();
  observed.outline = (await page.evaluate(()=>window.hostEvents)).find(e=>e.type==='deckcraft:opened'&&e.id==='load-outline-2');
  assert.ok(observed.outline);
  assert.equal(observed.outline.documentId,imported.documentId);
  assert.equal(observed.outline.sourceRetained,false,'Converted input must not become an overwrite of its source');
  assert.equal(imported.path,null);
  const count=(await ui()).documents.length;
  await postOpen('load-bad-3','Broken.deckcraft',Buffer.from([0,1,2]).toString('base64'));
  await page.waitForFunction(()=>window.hostEvents.some(e=>e.type==='deckcraft:failed'&&e.id==='load-bad-3'),{timeout:30000});
  assert.equal((await ui()).documents.length,count);
  observed.events=await page.evaluate(()=>window.hostEvents);
  assert.ok(!observed.events.some(e=>e.type==='deckcraft:opened'&&e.id==='load-bad-3'));
  assert.equal(errors.length,0);assert.equal(external.length,0);
  await page.screenshot({path:path.join(path.dirname(resultPath),'correlated-adoption.png')});
  result={status:'pass',observed,errors,external,requests,hostStoredBytes:false,
    scope:'Real native binary open/result correlation, stable creation identity, startup blank replacement, source retention and failure; no account storage or authenticated agent transport proof'};

} catch (error) {
  result = { status: 'fail', error: String(error), observed, errors, external, requests, hostStoredBytes: false };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await writeFile(resultPath, JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ status: result.status, error: result.error, openedDocumentId: observed.opened?.documentId, pairedOpenCount: observed.pairedOpenEvents?.length }) + '\n');
}
