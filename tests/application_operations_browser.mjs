/** Real Desktop/Help domain routing with synthetic in-page capabilities, not server agent authentication. */
import assert from 'node:assert/strict';
import {build} from 'esbuild';
import puppeteer from 'puppeteer-core';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = process.env.WEBOS_TEST_OUTPUT && path.resolve(process.env.WEBOS_TEST_OUTPUT);
assert(output && output !== root && !output.startsWith(root + path.sep), 'Provide a new external test directory.');
await mkdir(output, {mode: 0o700}); const publicRoot = path.join(output, 'public'); await mkdir(publicRoot, {mode: 0o700});
const entry = `
import {createDesktopController,mount as mountDesktop} from '@webos/desktop';
import {mount as mountHelp} from '@webos/help';
const human=Object.freeze({}), reader=Object.freeze({}), operator=Object.freeze({});let granted=null;
function authorize(caller,request){
 if(caller===human)return true;
 if(![reader,operator].includes(caller)||request.instanceId!==granted)return false;
 if(request.operation==='application.inspect')return true;
 if(request.operation==='application.execute')return request.request.operation==='inspect'||(caller===operator&&request.request.operation==='select');
 return request.operation==='inspect'||(caller===operator&&request.operation==='select'&&request.section==='documents');
}
const desktop=createDesktopController({sessionId:'fixture-session',accountId:'synthetic-account',authorize,
 applications:[{id:'help',title:'Help',width:620,height:500,mount:host=>mountHelp({...host,authority:human,authorize})}]});
const view=mountDesktop({desktop,authority:human});document.getElementById('root').append(view.element);
const state=desktop.inspect(),base={desktopId:state.desktopId,sessionId:state.sessionId};
const target=id=>({...base,instanceId:id,resourceId:'view:'+id});
const command=(id,operation,section)=>({...target(id),request:{instanceId:id,sessionId:state.sessionId,resource:null,operation,args:{section}}});
window.operations=Object.freeze({
 async open(){const result=await desktop.execute({...base,operation:'open',args:{appId:'help'}},human);if(!granted)granted=result.windowId;return result.windowId;},
 inspect:id=>desktop.inspectApplication(target(id),reader),
 read:id=>desktop.executeApplication(command(id,'inspect'),reader),
 select:(id,section)=>desktop.executeApplication(command(id,'select',section),operator),
 deniedSelect:(id,section)=>desktop.executeApplication(command(id,'select',section),reader),
 close:id=>desktop.execute({...base,operation:'close',args:{windowId:id}},human)
});
`;
await build({stdin: {contents: entry, resolveDir: root}, bundle: true, format: 'esm', outfile: path.join(publicRoot, 'client.mjs'), logLevel: 'silent'});
await writeFile(path.join(publicRoot, 'index.html'), '<!doctype html><html><head><link rel="icon" href="data:,"><link rel="stylesheet" href="/client.css"><style>html,body,#root{width:100%;height:100%;margin:0}</style></head><body><div id="root"></div><script type="module" src="/client.mjs"></script></body></html>');
const allowed = new Map([['/', ['index.html', 'text/html']], ['/client.mjs', ['client.mjs', 'text/javascript']], ['/client.css', ['client.css', 'text/css']]]);
const server = createServer(async (request, response) => {
  try {const record = allowed.get(request.url); if (!record || request.method !== 'GET') {response.writeHead(404); response.end(); return;} response.writeHead(200, {'Content-Type': record[1]}); response.end(await readFile(path.join(publicRoot, record[0])));}
  catch {response.writeHead(500); response.end();}
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = 'http://127.0.0.1:' + server.address().port, errors = [], report = {scope: 'Actual Desktop/Help public interfaces with synthetic caller capabilities; server delegation remains unqualified', status: 'FAIL', origin}; let browser;
try {
  browser = await puppeteer.launch({executablePath: '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'], userDataDir: path.join(output, 'browser-profile')});
  const page = await browser.newPage(); await page.setViewport({width: 1440, height: 1000}); page.on('pageerror', error => errors.push(error.message)); await page.goto(origin, {waitUntil: 'networkidle0'});
  const first = await page.evaluate(() => window.operations.open()); await page.waitForSelector('.webos-window[data-window-id="' + first + '"][data-phase=ready]');
  const initial = await page.evaluate(id => window.operations.inspect(id), first); assert.equal(initial.selected, 'desktop');
  await page.click('.webos-help button[data-topic=files]');
  await page.waitForFunction(() => document.querySelector('.webos-help article')?.dataset.topic === 'files');
  const read = await page.evaluate(id => window.operations.read(id), first); assert.equal(read.selected, 'files'); assert.equal(read.topic.id, 'files');
  await assert.rejects(page.evaluate(id => window.operations.deniedSelect(id, 'documents'), first), /denied/i);
  await assert.rejects(page.evaluate(id => window.operations.select(id, 'desktop'), first), /denied/i);
  assert.equal(await page.$eval('.webos-help article', node => node.dataset.topic), 'files');
  await page.evaluate(id => window.operations.select(id, 'documents'), first);
  assert.equal(await page.$eval('.webos-help article', node => node.dataset.topic), 'documents');
  const second = await page.evaluate(() => window.operations.open()); await page.waitForSelector('.webos-window[data-window-id="' + second + '"][data-phase=ready]');
  await assert.rejects(page.evaluate(id => window.operations.inspect(id), second), /denied/i);
  await page.evaluate(id => window.operations.close(id), first);
  await assert.rejects(page.evaluate(id => window.operations.inspect(id), first), /exists|unavailable|changed/i);
  assert.equal(await page.$eval('.webos-help article', node => node.dataset.topic), 'desktop');
  await page.screenshot({path: path.join(output, 'live-view-routing.png')}); assert.deepEqual(errors, []);
  Object.assign(report, {status: 'PASS', mouseAndProgrammaticCommandsShareState: true, readerCannotMutate: true, grantCannotCrossWindow: true, closedViewRefused: true, pageErrors: 0});
} catch (error) {report.error = {name: error.name, message: error.message}; report.pageErrors = errors; throw error;}
finally {await browser?.close(); await new Promise(resolve => server.close(resolve)); await writeFile(path.join(output, 'result.json'), JSON.stringify(report, null, 2) + '\n');}
console.log(JSON.stringify(report));
