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
const injectedUploadLoss = new WeakSet();
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

async function shortcut(page, id, key, modifiers = ['Control'], {closing = false} = {}) {
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
  if (!closing) await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

function photoWindow(id) {
  return photoView + '[data-window="'+id+'"]';
}

async function closePhoto(page, id) {
  await button(page,photoWindow(id),'Close');
}

async function draftPersisted(page, path, revision, typeDraft = false) {
  await page.waitForFunction(async ({path,revision,typeDraft}) => {
    const name = 'webos-photocraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db => db.name === name)) return false;
    const db = await new Promise((resolve,reject) => {
      const request = indexedDB.open(name);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    try {
      const records = await new Promise((resolve,reject) => {
        const request = db.transaction('drafts').objectStore('drafts').getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
      for (const row of records) {
        if (row.path !== path || row.revision !== revision || !(row.bytes instanceof Blob) || row.bytes.size < 8) continue;
        if (!typeDraft || await row.bytes.slice(0,8).text() === 'PCDRAFT1') return true;
      }
      return false;
    } finally { db.close(); }
  },{...options,polling:250},{path,revision,typeDraft});
}

async function reloadRecovered(page, id, text) {
  await page.bringToFront();
  const handleDialog = dialog => void dialog.accept();
  page.on('dialog', handleDialog);
  try {
    await page.reload({waitUntil:'networkidle0'});
    await page.waitForSelector(photoWindow(id)+' iframe:not([inert])',{timeout:120_000});
    await page.waitForFunction((selector,text)=>document.querySelector(selector+' [role="status"]')?.textContent.includes(text),
      options,photoWindow(id),text);
  } finally { page.off('dialog', handleDialog); }
}

async function loseCloseSaveReceipt(page, id) {
  const connection = await page.createCDPSession();
  let responses = 0, finish, fail, timer;
  const lost = new Promise((resolve, reject) => { finish = resolve; fail = reject; });
  const expiry = new Promise((_, reject) => {
    timer = setTimeout(() => reject(Error('No committed PhotoCraft response was intercepted.')),30_000);
  });
  connection.on('Fetch.requestPaused', event => {
    if (event.request.method === 'POST' && event.responseStatusCode >= 200 && event.responseStatusCode < 300) {
      responses++;
      injectedUploadLoss.add(page);
      void connection.send('Fetch.failRequest',{requestId:event.requestId,errorReason:'Failed'}).then(finish,fail);
    } else {
      void connection.send('Fetch.continueResponse',{requestId:event.requestId}).catch(fail);
    }
  });
  try {
    await connection.send('Fetch.enable',{patterns:[{urlPattern:origin+'/gateway/upload',requestStage:'Response'}]});
    await Promise.all([Promise.race([lost,expiry]),shortcut(page,id,'Enter',[],{closing:true})]);
    await page.waitForFunction(selector=>document.querySelector(selector+' [role="status"]')?.textContent.includes('unconfirmed'),
      options,photoWindow(id));
    await closePhoto(page,id);
    await page.waitForFunction(()=>document.querySelector('#feedback')?.textContent.includes('Finish the active PhotoCraft operation'),options);
    assert.equal(responses,1);
  } finally {
    clearTimeout(timer);
    await connection.send('Fetch.disable');
    await connection.detach();
  }
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

function editedText(artifact) {
  const program = 'import json,sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); d=json.loads(z.read("manifest.json")); print(json.dumps([l["content"]["text"] for l in d["document"]["layers"] if "text" in l["content"]]))';
  return JSON.parse(execFileSync('python3',['-c',program,path.join(output,artifact)],{encoding:'utf8'}));
}

async function observe(page) {
  await page.setViewport({width:1550,height:990});
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',event=>{
    const url = event.location().url;
    if (url === origin+'/gateway/upload' && event.text().includes('409 (Conflict)')) return;
    if (injectedUploadLoss.has(page) && url === origin+'/gateway/upload' && event.text().includes('net::ERR_FAILED')) return;
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

  await closePhoto(page,firstId);
  await page.waitForSelector(photoWindow(firstId),{...options,hidden:true});
  await bound(page,id,'Copy.pcraft');
  pass('The Desktop closes a clean PhotoCraft project without a prompt');

  await file(page,filesId,'open',{path:copyPath});
  assert.equal(await readyPhoto(page),id);
  await shortcut(page,id,'n', ['Control','Shift']);
  await page.keyboard.press('Enter');
  await closePhoto(page,id);
  await shortcut(page,id,'c',[]);
  assert.equal(await download(page,filesId,copyPath,'close-cancel.pcraft'),saved);
  await bound(page,id,'Copy.pcraft');
  pass('Cancelling native Close keeps the edited account project open');

  await closePhoto(page,id);
  await shortcut(page,id,'Enter',[],{closing:true});
  await page.waitForSelector(photoWindow(id),{...options,hidden:true});
  const savedOnClose=await download(page,filesId,copyPath,'close-saved.pcraft');
  assert.notEqual(savedOnClose,saved);
  assert.equal(layers('close-saved.pcraft'),blankLayers+2);
  pass('Save from the Close prompt persists the native edit before the Desktop removes the window');

  await file(page,filesId,'open',{path:copyPath});
  const updatedId=await readyPhoto(page);
  assert.notEqual(updatedId,id);
  await shortcut(page,updatedId,'n',['Control','Shift']);
  await page.keyboard.press('Enter');
  await closePhoto(page,updatedId);
  await shortcut(page,updatedId,'n',[],{closing:true});
  await page.waitForSelector(photoWindow(updatedId),{...options,hidden:true});
  assert.equal(await download(page,filesId,copyPath,'close-discard.pcraft'),savedOnClose);
  pass('Discard closes a dirty project without replacing the saved account file');

  await launch(page,'Graphics','PhotoCraft');
  const blankId=await readyPhoto(page);
  await shortcut(page,blankId,'n');
  await shortcut(page,blankId,'Enter',[]);
  await page.waitForFunction(selector=>document.querySelectorAll(selector).length===2,options,photoView);
  const newId=await readyPhoto(page);
  assert.notEqual(newId,blankId);
  assert.equal((await page.$$(photoView)).length,2);
  await closePhoto(page,newId);
  await page.waitForSelector(photoWindow(newId),{...options,hidden:true});
  assert(await page.$(photoWindow(blankId)));
  pass('Native New creates an independent window and an untouched blank closes quietly');

  const fresh=await browser.createBrowserContext();
  const reopened=await fresh.newPage();
  await observe(reopened);
  await login(reopened,A,false);
  const freshFiles=await files(reopened);
  await file(reopened,freshFiles,'list',{path:'Pictures'});
  await file(reopened,freshFiles,'open',{path:copyPath});
  const reopenedId=await readyPhoto(reopened);
  await bound(reopened,reopenedId,'Copy.pcraft');
  assert.equal(await download(reopened,freshFiles,copyPath,'reopened.pcraft'),savedOnClose);
  pass('The same account retrieves identical layered project bytes in a fresh browser context');

  const other=await browser.createBrowserContext();
  const outsider=await other.newPage();
  await observe(outsider);
  await login(outsider,B,true);
  const outsiderFiles=await files(outsider);
  await file(outsider,outsiderFiles,'list',{path:'Pictures'});
  await assert.rejects(file(outsider,outsiderFiles,'snapshot',{path:copyPath}));
  pass('A separate account cannot resolve the first account project');

  await shortcut(reopened,reopenedId,'n',['Control','Shift']);
  await reopened.keyboard.press('Enter');
  await closePhoto(reopened,reopenedId);
  await loseCloseSaveReceipt(reopened,reopenedId);
  await bound(reopened,reopenedId,'Copy.pcraft');
  assert.notEqual(await download(reopened,freshFiles,copyPath,'close-uncertain.pcraft'),savedOnClose);
  assert.equal(layers('close-uncertain.pcraft'),blankLayers+3);
  pass('A lost response after a committed Save leaves Close cancelled and the write unreplayed');

  await draftPersisted(reopened,copyPath,savedOnClose);
  const changedBase=await download(reopened,freshFiles,copyPath,'changed-recovery-base.pcraft');
  assert.notEqual(changedBase,savedOnClose);
  await reloadRecovered(reopened,reopenedId,'Recovered an unsaved copy');
  await bound(reopened,reopenedId,'Untitled');
  await shortcut(reopened,reopenedId,'s');
  await destination(reopened,'Conflict recovery');
  await bound(reopened,reopenedId,'Conflict recovery.pcraft');
  assert.equal(await download(reopened,freshFiles,copyPath,'changed-base-preserved.pcraft'),changedBase);
  await download(reopened,freshFiles,'Pictures/Conflict recovery.pcraft','recovered-copy.pcraft');
  assert.equal(layers('recovered-copy.pcraft'),blankLayers+3);
  pass('A changed server revision restores the local PhotoCraft draft as a separately saved copy');

  await shortcut(page,blankId,'n',['Control','Shift']);
  await page.keyboard.press('Enter');
  await draftPersisted(page,null,null);
  await reloadRecovered(page,blankId,'Recovered unsaved changes');
  await shortcut(page,blankId,'s');
  await destination(page,'Untitled recovery');
  await bound(page,blankId,'Untitled recovery.pcraft');
  const untitledPath='Pictures/Untitled recovery.pcraft';
  const typeBase=await download(page,filesId,untitledPath,'recovered-untitled.pcraft');
  assert.equal(layers('recovered-untitled.pcraft'),blankLayers+1);
  pass('An untitled locally journaled layer survives refresh and an explicit account save');

  await shortcut(page,blankId,'t',[]);
  const editor=await page.$(photoWindow(blankId)+' iframe');
  const canvas=await (await editor.contentFrame()).$('canvas#photocraft_canvas');
  const box=await canvas.boundingBox();
  assert(box);
  await page.mouse.click(box.x+Math.max(65,(box.width-230)/2),box.y+box.height*0.56);
  await page.keyboard.type('Recovered typed title',{delay:20});
  await draftPersisted(page,untitledPath,typeBase,true);
  assert.equal(await download(page,filesId,untitledPath,'uncommitted-type.pcraft'),typeBase);
  await reloadRecovered(page,blankId,'Recovered unsaved changes');
  await bound(page,blankId,'Untitled recovery.pcraft');
  await shortcut(page,blankId,'Enter',['Control']);
  await shortcut(page,blankId,'s');
  await page.waitForFunction(({id,base}) => [...window.desktopLab.surfaces.values()].some(desktop =>
    desktop.windows.some(win => String(win.id) === id && win.launchContext?.sha256 && win.launchContext.sha256 !== base)),
  options,{id:blankId,base:typeBase});
  assert.notEqual(await download(page,filesId,untitledPath,'recovered-type.pcraft'),typeBase);
  assert.deepEqual(editedText('recovered-type.pcraft'),['Recovered typed title']);
  pass('Pending native Type content survives refresh and stays editable until explicit commit');

  const autosaveContext=await browser.createBrowserContext();
  const automatic=await autosaveContext.newPage();
  await observe(automatic);
  await login(automatic,A,false);
  const autoFiles=await files(automatic);
  await file(automatic,autoFiles,'list',{path:'Pictures'});
  await file(automatic,autoFiles,'open',{path:untitledPath});
  const autoId=await readyPhoto(automatic);
  const toggle=photoWindow(autoId)+' .webos-photocraft button[aria-pressed]';
  assert.equal(await automatic.$eval(toggle,node=>node.getAttribute('aria-pressed')),'false');
  const writes=[];
  automatic.on('request',request=>{
    if (request.url()===origin+'/gateway/upload' && request.method()==='POST') writes.push(performance.now());
  });
  const boundRevision=()=>automatic.evaluate(id=>[...window.desktopLab.surfaces.values()].flatMap(surface=>surface.windows)
    .find(win=>String(win.id)===id)?.launchContext?.sha256,autoId);
  async function nextAutomaticRevision(base, timeout) {
    await automatic.waitForFunction(({id,base})=>[...window.desktopLab.surfaces.values()].some(desktop=>
      desktop.windows.some(win=>String(win.id)===id && win.launchContext?.sha256 && win.launchContext.sha256!==base)),
    {timeout},{id:autoId,base});
    return boundRevision();
  }
  const originalAuto=await boundRevision();
  await automatic.click(toggle);
  assert.equal(await automatic.$eval(toggle,node=>node.getAttribute('aria-pressed')),'true');
  const firstEdit=performance.now();
  await shortcut(automatic,autoId,'n',['Control','Shift']);
  await automatic.keyboard.press('Enter');
  const firstAuto=await nextAutomaticRevision(originalAuto,45_000);
  assert.equal(writes.length,1);
  assert(writes[0]-firstEdit>=9_800);
  assert.equal(await download(automatic,autoFiles,untitledPath,'first-automatic.pcraft'),firstAuto);
  assert.equal(layers('first-automatic.pcraft'),blankLayers+3);
  pass('Named PhotoCraft AutoSave is opt-in, waits after editing and publishes the confirmed native project');

  await shortcut(automatic,autoId,'n',['Control','Shift']);
  await automatic.keyboard.press('Enter');
  const secondAuto=await nextAutomaticRevision(firstAuto,85_000);
  assert.equal(writes.length,2);
  assert(writes[1]-writes[0]>=59_800);
  assert.equal(await download(automatic,autoFiles,untitledPath,'second-automatic.pcraft'),secondAuto);
  assert.equal(layers('second-automatic.pcraft'),blankLayers+4);
  pass('PhotoCraft spaces successive automatic account writes and preserves each later native layer');
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
