/** Real PhotoCraft WASM and classic Desktop against a disposable signed account server. */
import assert from 'node:assert/strict';
import {createHash, randomBytes} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {mkdir, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {zstdDecompressSync} from 'node:zlib';
import puppeteer from 'puppeteer-core';

const origin = process.env.WEBOS_VIEWER_ORIGIN;
const output = process.env.WEBOS_TEST_OUTPUT;
assert(path.isAbsolute(output) && new URL(origin).hostname === '127.0.0.1' && new URL(origin).origin === origin);
assert.equal((await (await fetch(origin+'/healthz')).json()).scope,'development');
const profile = await (await fetch(origin + '/viewer-build.json')).json();
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

async function endSession(page, decision) {
  await page.bringToFront();
  await page.click('.app-menu-button');
  await button(page,'.menu-pane','End session');
  await button(page,'dialog.webos-photocraft-session[open]',decision);
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
  if (!closing) {
    await page.evaluate(id=>{
      for (const desktop of window.desktopLab.surfaces.values()) {
        const editor = desktop.windows.find(window=>String(window.id)===String(id));
        if (!editor) continue;
        desktop.activateWindow(editor);
        return;
      }
      throw Error('The PhotoCraft window is unavailable.');
    },id);
  }
  const frameElem = await page.waitForSelector(selector + ' iframe:not([inert])',options);
  const frame = await frameElem.contentFrame();
  await frameElem.dispose();
  assert(frame);
  // The native dialog reply is applied on PhotoCraft's next rendering pass.
  await frame.evaluate(async () => {
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const canvas = document.querySelector('canvas#photocraft_canvas');
    canvas.tabIndex=0;
    canvas.focus({preventScroll:true});
    if (document.activeElement !== canvas) throw Error('The native PhotoCraft canvas did not receive focus.');
  });
  for (const modifier of modifiers) await page.keyboard.down(modifier);
  try { await page.keyboard.press(key); }
  finally { for (const modifier of [...modifiers].reverse()) await page.keyboard.up(modifier); }
  if (!closing) await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

function photoWindow(id) {
  return photoView + '[data-window="'+id+'"]';
}

function autoSaveControl(id) {
  return photoWindow(id) + ' .webos-photocraft button[aria-pressed]';
}

async function profileState(page, id) {
  return page.$eval(photoWindow(id),async node => {
    const frame = node.querySelector('iframe');
    const profile = new URL(frame.src).searchParams.get('profile');
    const desktop = [...window.desktopLab.surfaces.values()].find(surface=>surface.root.contains(node));
    const owner = desktop.layoutOwner;
    const databases = (await indexedDB.databases()).map(db=>db.name);
    const prefs = JSON.parse(localStorage.getItem('photocraft.preferences.account.'+owner));
    const recents = prefs?.fileHandling?.recentFiles ?? [];
    return {profile,owner,databases,recents,enabled:node.querySelector('.webos-photocraft button[aria-pressed]').getAttribute('aria-pressed')};
  });
}

async function closePhoto(page, id) {
  await button(page,photoWindow(id),'Close');
}

async function dropImage(page, id, name, onCanvas) {
  const element = await page.waitForSelector(photoWindow(id) + ' iframe:not([inert])',options);
  const frame = await element.contentFrame();
  await element.dispose();
  assert(frame);
  const bytes = await frame.evaluate(async ({fileName,onCanvas}) => {
    const image = document.createElement('canvas');
    image.width = 24;
    image.height = 16;
    const context = image.getContext('2d');
    context.fillStyle = '#e14422';
    context.fillRect(0,0,12,16);
    context.fillStyle = '#2483bc';
    context.fillRect(12,0,12,16);
    const png = await new Promise(resolve => image.toBlob(resolve,'image/png'));
    const transfer = new DataTransfer();
    transfer.items.add(new File([png],fileName,{type:'image/png'}));
    const canvas = document.querySelector('#photocraft_canvas');
    const box = canvas.getBoundingClientRect();
    const event = {dataTransfer:transfer,bubbles:true,cancelable:true,
      clientX:box.left+box.width/2,clientY:box.top+(onCanvas ? box.height/2 : 12)};
    canvas.dispatchEvent(new DragEvent('dragover',event));
    canvas.dispatchEvent(new DragEvent('drop',event));
    return Array.from(new Uint8Array(await png.arrayBuffer()));
  },{fileName:name,onCanvas});
  return Buffer.from(bytes);
}

async function placeImage(page, id, name) {
  const bytes = await dropImage(page,id,name,true);
  await page.waitForFunction(selector => {
    const snapshot = document.querySelector(selector)?.appView.lifecycle.snapshot();
    return snapshot?.dirty && !snapshot.pending;
  },options,photoWindow(id));
  await shortcut(page,id,'Enter',[]);
  return bytes;
}

async function draftPersisted(page, path, revision, format = null) {
  await page.waitForFunction(async ({path,revision,format}) => {
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
        if (!format || await row.bytes.slice(0,8).text() === format) return true;
      }
      return false;
    } finally { db.close(); }
  },{...options,polling:250},{path,revision,format});
}

async function reloadRecovered(page, id, text) {
  await page.bringToFront();
  const dialogs = [];
  const handleDialog = dialog => { dialogs.push(dialog.type()); void dialog.accept(); };
  page.on('dialog', handleDialog);
  try {
    await page.reload({waitUntil:'networkidle0'});
    await page.waitForSelector(photoWindow(id)+' iframe:not([inert])',{timeout:120_000});
    await page.waitForFunction((selector,text)=>document.querySelector(selector+' [role="status"]')?.textContent.includes(text),
      options,photoWindow(id),text);
    assert.deepEqual(dialogs,['beforeunload']);
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

async function changedBinding(page,id,base,waitOptions = options) {
  const handle = await page.waitForFunction(({id,base})=>{
    const current = [...window.desktopLab.surfaces.values()].flatMap(surface=>surface.windows)
      .find(win=>String(win.id)===id)?.launchContext?.sha256;
    return current && current !== base ? current : false;
  },waitOptions,{id,base});
  try { return await handle.jsonValue(); }
  finally { await handle.dispose(); }
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

function dimensions(artifact) {
  const program = 'import json,sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); print(json.dumps(json.loads(z.read("manifest.json"))["document"]["size"]))';
  return JSON.parse(execFileSync('python3',['-c',program,path.join(output,artifact)],{encoding:'utf8'}));
}

function embeddedImage(artifact, fileName) {
  const program = `import json,re,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as project:
    manifest=json.loads(project.read('manifest.json'))
    matches=[layer['content']['source'] for layer in manifest['document']['layers']
             if layer['content']['kind']=='smart' and layer['content']['source'].get('file_name')==sys.argv[2]]
    assert len(matches)==1 and matches[0]['kind']=='embedded'
    blob=matches[0]['blob']
    assert re.fullmatch('[0-9a-f]{64}',blob)
    sys.stdout.buffer.write(project.read('blobs/'+blob+'.zst'))`;
  return zstdDecompressSync(execFileSync('python3',['-c',program,path.join(output,artifact),fileName]));
}

function editedText(artifact) {
  const program = 'import json,sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); d=json.loads(z.read("manifest.json")); print(json.dumps([l["content"]["text"] for l in d["document"]["layers"] if "text" in l["content"]]))';
  return JSON.parse(execFileSync('python3',['-c',program,path.join(output,artifact)],{encoding:'utf8'}));
}

async function verifyComposition(page) {
  await launch(page,'Graphics','PhotoCraft');
  const id=await readyPhoto(page);
  const filesId=await files(page);
  await shortcut(page,id,'s');
  await destination(page,'Text Composition');
  await bound(page,id,'Text Composition.pcraft');
  const resource='Pictures/Text Composition.pcraft';
  const before=await download(page,filesId,resource,'ime-before.pcraft');
  await page.evaluate(selector=>{
    const source=document.querySelector(selector+' iframe').contentWindow;
    window.photoCompositionState=null;
    window.addEventListener('message',event=>{
      const {type,capturable,unfinishedEdit}=event.data??{};
      if (event.origin===location.origin && event.source===source && type==='photocraft:account-project-state') {
        window.photoCompositionState={capturable,unfinishedEdit};
      }
    });
  },photoWindow(id));
  await shortcut(page,id,'t',[]);
  const frame=await page.waitForSelector(photoWindow(id)+' iframe:not([inert])',options);
  const canvas=await (await frame.contentFrame()).$('canvas#photocraft_canvas');
  const box=await canvas.boundingBox();
  await canvas.dispose();
  await frame.dispose();
  await page.mouse.click(box.x+Math.max(65,(box.width-230)/2),box.y+box.height*0.56);
  await page.keyboard.type('Before ');
  await page.waitForFunction(()=>window.photoCompositionState?.capturable && window.photoCompositionState?.unfinishedEdit,options);
  const connection=await page.createCDPSession();
  try {
    await connection.send('Input.imeSetComposition',{text:'にほ',selectionStart:2,selectionEnd:2});
    await page.waitForFunction(()=>window.photoCompositionState?.unfinishedEdit && !window.photoCompositionState?.capturable,options);
    let uploads=0;
    const observeUpload=request=>{
      if(request.url()===origin+'/gateway/upload' && request.method()==='POST') uploads++;
    };
    page.on('request',observeUpload);
    try {
      await page.keyboard.down('Control');
      try { await page.keyboard.press('s'); }
      finally { await page.keyboard.up('Control'); }
      await new Promise(resolve=>setTimeout(resolve,300));
      assert.equal(await download(page,filesId,resource,'ime-unsaved.pcraft'),before);
      assert.equal(uploads,0);
      assert.deepEqual(await page.evaluate(()=>window.photoCompositionState),{capturable:false,unfinishedEdit:true});
    } finally { page.off('request',observeUpload); }
    await connection.send('Input.insertText',{text:'日本'});
    await page.waitForFunction(()=>window.photoCompositionState?.capturable,options);
  } finally { await connection.detach(); }
  await shortcut(page,id,'Enter',['Control']);
  await shortcut(page,id,'s');
  const confirmed=await changedBinding(page,id,before);
  assert.equal(await download(page,filesId,resource,'ime-confirmed.pcraft'),confirmed);
  assert(editedText('ime-confirmed.pcraft').some(text=>JSON.stringify(text).includes('Before 日本')));
  pass('Active Chromium text composition survives Save and persists confirmed Japanese text after composition ends');
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

  await launch(page,'Graphics','PhotoCraft');
  const embeddedId = await readyPhoto(page);
  const embeddedPath = 'Pictures/Portable artwork.pcraft';
  const originalImage = await placeImage(page,embeddedId,'tiles.png');
  await shortcut(page,embeddedId,'s');
  await destination(page,'Portable artwork');
  await bound(page,embeddedId,'Portable artwork.pcraft');
  const embeddedRevision = await download(page,filesId,embeddedPath,'portable.pcraft');
  assert.deepEqual(embeddedImage('portable.pcraft','tiles.png'),originalImage);

  await file(page,filesId,'open',{path:embeddedPath});
  assert.equal(await readyPhoto(page),embeddedId);
  const beforeImport = (await page.$$(photoView)).length;
  await dropImage(page,embeddedId,'Dropped illustration.png',false);
  await page.waitForFunction((selector,count)=>document.querySelectorAll(selector).length===count+1,options,photoView,beforeImport);
  const droppedId=await readyPhoto(page);
  assert.notEqual(droppedId,embeddedId);
  await page.$eval(photoWindow(droppedId),win=>win.appView.ready);
  await bound(page,droppedId,'Dropped illustration.png');
  await bound(page,embeddedId,'Portable artwork.pcraft');
  await draftPersisted(page,null,null);
  await shortcut(page,droppedId,'s');
  await destination(page,'From device drop');
  const droppedPath='Pictures/From device drop.pcraft';
  await bound(page,droppedId,'From device drop.pcraft');
  const droppedRevision=await download(page,filesId,droppedPath,'device-drop.pcraft');
  assert.deepEqual(dimensions('device-drop.pcraft'),{width:24,height:16});
  assert.equal(await download(page,filesId,embeddedPath,'portable-after-drop.pcraft'),embeddedRevision);
  await closePhoto(page,droppedId);
  await page.waitForSelector(photoWindow(droppedId),{...options,hidden:true});
  pass('Dropping outside the canvas starts a separate recoverable project and preserves the source window and account file');

  await file(page,filesId,'open',{path:embeddedPath});
  const devicePath=path.join(output,'Device illustration.png');
  await writeFile(devicePath,originalImage);
  const [fileChooser]=await Promise.all([
    page.waitForFileChooser(),button(page,photoWindow(embeddedId),'Open from device'),
  ]);
  await fileChooser.accept([devicePath]);
  await page.waitForFunction((selector,count)=>document.querySelectorAll(selector).length===count+1,options,photoView,beforeImport);
  const deviceId=await readyPhoto(page);
  assert.notEqual(deviceId,embeddedId);
  await page.$eval(photoWindow(deviceId),win=>win.appView.ready);
  await bound(page,deviceId,'Device illustration.png');
  await closePhoto(page,deviceId);
  await shortcut(page,deviceId,'n',[],{closing:true});
  await page.waitForSelector(photoWindow(deviceId),{...options,hidden:true});
  assert.equal(await download(page,filesId,droppedPath,'device-after-discard.pcraft'),droppedRevision);
  pass('The device picker opens an independent native project that can be discarded without modifying account files');

  await closePhoto(page,embeddedId);
  await page.waitForSelector(photoWindow(embeddedId),{...options,hidden:true});

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
  await file(reopened,freshFiles,'open',{path:embeddedPath});
  const reopenedEmbedded=await readyPhoto(reopened);
  await bound(reopened,reopenedEmbedded,'Portable artwork.pcraft');
  await closePhoto(reopened,reopenedEmbedded);
  await reopened.waitForSelector(photoWindow(reopenedEmbedded),{...options,hidden:true});
  assert.equal(await download(reopened,freshFiles,embeddedPath,'portable-reopened.pcraft'),embeddedRevision);
  assert.deepEqual(embeddedImage('portable-reopened.pcraft','tiles.png'),originalImage);
  pass('A dropped image reopens in a fresh browser as an embedded smart object with its original bytes');

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
  await draftPersisted(page,untitledPath,typeBase,'PCDRAFT1');
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
  const toggle=autoSaveControl(autoId);
  assert.equal(await automatic.$eval(toggle,node=>node.getAttribute('aria-pressed')),'false');
  const writes=[];
  automatic.on('request',request=>{
    if (request.url()===origin+'/gateway/upload' && request.method()==='POST') writes.push(performance.now());
  });
  const boundRevision=()=>automatic.evaluate(id=>[...window.desktopLab.surfaces.values()].flatMap(surface=>surface.windows)
    .find(win=>String(win.id)===id)?.launchContext?.sha256,autoId);
  const nextAutomaticRevision = (base,timeout) => changedBinding(automatic,autoId,base,{timeout});
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

  await automatic.click(toggle);
  await shortcut(automatic,autoId,'n',['Control','Shift']);
  await automatic.keyboard.press('Enter');
  await draftPersisted(automatic,untitledPath,secondAuto);
  await endSession(automatic,'Cancel');
  await automatic.waitForFunction(()=>!!window.desktopLab.session && !document.querySelector('.desktop').inert,options);
  assert.equal(await boundRevision(),secondAuto);
  pass('PhotoCraft Cancel keeps the signed session and the native dirty layer available');

  await endSession(automatic,'Save');
  await automatic.waitForSelector('.login-gate',{timeout:120_000});
  await login(automatic,A,false);
  const savedFiles=await files(automatic);
  await file(automatic,savedFiles,'list',{path:'Pictures'});
  const sessionSaved=await download(automatic,savedFiles,untitledPath,'session-saved.pcraft');
  assert.notEqual(sessionSaved,secondAuto);
  assert.equal(layers('session-saved.pcraft'),blankLayers+5);
  pass('PhotoCraft Save on sign-out persists and acknowledges the native layer before Accounts ends');

  await file(automatic,savedFiles,'open',{path:untitledPath});
  const discardedId=await readyPhoto(automatic);
  await shortcut(automatic,discardedId,'n',['Control','Shift']);
  await automatic.keyboard.press('Enter');
  await draftPersisted(automatic,untitledPath,sessionSaved);
  await endSession(automatic,'Discard');
  await automatic.waitForSelector('.login-gate',{timeout:120_000});
  await login(automatic,B,false);
  const switchedFiles=await files(automatic);
  await file(automatic,switchedFiles,'list',{path:'Pictures'});
  await assert.rejects(file(automatic,switchedFiles,'snapshot',{path:untitledPath}));
  assert.equal((await automatic.$$(photoView)).length,0);
  await automatic.click('.app-menu-button');
  await button(automatic,'.menu-pane','End session');
  await automatic.waitForSelector('.login-gate',{timeout:120_000});
  await login(automatic,A,false);
  const returnedFiles=await files(automatic);
  assert.equal(await download(automatic,returnedFiles,untitledPath,'session-discarded.pcraft'),sessionSaved);
  await file(automatic,returnedFiles,'open',{path:untitledPath});
  const returned=await readyPhoto(automatic);
  assert.doesNotMatch(await automatic.$eval(photoWindow(returned)+' [role="status"]',node=>node.textContent),/Recovered/);
  pass('Discard before sign-out clears the draft while account switching preserves the saved file');

  await automatic.click(autoSaveControl(returned));
  const accountA=await profileState(automatic,returned);
  assert.equal(accountA.profile,accountA.owner);
  assert.equal(accountA.enabled,'true');
  assert(accountA.recents.includes(untitledPath));
  assert(accountA.databases.includes('photocraft.presets.account.'+accountA.owner));
  await automatic.click('.app-menu-button');
  await button(automatic,'.menu-pane','End session');
  await automatic.waitForSelector('.login-gate',{timeout:120_000});
  await login(automatic,B,false);
  await launch(automatic,'Graphics','PhotoCraft');
  const profileB=await readyPhoto(automatic);
  const accountB=await profileState(automatic,profileB);
  assert.notEqual(accountB.owner,accountA.owner);
  assert.equal(accountB.profile,accountB.owner);
  assert.equal(accountB.enabled,'false');
  assert.deepEqual(accountB.recents,[]);
  assert(accountB.databases.includes('photocraft.presets.account.'+accountB.owner));
  assert(!accountB.databases.includes('photocraft.presets'));
  await automatic.click('.app-menu-button');
  await button(automatic,'.menu-pane','End session');
  await automatic.waitForSelector('.login-gate',{timeout:120_000});
  await login(automatic,A,false);
  await launch(automatic,'Graphics','PhotoCraft');
  const profileA=await readyPhoto(automatic);
  const againA=await profileState(automatic,profileA);
  assert.equal(againA.profile,accountA.owner);
  assert.equal(againA.enabled,'true');
  assert(againA.recents.includes(untitledPath));
  pass('Switching accounts in one browser separates native preset databases, recent paths and AutoSave settings');
  if (process.env.WEBOS_PHOTO_NESTED_RECOVERY === '1') {
    await launch(automatic,'Graphics','PhotoCraft');
    const nestedId = await readyPhoto(automatic);
    const nestedFiles = await files(automatic);
    await shortcut(automatic,nestedId,'s');
    await destination(automatic,'Nested Recovery');
    await bound(automatic,nestedId,'Nested Recovery.pcraft');
    const nestedPath = 'Pictures/Nested Recovery.pcraft';
    const blankRevision = await download(automatic,nestedFiles,nestedPath,'nested-blank.pcraft');
    await placeImage(automatic,nestedId,'nested-asset.png');
    await shortcut(automatic,nestedId,'s');
    const nestedBase = await changedBinding(automatic,nestedId,blankRevision);
    await shortcut(automatic,nestedId,'f');
    await automatic.keyboard.type('Edit Contents',{delay:20});
    await automatic.keyboard.press('Enter');
    await automatic.waitForFunction(selector=>document.querySelector(selector)?.appView.lifecycle.snapshot().pending,
      options,photoWindow(nestedId));
    await shortcut(automatic,nestedId,'n',['Control','Shift']);
    await shortcut(automatic,nestedId,'Enter',[]);
    await draftPersisted(automatic,nestedPath,nestedBase,'PCNEST01');
    await reloadRecovered(automatic,nestedId,'Recovered unsaved changes');
    await automatic.waitForFunction(selector=>{
      const state=document.querySelector(selector)?.appView.lifecycle.snapshot();
      return state?.dirty && state.pending;
    },options,photoWindow(nestedId));
    const restoredFiles = await files(automatic);
    assert.equal(await download(automatic,restoredFiles,nestedPath,'nested-before-save.pcraft'),nestedBase);
    await shortcut(automatic,nestedId,'s');
    await shortcut(automatic,nestedId,'w');
    await automatic.waitForFunction(selector=>{
      const state=document.querySelector(selector)?.appView.lifecycle.snapshot();
      return state?.dirty && !state.pending;
    },options,photoWindow(nestedId));
    await shortcut(automatic,nestedId,'s');
    await changedBinding(automatic,nestedId,nestedBase);
    await download(automatic,restoredFiles,nestedPath,'nested-after-save.pcraft');
    await writeFile(path.join(output,'nested-embedded.pcraft'),embeddedImage('nested-after-save.pcraft','nested-asset.pcraft'));
    assert.equal(layers('nested-embedded.pcraft'),2);
    pass('Refresh restores the dirty smart-object tab and saving it updates the account project only after the parent Save');
    await verifyComposition(automatic);
  }
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
