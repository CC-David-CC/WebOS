/** Real PhotoCraft WASM and classic Desktop against a disposable signed account server. */
import assert from 'node:assert/strict';
import {createHash, randomBytes} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const origin = process.env.WEBOS_VIEWER_ORIGIN;
const output = process.env.WEBOS_TEST_OUTPUT;
assert(path.isAbsolute(output) && new URL(origin).hostname === '127.0.0.1' && new URL(origin).origin === origin);
const profile = await (await fetch(origin + '/viewer-build.json')).json();
assert.equal(profile.developmentOnly,true);
assert(profile.apps.includes('photocraft'));
await mkdir(output,{mode:0o700});

const options = {timeout:30_000};
const photoView = '.window:has(.webos-photocraft)';
const picker = 'dialog.codi-file-picker[open]';
const prompt = 'dialog.codi-confirm-dialog[open]';
const firstPath = 'Pictures/First.pcraft';
const copyPath = 'Pictures/Copy.pcraft';
const checks = [], errors = [], assets = new Set(), external = [];
const uploadConflicts = [];
const job = name => ({username:'photo'+name+randomBytes(5).toString('hex'),password:randomBytes(12).toString('hex')});
const A = job('a'), B = job('b');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

function pass(check) {
  checks.push(check);
  console.log(JSON.stringify({status:'PASS',check}));
}

async function button(page, selector, label) {
  const handle = await page.waitForFunction((scope,wanted) =>
    [...document.querySelectorAll(scope+' button')].find(node => !node.disabled &&
      [node.getAttribute('aria-label'),(node.querySelector('.row-text')||node).textContent.trim()].includes(wanted)),
  options, selector, label);
  try { await handle.asElement().click(); }
  finally { await handle.dispose(); }
}

async function login(page, account, register) {
  await page.goto(origin,{waitUntil:'networkidle0'});
  await page.waitForSelector('.login-gate');
  if (register) await page.click('.login-toggle');
  await page.type('[aria-label="Username"]',account.username);
  await page.type('[aria-label="Password"]',account.password);
  if (register) await page.type('[aria-label="Confirm password"]',account.password);
  await button(page,'.login-gate',register?'Register':'Sign in');
  await page.waitForFunction(() => !!window.desktopLab?.session && !document.querySelector('.login-gate'),options);
}

async function launch(page, group, name) {
  await page.bringToFront();
  await page.click('.app-menu-button');
  await button(page,'.menu-pane',group);
  await button(page,'.menu-pane',name);
}

async function readyPhoto(page) {
  const selector = photoView + '.focused';
  await page.waitForSelector(selector + ' iframe:not([inert])',{timeout:120_000});
  return page.$eval(selector,element=>element.dataset.window);
}

async function files(page) {
  await launch(page,'System Tools','Files');
  const selector = '.window.focused:has(.webos-files)';
  await page.waitForSelector(selector,options);
  await page.$eval(selector,element=>element.appView.ready);
  return page.$eval(selector,element=>element.dataset.window);
}

function file(page, id, operation, args) {
  return page.$eval('.window[data-window="'+id+'"]',(element,{operation,args})=>
    element.appView.execute(operation,args),{operation,args});
}

async function shortcut(page, id, key, modifiers = ['Control']) {
  const selector = '.window[data-window="'+id+'"]';
  await page.bringToFront();
  const frameElem = await page.waitForSelector(selector + ' iframe:not([inert])',options);
  const frame = await frameElem.contentFrame();
  await frameElem.dispose();
  assert(frame);
  // The native dialog reply is applied on PhotoCraft's next rendering pass.
  await frame.evaluate(async () => {
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const canvas = document.querySelector('canvas#photocraft_canvas');
    canvas.tabIndex=0;
    canvas.focus();
  });
  for (const modifier of modifiers) await page.keyboard.down(modifier);
  try { await page.keyboard.press(key); }
  finally { for (const modifier of [...modifiers].reverse()) await page.keyboard.up(modifier); }
  await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

async function location(page) {
  await page.waitForSelector(picker,options);
  await button(page,picker,'Open folder Pictures');
}

async function destination(page, name) {
  await location(page);
  await button(page,picker,'Use this folder');
  await page.waitForSelector(prompt + ' input',options);
  await page.$eval(prompt + ' input',(element,value)=>{element.value=value;},name);
  await button(page,prompt,'Save');
}

async function bound(page,id,name) {
  const selector = '.window[data-window="'+id+'"] .caption-text';
  await page.waitForFunction((selector,name)=>document.querySelector(selector)?.textContent===name+' — PhotoCraft',options,selector,name);
}

async function download(page, id, resource, artifact) {
  await file(page,id,'list',{path:resource.slice(0,resource.lastIndexOf('/'))});
  const {sha256} = await file(page,id,'snapshot',{path:resource});
  assert.match(sha256,/^[a-f0-9]{64}$/);
  const bytes = Buffer.from(await page.$eval('.window[data-window="'+id+'"]',async (element,{resource,sha256}) => {
    const result = await element.appView.execute('download',{path:resource,expectedRevision:sha256});
    return Array.from(result.data);
  },{resource,sha256}));
  assert.equal(hash(bytes),sha256);
  await writeFile(path.join(output,artifact),bytes);
  return sha256;
}

function layers(artifact) {
  const program = 'import json,sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); d=json.loads(z.read("manifest.json")); print(len(d["document"]["layers"]))';
  return Number(execFileSync('python3',['-c',program,path.join(output,artifact)],{encoding:'utf8'}));
}

async function observe(page) {
  await page.setViewport({width:1550,height:990});
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',event=>{
    const url = event.location().url;
    if (url === origin+'/gateway/upload' && event.text().includes('409 (Conflict)')) return;
    if (event.type()==='error' && url!==origin+'/photocraft/fonts/manifest.txt') errors.push(event.text());
  });
  page.on('response',response=>{
    const url=new URL(response.url());
    if(url.origin===origin && url.pathname.startsWith('/photocraft/') && response.ok())assets.add(url.pathname);
    if(url.origin===origin && url.pathname==='/gateway/upload' && response.status()===409)uploadConflicts.push(url.pathname);
  });
  await page.setRequestInterception(true);
  page.on('request',request=>{
    const url=request.url();
    if(url.startsWith(origin+'/')||url.startsWith('blob:')||url.startsWith('data:'))void request.continue();
    else {external.push(url);void request.abort();}
  });
}

let browser, page;
try {
  browser=await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true, protocolTimeout:180_000, userDataDir:path.join(output,'profile'),
    args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-background-networking']
  });
  page=await browser.newPage();
  await observe(page);
  await login(page,A,true);
  await launch(page,'Graphics','PhotoCraft');
  const id=await readyPhoto(page);
  await shortcut(page,id,'s');
  await destination(page,'First');
  await bound(page,id,'First.pcraft');
  const filesId=await files(page);
  const first=await download(page,filesId,firstPath,'first.pcraft');
  const blankLayers=layers('first.pcraft');
  assert(blankLayers>=1);
  pass('Native keyboard Save confirms a clean blank through signed account storage');

  await file(page,filesId,'open',{path:firstPath});
  assert.equal(await readyPhoto(page),id);
  assert.equal((await page.$$(photoView)).length,1);
  await shortcut(page,id,'o');
  await location(page);
  await button(page,picker,'Choose file First.pcraft');
  assert.equal(await readyPhoto(page),id);
  assert.equal((await page.$$(photoView)).length,1);
  pass('Files Open and native Open activate the same account project window');

  await shortcut(page,id,'s',['Control','Shift']);
  await page.waitForSelector(picker,options);
  await button(page,picker,'Cancel');
  await bound(page,id,'First.pcraft');
  assert.equal(await download(page,filesId,firstPath,'cancelled.pcraft'),first);
  pass('Cancelling Save As preserves the original account binding and bytes');

  await shortcut(page,id,'n',['Control','Shift']);
  await page.keyboard.press('Enter');
  await shortcut(page,id,'s',['Control','Shift']);
  await destination(page,'Copy.pcraft');
  await bound(page,id,'Copy.pcraft');
  const saved=await download(page,filesId,copyPath,'copy.pcraft');
  assert.notEqual(saved,first);
  assert.equal(layers('copy.pcraft'),blankLayers+1);
  assert.equal(await download(page,filesId,firstPath,'original.pcraft'),first);
  pass('Native layer editing survives Save As and leaves the original account project intact');

  await shortcut(page,id,'s',['Control','Shift']);
  await destination(page,'First.pcraft');
  await page.waitForFunction(() => [...document.querySelectorAll('.webos-photocraft [role="status"]')]
    .some(element=>/changed|exists|conflict/i.test(element.textContent)),options);
  await bound(page,id,'Copy.pcraft');
  assert.equal(await download(page,filesId,firstPath,'collision-original.pcraft'),first);
  assert.equal(await download(page,filesId,copyPath,'collision-copy.pcraft'),saved);
  assert.deepEqual(uploadConflicts,['/gateway/upload']);
  pass('A create-only Save As collision preserves both account files and the confirmed binding');

  await shortcut(page,id,'o');
  await location(page);
  await button(page,picker,'Choose file First.pcraft');
  await page.waitForFunction(selector=>document.querySelectorAll(selector).length===2,{timeout:120_000},photoView);
  const firstId=await readyPhoto(page);
  assert.notEqual(firstId,id);
  await bound(page,firstId,'First.pcraft');
  await bound(page,id,'Copy.pcraft');
  pass('Native Open gives a different project an independent Desktop window');

  const fresh=await browser.createBrowserContext();
  const reopened=await fresh.newPage();
  await observe(reopened);
  await login(reopened,A,false);
  const freshFiles=await files(reopened);
  await file(reopened,freshFiles,'list',{path:'Pictures'});
  await file(reopened,freshFiles,'open',{path:copyPath});
  await bound(reopened,await readyPhoto(reopened),'Copy.pcraft');
  assert.equal(await download(reopened,freshFiles,copyPath,'reopened.pcraft'),saved);
  pass('The same account retrieves identical layered project bytes in a fresh browser context');

  const other=await browser.createBrowserContext();
  const outsider=await other.newPage();
  await observe(outsider);
  await login(outsider,B,true);
  const outsiderFiles=await files(outsider);
  await file(outsider,outsiderFiles,'list',{path:'Pictures'});
  await assert.rejects(file(outsider,outsiderFiles,'snapshot',{path:copyPath}));
  pass('A separate account cannot resolve the first account project');
  assert.deepEqual(external,[]);
  assert.deepEqual(errors,[]);
  assert([...assets].some(url=>url.endsWith('.mjs')));
  assert([...assets].some(url=>url.includes('/app/snippets/')));
  await reopened.screenshot({path:path.join(output,'reopened.png')});
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,errors,external,assets:[...assets]},null,2)+'\n');
} catch (error) {
  await writeFile(path.join(output,'failure.json'),JSON.stringify({error:error.stack,checks,errors,external,assets:[...assets]},null,2)+'\n');
  await page?.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
  throw error;
} finally {
  await browser?.close();
}
