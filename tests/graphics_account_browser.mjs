/** Qualify a linked graphics editor inside an actual account desktop. */
import assert from 'node:assert/strict';
import {randomBytes} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const {WEBOS_VIEWER_ORIGIN:origin,WEBOS_TEST_OUTPUT:output} = process.env;
assert(path.isAbsolute(output) && new URL(origin).hostname === '127.0.0.1');
assert.equal((await (await fetch(origin+'/healthz')).json()).scope,'development');
await mkdir(output,{mode:0o700});
const app = process.env.WEBOS_TEST_GRAPHICS_APP || 'figcraft';
const label = {figcraft:'FigCraft',vectorcraft:'VectorCraft',anicraft:'AniCraft'}[app];
const menu = app === 'anicraft' ? 'Animation & Video' : 'Graphics';
assert(label);
const {apps} = await (await fetch(origin+'/viewer-build.json')).json();
assert(apps.includes(app));
const username = app + randomBytes(6).toString('hex');
const password = randomBytes(12).toString('hex');
const selector = `.window:has(.webos-${app})`;
const files = '.window:has(.webos-files)';
const project = 'Documents/Browser.'+app;
const copy = 'Documents/Browser Copy.'+app;
const checks = [], errors = [];

async function button(page, scope, label) {
  const handle = await page.waitForFunction((container,label) =>
    [...document.querySelectorAll(container+' button')].find(node => !node.disabled &&
      [node.getAttribute('aria-label'),(node.querySelector('.row-text')||node).textContent.trim()].includes(label)),
  {}, scope, label);
  try { await handle.asElement().click(); }
  finally { await handle.dispose(); }
}

async function launch(page, menu, app) {
  await page.click('.app-menu-button');
  await button(page,'.menu-pane',menu);
  await button(page,'.menu-pane',app);
}

async function login(page, register) {
  await page.setViewport({width:1440,height:1000});
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(origin,{waitUntil:'networkidle0'});
  await page.waitForSelector('.login-gate');
  if (register) await page.click('.login-toggle');
  await page.type('[aria-label="Username"]',username);
  await page.type('[aria-label="Password"]',password);
  if (register) await page.type('[aria-label="Confirm password"]',password);
  await button(page,'.login-gate',register?'Register':'Sign in');
  await page.waitForFunction(()=>!!window.desktopLab?.session && !document.querySelector('.login-gate'));
}

async function ready(page) {
  await page.waitForSelector(selector,{timeout:30_000});
  await page.$eval(selector,window=>window.appView?.ready);
  return page.waitForSelector(selector+' iframe:not([inert])',{timeout:120_000});
}

const binding = page => page.$eval(selector,node=>[...window.desktopLab.surfaces.values()]
  .flatMap(surface=>surface.windows).find(window=>String(window.id)===node.dataset.window)?.launchContext);

async function clean(page, expected) {
  await page.waitForFunction((view,expectClean)=>{
    const state = document.querySelector(view)?.appView?.lifecycle.snapshot();
    return state && !state.pending && state.dirty===!expectClean;
  },{},selector,expected);
}

async function draw(page, horizontal = .45) {
  await page.bringToFront();
  await page.waitForSelector(selector);
  await page.$eval(selector,node=>{
    const desktop = [...window.desktopLab.surfaces.values()].find(surface=>surface.root.contains(node));
    const target = desktop.windows.find(window=>String(window.id)===node.dataset.window);
    if (desktop.active!==target.id) desktop.activateWindow(target);
  });
  let iframe = await ready(page);
  if (['vectorcraft','anicraft'].includes(app) && (await iframe.boundingBox())?.width < 1000) {
    await iframe.dispose();
    await button(page,selector,'Maximize');
    iframe = await ready(page);
  }
  const bounds = await iframe.boundingBox();
  assert(bounds && bounds.width>400 && bounds.height>300);
  const position = app === 'vectorcraft' ? .32+(horizontal-.37)*.65 : horizontal;
  const point = {x:bounds.x+bounds.width*position,y:bounds.y+bounds.height*.43};
  await page.waitForFunction(({x,y},view)=>document.elementFromPoint(x,y)===document.querySelector(view+' iframe'),{},point,selector);
  const frame = await iframe.contentFrame();
  const painted = () => frame.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await frame.$eval(`#${app}_canvas`,canvas=>{canvas.tabIndex=0;canvas.focus();});
  await page.keyboard.press(app === 'vectorcraft' ? 'm' : 'r');
  await painted();
  await page.mouse.move(point.x,point.y);
  await page.mouse.down();
  await painted();
  await page.mouse.move(bounds.x+bounds.width*(position+.16),bounds.y+bounds.height*.65,{steps:10});
  await page.mouse.up();
  await iframe.dispose();
  await clean(page,false);
}

async function pressShortcut(page, key, modifiers = ['Control']) {
  for (const modifier of modifiers) await page.keyboard.down(modifier);
  try { await page.keyboard.press(key); }
  finally { for (const modifier of [...modifiers].reverse()) await page.keyboard.up(modifier); }
}

const saveShortcut = (page, modifiers) => pressShortcut(page,'s',modifiers);

async function saveAs(page, name, modifiers) {
  await saveShortcut(page,modifiers);
  const picker = 'dialog.codi-file-picker[open]', prompt = 'dialog.codi-confirm-dialog[open]';
  await button(page,picker,'Open folder Documents');
  await button(page,picker,'Use this folder');
  await page.waitForSelector(prompt+' input');
  await page.$eval(prompt+' input',(input,value)=>{input.value=value;},name);
  await button(page,prompt,'Save');
  await page.waitForFunction((view,title)=>document.querySelector(view+' .caption-text')?.textContent===title,
    {},selector,`${name}.${app} — ${label}`);
  await clean(page,true);
}

async function accountRevision(page, path, open = false) {
  return page.$eval(files,async (window,{path,open})=>{
    await window.appView.ready;
    await window.appView.execute('list',{path:'Documents'});
    const receipt = await window.appView.execute('snapshot',{path});
    if (open) await window.appView.execute('open',{path});
    return receipt.sha256;
  },{path,open});
}

async function accountAnimation(page, pathname) {
  return page.$eval(files,async (node,pathname)=>{
    const desktop = [...window.desktopLab.surfaces.values()].find(surface=>surface.root.contains(node));
    const model = desktop.windows.find(w=>String(w.id)===node.dataset.window);
    const host = await publicAppHost(desktop,model);
    const context = await host.storage.accountFileContext();
    const snapshot = await context.files.read(pathname);
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(snapshot.data));
  },pathname);
}

async function renderFrame(frame) {
  await frame.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
}

function aniWavFixture() {
  const rate = 48_000;
  const samples = 4_800;
  const audio = Buffer.alloc(44 + samples*2);
  audio.write('RIFF',0);
  audio.writeUInt32LE(audio.length-8,4);
  audio.write('WAVEfmt ',8);
  audio.writeUInt32LE(16,16);
  audio.writeUInt16LE(1,20);
  audio.writeUInt16LE(1,22);
  audio.writeUInt32LE(rate,24);
  audio.writeUInt32LE(rate*2,28);
  audio.writeUInt16LE(2,32);
  audio.writeUInt16LE(16,34);
  audio.write('data',36);
  audio.writeUInt32LE(samples*2,40);
  for (let i=0;i<samples;i++) audio.writeInt16LE(Math.round(2000*Math.sin(i*2*Math.PI*440/rate)),44+i*2);
  return audio;
}

async function aniTimelineAndMedia(page) {
  const iframe = await ready(page);
  const frame = await iframe.contentFrame();
  const imageName = 'timeline-swatch.png';
  const imagePath = path.join(output,imageName);
  const data = await page.evaluate(()=>{
    const canvas = document.createElement('canvas');
    canvas.width = 12;
    canvas.height = 10;
    const context = canvas.getContext('2d');
    context.fillStyle = '#d5289c';
    context.fillRect(0,0,12,10);
    return canvas.toDataURL('image/png').split(',')[1];
  });
  await writeFile(imagePath,Buffer.from(data,'base64'),{flag:'wx',mode:0o600});
  const soundPath = path.join(output,'timeline-tone.wav');
  await writeFile(soundPath,aniWavFixture(),{flag:'wx',mode:0o600});
  await frame.$eval('#anicraft_canvas',element=>element.focus());
  await page.keyboard.press('F6');
  await renderFrame(frame);
  for (const source of [imagePath,soundPath]) {
    const previous = await page.$eval(selector,node=>node.appView.lifecycle.snapshot().revision);
    const [picker] = await Promise.all([page.waitForFileChooser(),pressShortcut(page,'r')]);
    await picker.accept([source]);
    await page.waitForFunction((selector,previous)=>{
      const state = document.querySelector(selector)?.appView.lifecycle.snapshot();
      return state && !state.pending && state.dirty && state.revision>previous;
    },{},selector,previous);
    await renderFrame(frame);
  }
  await iframe.dispose();
}

async function aniExportFrame(page, stage) {
  const iframe = await ready(page);
  const frame = await iframe.contentFrame();
  const downloads = path.join(output,'downloads');
  await mkdir(downloads,{mode:0o700});
  const cdp = await browser.target().createCDPSession();
  let timer;
  try {
    await cdp.send('Browser.setDownloadBehavior',{
      behavior:'allow',downloadPath:downloads,browserContextId:page.browserContext().id,eventsEnabled:true
    });
    let observed;
    const completed = new Promise((resolve,reject)=>{
      timer = setTimeout(()=>reject(Error('The native PNG export did not complete.')),20_000);
      cdp.on('Browser.downloadWillBegin',event=>{ observed = event; });
      cdp.on('Browser.downloadProgress',event=>{
        if (event.guid !== observed?.guid) return;
        if (event.state === 'completed') resolve(observed.suggestedFilename);
        if (event.state === 'canceled') reject(Error('The native PNG export was canceled.'));
      });
    });
    await frame.$eval('#anicraft_canvas',canvas=>{canvas.tabIndex=0;canvas.focus();});
    // Reopening starts at frame one. Move to the next keyframe before exporting.
    await page.keyboard.press('Period');
    await renderFrame(frame);
    await pressShortcut(page,'k');
    await renderFrame(frame);
    await page.keyboard.type('Export Frame as PNG');
    await renderFrame(frame);
    await page.keyboard.press('Enter');
    await renderFrame(frame);
    await page.keyboard.press('Enter');
    const name = await completed;
    assert.match(name,/^frame_\d{4}\.png$/);
    const png = await readFile(path.join(downloads,name));
    assert.deepEqual([...png.subarray(0,8)],[137,80,78,71,13,10,26,10]);
    assert.deepEqual([png.readUInt32BE(16),png.readUInt32BE(20)],[stage.width,stage.height]);
    const painted = await page.evaluate(async encoded=>{
      const bytes = Uint8Array.from(atob(encoded),character=>character.charCodeAt(0));
      const image = await createImageBitmap(new Blob([bytes],{type:'image/png'}));
      const canvas = new OffscreenCanvas(image.width,image.height);
      const context = canvas.getContext('2d');
      context.drawImage(image,0,0);
      const {data} = context.getImageData(0,0,image.width,image.height);
      image.close();
      let swatchPixels = 0;
      for (let pixel=0; pixel<data.length; pixel+=4) {
        if (data[pixel]===213 && data[pixel+1]===40 && data[pixel+2]===156 && data[pixel+3]===255) swatchPixels++;
      }
      return swatchPixels;
    },png.toString('base64'));
    assert.ok(painted>=100,'The exported second frame contains the embedded magenta swatch');
  } finally {
    clearTimeout(timer);
    await cdp.detach();
    await iframe.dispose();
  }
}

async function waitForDraft(page, path, revision, present) {
  await page.waitForFunction(async ({path,revision,present,app})=>{
    const name = `webos-${app}-recovery-v1`;
    if (!(await indexedDB.databases()).some(database=>database.name===name)) return !present;
    const db = await new Promise((resolve,reject)=>{
      const request = indexedDB.open(name);
      request.onsuccess = ()=>resolve(request.result);
      request.onerror = ()=>reject(request.error);
    });
    try {
      const rows = await new Promise((resolve,reject)=>{
        const request = db.transaction('drafts').objectStore('drafts').getAll();
        request.onsuccess = ()=>resolve(request.result);
        request.onerror = ()=>reject(request.error);
      });
      return rows.some(row=>row.path===path && row.revision===revision && row.bytes instanceof Blob && row.bytes.size>8)===present;
    } finally { db.close(); }
  },{polling:250},{path,revision,present,app});
}

async function close(page, choice) {
  await button(page,selector,'Close');
  await button(page,`dialog.webos-${app}-session[open]`,choice);
  if (choice === 'Cancel') await clean(page,false);
  else await page.waitForSelector(selector,{hidden:true});
}

async function reload(page) {
  const dialogs = [];
  const accept = dialog=>{dialogs.push(dialog.type()); void dialog.accept();};
  page.on('dialog',accept);
  try { await page.reload({waitUntil:'domcontentloaded'}); }
  finally { page.off('dialog',accept); }
  await ready(page);
  await clean(page,false);
  assert(dialogs.includes('beforeunload'));
}

async function loseWriteReceipt(page) {
  const session = await page.createCDPSession();
  let timer, finish, reject;
  const responseLost = new Promise((resolve, rejectPromise)=>{
    finish = resolve;
    reject = rejectPromise;
    timer = setTimeout(()=>reject(Error('No accepted account write was intercepted.')),30_000);
  });
  session.on('Fetch.requestPaused', event=>{
    if (event.request.method==='POST' && event.responseStatusCode>=200 && event.responseStatusCode<300) {
      void session.send('Fetch.failRequest',{requestId:event.requestId,errorReason:'Failed'}).then(finish,reject);
    } else {
      void session.send('Fetch.continueResponse',{requestId:event.requestId}).catch(reject);
    }
  });
  try {
    await session.send('Fetch.enable',{patterns:[{urlPattern:origin+'/gateway/upload',requestStage:'Response'}]});
    await Promise.all([responseLost,saveShortcut(page)]);
    await page.waitForFunction(view=>document.querySelector(view+' [role=status]')?.textContent.includes('unconfirmed'),{},selector);
  } finally {
    clearTimeout(timer);
    await session.send('Fetch.disable');
    await session.detach();
  }
}

let browser, page;
try {
  browser = await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true,
    args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-background-networking'],
  });
  page = await browser.newPage();
  await login(page,true);
  await launch(page,menu,label);
  const iframe = await ready(page);
  const frame = await iframe.contentFrame();
  await frame.waitForSelector(`canvas#${app}_canvas`);
  checks.push(`${label} starts from the classic Desktop menu`);

  await draw(page);
  checks.push('Drawing on the native canvas changes the document');

  if (app === 'anicraft') await aniTimelineAndMedia(page);
  await saveAs(page,'Browser',['Control']);
  checks.push(`Native Save creates an account-backed ${label} project`);

  const fresh = await browser.createBrowserContext();
  page = await fresh.newPage();
  await login(page,false);
  await launch(page,'System Tools','Files');
  await page.waitForFunction(files=>!!document.querySelector(files)?.appView,{},files);
  const saved = await accountRevision(page,project,true);
  assert.match(saved,/^[a-f0-9]{64}$/);
  await ready(page);
  assert.equal((await binding(page)).sha256,saved);
  checks.push('A fresh browser signs in and opens the server revision from Files');
  if (app === 'anicraft') {
    const {document:animation} = await accountAnimation(page,project);
    const layers = animation.scenes[0].timeline.layers;
    assert.ok(layers.some(layer=>layer.keyframes.length>=2),'A second native keyframe survived Save and reopen');
    assert.ok(animation.bitmaps.some(image=>image.name==='timeline-swatch.png' && image.width===12 && image.height===10));
    const audio = animation.sounds.find(sound=>sound.rate===48_000 && sound.channels===1);
    assert.deepEqual(Buffer.from(audio.data,'base64'),aniWavFixture());
    const soundLayer = layers.find(layer=>layer.name==='timeline-tone');
    assert.ok(soundLayer?.keyframes.some(keyframe=>keyframe.sound?.sound===audio.id));
    checks.push('Native keyframes, an embedded bitmap and a linked WAV cue survive Save and fresh-browser reopen');
    await aniExportFrame(page,animation.stage);
    checks.push('Native PNG export from the reopened timeline contains the embedded bitmap at the project size');
  }

  await draw(page,.60);
  await saveAs(page,'Browser Copy',['Control','Shift']);
  const copied = (await binding(page)).sha256;
  assert.equal((await binding(page)).path,copy);
  assert.notEqual(copied,saved);
  assert.equal(await accountRevision(page,project),saved);
  assert.equal(await accountRevision(page,copy),copied);
  checks.push('Native Save As adopts a separate path and preserves the original version');

  await draw(page,.37);
  await waitForDraft(page,copy,copied,true);
  await reload(page);
  assert.equal((await binding(page)).sha256,copied);
  assert.equal(await accountRevision(page,copy),copied);
  checks.push('Refresh warns and recovers the draft against its unchanged server version');

  await close(page,'Cancel');
  assert.equal((await binding(page)).sha256,copied);
  await waitForDraft(page,copy,copied,true);
  checks.push('Cancel in the dirty close dialog keeps the recovered editor and draft');
  await close(page,'Discard');
  await waitForDraft(page,copy,copied,false);
  assert.equal(await accountRevision(page,copy,true),copied);
  await ready(page);
  await clean(page,true);
  checks.push('Discard clears the recovered draft and leaves the server version untouched');

  await draw(page,.53);
  await close(page,'Save');
  const afterClose = await accountRevision(page,copy,true);
  assert.notEqual(afterClose,copied);
  assert.equal(await accountRevision(page,project),saved);
  checks.push('Save from dirty close writes the confirmed account revision before closing');

  await draw(page,.40);
  await waitForDraft(page,copy,afterClose,true);
  const concurrent = await (await browser.createBrowserContext()).newPage();
  await login(concurrent,false);
  await launch(concurrent,'System Tools','Files');
  await concurrent.waitForFunction(files=>!!document.querySelector(files)?.appView,{},files);
  assert.equal(await accountRevision(concurrent,copy,true),afterClose);
  await draw(concurrent,.56);
  await saveShortcut(concurrent);
  await clean(concurrent,true);
  const latest = (await binding(concurrent)).sha256;
  assert.notEqual(latest,afterClose);
  await page.bringToFront();
  await saveShortcut(page);
  await page.waitForFunction(view=>/changed.*(reload|replacing|version)|conflict/i.test(document.querySelector(view+' [role=status]')?.textContent),{},selector);
  await clean(page,false);
  assert.equal((await binding(page)).sha256,afterClose);
  assert.equal(await accountRevision(page,copy),latest);
  await waitForDraft(page,copy,afterClose,true);
  checks.push('A second browser can save while the stale editor keeps its original binding and draft');

  await reload(page);
  assert.equal(await binding(page),undefined);
  assert.match(await page.$eval(selector+' [role=status]',node=>node.textContent),/recovered an unsaved copy/i);
  assert.equal(await accountRevision(page,copy),latest);
  checks.push('A stale recovery draft opens as an unsaved copy and preserves the newer account file');

  await draw(concurrent,.44);
  await waitForDraft(concurrent,copy,latest,true);
  await loseWriteReceipt(concurrent);
  const committed = await accountRevision(page,copy);
  assert.notEqual(committed,latest);
  assert.equal((await binding(concurrent)).sha256,latest);
  await waitForDraft(concurrent,copy,latest,true);
  await button(concurrent,selector,'Close');
  await concurrent.waitForFunction(label=>document.querySelector('#feedback')?.textContent.includes(`Finish the pending ${label} operation`),{},label);
  assert.equal(await accountRevision(page,copy),committed);
  checks.push('A lost write response preserves the prior binding and draft and prevents close until the result is reviewed');
  assert.deepEqual(errors,[]);
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,errors})+'\n');
} catch (error) {
  const status = await page?.$eval(selector+' [role=status]',node=>node.textContent).catch(()=>null);
  await page?.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'FAIL',checks,errors,error:error.message,editorStatus:status})+'\n');
  throw error;
} finally {
  await browser?.close();
}
