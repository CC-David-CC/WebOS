// Actual WASM view adapter test with explicitly fake Storage.
// Usage: node tests/deckcraft_adapter_browser.mjs PUBLIC_ROOT RESULT_JSON ADAPTER_ROOT
import http from 'node:http';
import { readFile, realpath, writeFile } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const [publicArgument, resultPath, adapterArgument] = process.argv.slice(2);
const adapterRoot = await realpath(adapterArgument);
if (!publicArgument || !resultPath) throw Error('PUBLIC_ROOT and RESULT_JSON required');
const publicRoot = await realpath(publicArgument);
const fixture = `<!doctype html><meta charset="utf-8"><title>DeckCraft adapter transport qualification</title>
<style>body{margin:0}#views{display:flex;height:92vh}#views>div{width:50%;height:100%}</style><div id="views"></div>
<script type="module">
import {mount} from '/__adapter__/index.mjs';
const human=Object.freeze({}), views=new Map(), records=new Map();let sequence=0,writes=0,readGate=null,releaseRead=null,readWaiting=false;
const files={check(){},async read(path){if(readGate){readWaiting=true;await readGate;readWaiting=false}const entry=records.get(path);if(!entry)throw Error('Missing test file');return {data:entry.bytes.slice(),sha256:entry.sha256}},async write(path,blob,previous){writes++;
 const existing=records.get(path);if(previous===null?!!existing:existing?.sha256!==previous)throw Object.assign(Error('Conflict'),{status:409});
 const bytes=new Uint8Array(await blob.arrayBuffer()),sha256=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(b=>b.toString(16).padStart(2,'0')).join('');records.set(path,{bytes,sha256});return {sha256};}};
window.harness={
 create(resource=null,aborted=false){const id='test-view-'+(++sequence),abort=new AbortController();if(aborted)abort.abort();const view=mount({instanceId:id,sessionId:'test-session',resource,files,authority:human,authorize:c=>c===human,url:'/index.html?webgl',signal:abort.signal});if(view instanceof Promise)throw Error('Mount must be synchronous');views.set(id,view);document.getElementById('views').append(view.element);return id},
 ready:id=>views.get(id).ready,inspect:id=>views.get(id).inspect(),
 async run(id,command,args={}){const view=views.get(id),state=await view.inspect(),doc=state.native.documentId,binding=state.accountFiles.bindings.find(x=>x.documentId===doc);return view.execute({instanceId:id,sessionId:'test-session',documentId:doc,resourceId:binding?.path||'draft:'+doc,command,args},human)},
 async denied(id,missing=false){const view=views.get(id),state=await view.inspect();try{await view.execute({instanceId:id,sessionId:'test-session',documentId:state.native.documentId,resourceId:'draft:'+state.native.documentId,command:'shape.insert',args:{preset:'rect',rect:[1,1,10,10]}},missing?undefined:Object.freeze({}));return false}catch{return true}},
 close:id=>views.get(id).requestClose(),dispose:id=>views.get(id).dispose(),
 pauseRead(){readGate=new Promise(resolve=>releaseRead=resolve)},resumeRead(){readGate=null;releaseRead()},readWaiting:()=>readWaiting,writes:()=>writes,
 nativeReady:id=>typeof views.get(id).element.querySelector('iframe')?.contentWindow?.deckcraft?.execute==='function',
 native:(id,command,args={})=>views.get(id).element.querySelector('iframe').contentWindow.deckcraft.execute(command,args),
 nativeUi:id=>views.get(id).element.querySelector('iframe').contentWindow.deckcraft.uiInspect(),
 status:id=>views.get(id).element.querySelector('[role=status]').textContent,
 records:()=>[...records].map(([path,value])=>({path,sha256:value.sha256,bytes:value.bytes.length})),
};window.harnessReady=true;
</script>`;
const requests = [], errors = [], external = [];
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.wasm': 'application/wasm', '.ico': 'image/x-icon' };
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://127.0.0.1');
    if (url.pathname === '/__host__') {
      response.writeHead(200, { 'content-type': 'text/html' }); response.end(fixture); return;
    }
    if (url.pathname === '/favicon.ico') { response.writeHead(204); response.end(); return; }
    const adapter = url.pathname.startsWith('/__adapter__/');
    const root = adapter ? adapterRoot : publicRoot;
    const relative = adapter ? url.pathname.slice('/__adapter__'.length) : (url.pathname === '/' ? '/index.html' : url.pathname);
    const file = await realpath(path.join(root, decodeURIComponent(relative)));
    if (!file.startsWith(root + '/')) throw Error('Outside public root');
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
  await page.waitForFunction(()=>window.harnessReady,{timeout:30000});
  const create=resource=>page.evaluate(resource=>window.harness.create(resource),resource);
  const ready=id=>page.evaluate(id=>window.harness.ready(id),id);
  const inspect=id=>page.evaluate(id=>window.harness.inspect(id),id);
  const run=(id,command,args={})=>page.evaluate(({id,command,args})=>window.harness.run(id,command,args),{id,command,args});
  const first=await create(null);await ready(first);observed.initial=await inspect(first);
  assert.equal(observed.initial.phase,'ready');assert.equal(observed.initial.native.documents.length,1);
  assert.equal(await page.evaluate(id=>window.harness.denied(id),first),true);
  assert.equal(await page.evaluate(id=>window.harness.denied(id,true),first),true);
  await run(first,'shape.insert',{preset:'roundRect',rect:[100,100,360,120],text:'Adapter round trip'});
  observed.edited=await inspect(first);assert.equal(observed.edited.dirty,true);
  observed.saved=await run(first,'file.save');assert.equal(observed.saved.committed,true);
  await page.waitForFunction(async id=>!(await window.harness.inspect(id)).dirty,{timeout:30000},first);
  observed.confirmed=await inspect(first);assert.equal(observed.confirmed.accountFiles.bindings[0].sha256,observed.saved.sha256);
  const resource={path:observed.saved.path,sha256:observed.saved.sha256};
  const second=await create(resource);await ready(second);observed.reopened=await inspect(second);
  assert.equal(observed.reopened.accountFiles.bindings[0].path,resource.path);
  assert.notEqual(observed.reopened.native.documentId,observed.confirmed.native.documentId);
  assert.equal(observed.reopened.native.documents.length,1);assert.equal(observed.reopened.dirty,false);
  const count=observed.reopened.native.documents.length;
  await run(second,'shape.insert',{preset:'rect',rect:[500,100,100,100],text:'Second view edit'});
  assert.equal((await inspect(first)).dirty,false,'Independent first view must remain clean');
  await page.evaluate(id=>{window.closeResult=undefined;window.harness.close(id).then(value=>window.closeResult=value)},second);
  await page.waitForSelector('dialog[open]');
  await page.evaluate(()=>[...document.querySelectorAll('dialog button')].find(b=>b.textContent==='Cancel').click());
  await page.waitForFunction(()=>window.closeResult===false);
  assert.equal((await inspect(second)).dirty,true);
  await page.evaluate(id=>{window.closeResult=undefined;window.harness.close(id).then(value=>window.closeResult=value)},second);
  await page.waitForSelector('dialog[open]');
  await page.evaluate(()=>[...document.querySelectorAll('dialog button')].find(b=>b.textContent==='Save').click());
  await page.waitForFunction(()=>window.closeResult===true,{timeout:30000});
  observed.savedOnClose=await inspect(second);assert.equal(observed.savedOnClose.dirty,false);
  assert.equal(observed.savedOnClose.native.documents.length,count);
  assert.notEqual(observed.savedOnClose.accountFiles.bindings[0].sha256,resource.sha256);
  observed.records=await page.evaluate(()=>window.harness.records());assert.equal(observed.records.length,1);
  assert.equal(await page.evaluate(id=>window.harness.close(id),first),true);
  const latest=observed.savedOnClose.accountFiles.bindings[0];
  await page.evaluate(()=>window.harness.pauseRead());
  const paused=await create({path:latest.path,sha256:latest.sha256});
  await page.waitForFunction(id=>window.harness.nativeReady(id)&&window.harness.readWaiting(),{timeout:30000},paused);
  const writesBefore=await page.evaluate(()=>window.harness.writes());
  assert.equal((await inspect(paused)).phase,'loading');
  await page.evaluate(id=>window.harness.native(id,'file.save'),paused);
  await page.waitForFunction(async id=>!Object.keys((await window.harness.nativeUi(id)).pendingSaves).length,{timeout:30000},paused);
  observed.startup={writesBefore,writesAfter:await page.evaluate(()=>window.harness.writes()),status:await page.evaluate(id=>window.harness.status(id),paused)};
  assert.equal(observed.startup.writesAfter,writesBefore,'Save during initial account read must not dispatch a Storage write');
  await page.evaluate(()=>window.harness.resumeRead());await ready(paused);
  assert.equal((await inspect(paused)).accountFiles.bindings[0].path,latest.path);
  await page.evaluate(id=>window.harness.dispose(id),paused);
  const aborted=await page.evaluate(()=>window.harness.create(null,true));
  assert.equal((await inspect(aborted)).phase,'disposed');
  assert.equal(await page.evaluate(async id=>{try{await window.harness.ready(id);return false}catch{return true}},aborted),true);
  await page.evaluate(id=>window.harness.dispose(id),aborted);
  await page.screenshot({path:path.join(path.dirname(resultPath),'adapter-views.png')});
  assert.equal(errors.length,0);assert.equal(external.length,0);
  await page.evaluate(ids=>ids.forEach(id=>window.harness.dispose(id)),[first,second,aborted]);
  result={status:'pass',observed,errors,external,requests,scope:'Actual DeckCraft WASM plus new synchronous adapter with in-memory fake Storage; transport/lifecycle/domain qualification only, not real account persistence or agent authorization'};

} catch (error) {
  result = { status: 'fail', error: String(error), observed, errors, external, requests, hostStoredBytes: false };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
  await writeFile(resultPath, JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ status: result.status, error: result.error, openedDocumentId: observed.opened?.documentId, pairedOpenCount: observed.pairedOpenEvents?.length }) + '\n');
}
