import assert from 'node:assert/strict';
import {createHash, randomBytes} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {mkdir, writeFile} from 'node:fs/promises';
import {registerHooks} from 'node:module';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

registerHooks({resolve(specifier, context, next) {
  if (specifier !== '@webos/runtime/strict-json') return next(specifier, context);
  return {url:new URL('../platform/runtime/active-system/network/strict-json.mjs', import.meta.url).href, shortCircuit:true};
}});
const {makeKey, hash, nowSeconds, signJws} = await import('../platform/accounts/browser/crypto.mjs');
const {PROOF_TYPE} = await import('../platform/accounts/browser/identity.mjs');

const origin = process.env.WEBOS_VIEWER_ORIGIN;
const output = process.env.WEBOS_TEST_OUTPUT;
assert.equal(new URL(origin).hostname, '127.0.0.1');
assert.equal(new URL(origin).origin, origin);
assert(output && path.isAbsolute(output));
assert.equal((await (await fetch(origin+'/healthz')).json()).scope, 'development');
const {apps} = await (await fetch(origin+'/viewer-build.json')).json();
const photoProfile = apps.includes('photocraft');
const officeProfile = apps.includes('gridcraft') && apps.includes('deckcraft');
const disabled = process.env.WEBOS_AGENT_DISABLED_TEST === '1';
const graphicsOnly = process.env.WEBOS_GRAPHICS_AGENT_ONLY === '1';
const lightOnly = process.env.WEBOS_LIGHTCRAFT_TEST === '1';
const graphics = ['figcraft','vectorcraft','anicraft'].filter(app=>apps.includes(app));
assert(lightOnly ? apps.includes('lightcraft') : graphicsOnly ? graphics.length : disabled || photoProfile || officeProfile);
await mkdir(output, {mode:0o700});
const checks = [];
const agent = await makeKey();
const otherAgent = await makeKey();
const present = (name) => { checks.push(name); console.log('PASS '+name); };
const timeout = {timeout:120_000};
const modal = 'dialog[open]';
const selector = windowId => '.window[data-window="'+windowId+'"]';

async function login(browser, existing) {
  const context = await browser.createBrowserContext();
  const page = await context.newPage();
  const marker = randomBytes(6).toString('hex');
  const credentials = existing ?? {username:'office'+marker,password:marker+marker};
  await page.goto(origin, {waitUntil:'networkidle0'});
  if (!existing) await page.click('.login-toggle');
  await page.type('[aria-label="Username"]', credentials.username);
  await page.type('[aria-label="Password"]', credentials.password);
  if (!existing) await page.type('[aria-label="Confirm password"]', credentials.password);
  await page.click('.login-gate button[type="submit"]');
  const status = await page.waitForFunction(() => window.desktopLab.session && !document.querySelector('.login-gate')
    ? 'signed in' : document.querySelector('.login-error')?.textContent || false, timeout);
  assert.equal(await status.jsonValue(), 'signed in');
  return {page, context, credentials};
}

async function editor(page, app) {
  const id = await page.evaluate(app => window.desktopLab.surfaces.get('Desktop').launch(app).id, app);
  const status = await page.waitForFunction(async (id,app) => {
    const model = await document.querySelector('.window[data-window="'+id+'"]')?.appView?.inspect();
    if (['photocraft','figcraft','vectorcraft','anicraft','lightcraft'].includes(app)) return model?.instanceId ? 'ready' : false;
    return model && ['ready','failed','unavailable'].includes(model.phase) ? model.phase : false;
  }, timeout, id, app);
  assert.equal(await status.jsonValue(), 'ready');
  return id;
}

async function approve(page, windowId, commands) {
  const {instanceId} = await page.$eval(selector(windowId), node => node.appView.inspect());
  return page.evaluate(params => window.desktopLab.agentOperations.approve(params).then(
    result => ({result}), error => ({error:error.message})),
    {instanceId, agentKey:agent.publicKey, commands, seconds:180});
}

const dispatch = (page, confirmation, intent) => page.evaluate(request =>
  window.desktopLab.agentOperations.dispatch(request).then(result => ({result}), error => ({error:error.message})),
  {confirmation, intent});

function intentFor(approval, command, args) {
  return {method:'application.execute', target:approval.target, resources:approval.grant.scope.resources,
    request:{...approval.document,command,args}};
}

async function authorize(approval, intent, signingAgent = agent) {
  const operation = '/api/v1/agents/authorize';
  const headers = {'Content-Type':'application/json',Origin:origin};
  const response = await fetch(origin+'/api/v1/agents/challenge', {method:'POST',headers,
    body:JSON.stringify({key:signingAgent.publicKey,path:operation})});
  assert.equal(response.status, 200);
  const {nonce} = await response.json();
  const request = JSON.stringify({intent}), t = nowSeconds();
  const proof = await signJws({v:1,nonce,iss:approval.grant.id,aud:origin,method:'POST',path:operation,iat:t,exp:t+60,
    request_sha256:await hash(request)}, signingAgent.privateKey, PROOF_TYPE);
  const result = await fetch(origin+operation, {method:'POST',headers:{...headers,Authorization:'Agent '+approval.grant.agent_token},
    body:JSON.stringify({request,proof})});
  return {status:result.status, ...(await result.json())};
}

async function editorFrame(page, windowId) {
  const element = await page.$(selector(windowId)+' iframe');
  const frame = await element.contentFrame();
  await element.dispose();
  return frame;
}

async function native(page, windowId, command, args) {
  const frame = await editorFrame(page, windowId);
  return frame.evaluate(async ({command,args}) => {
    const state = await window.gridcraft.request('ui.state', {});
    return window.gridcraft.request('ui.documentHost',{command,params:args,doc:Number(state.hostDocumentState.active)});
  },{command,args});
}

async function deckCommand(page, windowId, command, args = {}) {
  const frame = await editorFrame(page,windowId);
  return frame.evaluate(async ({command,args}) => {
    const state = await window.deckcraft.request('ui.inspect',{});
    return window.deckcraft.request('engine.execute',{command,params:args,documentId:state.documentId});
  },{command,args});
}

async function photoKeys(page, id, key, modifiers = []) {
  await page.bringToFront();
  await page.evaluate(id=>{
    const desktop=window.desktopLab.surfaces.get('Desktop');
    const target=desktop.windows.find(candidate=>String(candidate.id)===String(id));
    if (desktop.active!==target.id) desktop.activateWindow(target);
  },id);
  const frame = await editorFrame(page,id);
  await frame.evaluate(() => {
    const canvas = document.querySelector('#photocraft_canvas');
    canvas.tabIndex = 0;
    canvas.focus();
  });
  for (const modifier of modifiers) await page.keyboard.down(modifier);
  try { await page.keyboard.press(key); }
  finally { for (const modifier of [...modifiers].reverse()) await page.keyboard.up(modifier); }
  await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

async function graphicsDispatch(page, app) {
  const first = await editor(page,app);
  const native = await editorFrame(page,first);
  const canvas = await native.waitForSelector(`#${app}_canvas`,timeout);
  const bounds = await canvas.boundingBox();
  await canvas.dispose();
  assert(bounds);
  const start = {x:bounds.x+bounds.width*(app==='vectorcraft'?.34:.45),y:bounds.y+bounds.height*.44};
  await page.waitForFunction(({x,y},scope)=>document.elementFromPoint(x,y)===document.querySelector(scope+' iframe'),
    timeout,start,selector(first));
  const painted = () => native.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.mouse.click(start.x,start.y);
  await page.keyboard.press(app==='vectorcraft'?'m':'r');
  await painted();
  await page.mouse.move(start.x,start.y);
  await page.mouse.down();
  await painted();
  await page.mouse.move(start.x+bounds.width*.15,start.y+bounds.height*.18,{steps:10});
  await page.mouse.up();
  await page.waitForFunction(scope=>document.querySelector(scope)?.appView?.lifecycle.snapshot().dirty,timeout,selector(first));

  const second = await editor(page,app);
  const commands = ['document.inspect','layer.rename'];
  async function grant(id) {
    const pending = approve(page,id,commands);
    await page.waitForSelector(modal,timeout);
    await page.click(modal+' button[aria-label="Approve access"]');
    const reply = await pending;
    assert.equal(reply.error,undefined,reply.error);
    return reply.result;
  }
  async function confirm(scope,command,args) {
    const intent = JSON.stringify(intentFor(scope,command,args));
    const reply = await authorize(scope,intent);
    assert.equal(reply.status,200,reply.error);
    return {intent,confirmation:reply.confirmation};
  }
  async function run(scope,command,args) {
    const {intent,confirmation} = await confirm(scope,command,args);
    const reply = await dispatch(page,confirmation,intent);
    assert.equal(reply.error,undefined,reply.error);
    return reply.result.result;
  }
  const drawn = await grant(first), blank = await grant(second);
  const {layers} = await run(drawn,'document.inspect',{});
  const untouched = (await run(blank,'document.inspect',{})).layers;
  const layer = app==='figcraft' ? layers.find(row=>!untouched.some(other=>other.name===row.name)) : layers[0];
  assert(layer,JSON.stringify(layers));
  const rename = {layerId:layer.id,name:'Approved graphics layer'};
  const request = await confirm(drawn,'layer.rename',rename);
  assert.match((await dispatch(page,request.confirmation,request.intent.replace(rename.name,'Changed intent'))).error,/intent changed/i);
  const renamed = await dispatch(page,request.confirmation,request.intent);
  assert.equal(renamed.error,undefined,renamed.error);
  assert.deepEqual(renamed.result.target,drawn.document);
  assert.match((await dispatch(page,request.confirmation,request.intent)).error,/already consumed/i);
  assert.equal((await run(drawn,'document.inspect',{})).layers.find(row=>row.id===layer.id).name,rename.name);
  assert.deepEqual((await run(blank,'document.inspect',{})).layers,untouched);

  await page.evaluate(id=>{
    const desktop = window.desktopLab.surfaces.get('Desktop');
    desktop.activateWindow(desktop.windows.find(candidate=>candidate.id===id));
  },first);
  await native.$eval(`#${app}_canvas`,canvas=>{canvas.tabIndex=0;canvas.focus();});
  await page.keyboard.down('Control');
  try { await page.keyboard.press('z'); }
  finally { await page.keyboard.up('Control'); }
  await painted();
  assert.equal((await run(drawn,'document.inspect',{})).layers.find(row=>row.id===layer.id).name,layer.name);
  present(`${app} applies signed layer rename only in the scoped window and records native Undo`);
}

async function photoDispatch(page) {
  const original = await editor(page,'photocraft');
  await photoKeys(page,original,'n',['Control','Shift']);
  await photoKeys(page,original,'Enter');
  const second = await editor(page,'photocraft');
  const commands = ['document.inspect','layer.rename'];
  assert.match((await approve(page,original,['file.saveAs'])).error,/Unsupported/);
  async function grant(windowId) {
    const pending = approve(page,windowId,commands);
    await page.waitForSelector(modal,timeout);
    await page.click(modal+' button[aria-label="Approve access"]');
    const result = await pending;
    assert.equal(result.error,undefined,result.error);
    return result.result;
  }
  async function confirmed(scope, command, args) {
    const intent=JSON.stringify(intentFor(scope,command,args));
    const signed=await authorize(scope,intent);
    assert.equal(signed.status,200,signed.error);
    return {intent,confirmation:signed.confirmation};
  }
  async function run(scope,command,args) {
    const {confirmation,intent}=await confirmed(scope,command,args);
    const reply=await dispatch(page,confirmation,intent);
    assert.equal(reply.error,undefined,reply.error);
    return reply.result.result;
  }
  const scoped=await grant(original), other=await grant(second);
  const firstState=await run(scoped,'document.inspect',{});
  const layer=firstState.layers.find(node=>node.name!=='Background');
  assert(layer);
  const untouched=await run(other,'document.inspect',{});
  const rename={layerId:layer.id,name:'Delegated visible layer'};
  const request=await confirmed(scoped,'layer.rename',rename);
  assert.match((await dispatch(page,request.confirmation,request.intent.replace(rename.name,'Changed args'))).error,/intent changed/i);
  const changed=await dispatch(page,request.confirmation,request.intent);
  assert.equal(changed.error,undefined,changed.error);
  assert.equal(changed.result.actor.id,scoped.grant.id);
  assert.deepEqual(changed.result.target,scoped.document);
  assert.match((await dispatch(page,request.confirmation,request.intent)).error,/already consumed/i);
  assert.deepEqual(await run(other,'document.inspect',{}),untouched);
  assert.equal(await page.$eval(selector(original),node=>typeof node.appView.execute),'undefined');
  await photoKeys(page,original,'z',['Control']);
  assert.equal((await run(scoped,'document.inspect',{})).layers.find(node=>node.id===layer.id).name,layer.name);
  await run(scoped,'layer.rename',rename);
  present('One signed native layer rename targets an exact PhotoCraft window and remains undoable through the editor');

  await page.evaluate(scope=>{
    const frame=document.querySelector(scope+' iframe');
    globalThis.photoTypeState=null;
    globalThis.addEventListener('message',event=>{
      if (event.source===frame.contentWindow && event.origin===location.origin && event.data?.type==='photocraft:account-project-state') {
        globalThis.photoTypeState=event.data;
      }
    });
  },selector(original));
  await photoKeys(page,original,'t');
  const frame=await editorFrame(page,original);
  const canvas=await frame.$('#photocraft_canvas');
  const box=await canvas.boundingBox();
  await canvas.dispose();
  assert(box);
  const point={x:box.x+Math.max(65,(box.width-230)/2),y:box.y+box.height*0.56};
  await page.waitForFunction(({x,y},scope)=>document.elementFromPoint(x,y)===document.querySelector(scope+' iframe'),
    {timeout:8_000},point,selector(original));
  await page.screenshot({path:path.join(output,'photocraft-type-target.png')});
  await page.mouse.click(point.x,point.y);
  await page.keyboard.type('Human input in progress',{delay:20});
  await page.screenshot({path:path.join(output,'photocraft-type-edit.png')});
  await page.waitForFunction(()=>globalThis.photoTypeState?.unfinishedEdit && globalThis.photoTypeState?.capturable,{timeout:8_000});
  const blocked=await confirmed(scoped,'layer.rename',{...rename,name:'Do not apply'});
  assert.match((await dispatch(page,blocked.confirmation,blocked.intent)).error,/Finish the active PhotoCraft edit/);
  await photoKeys(page,original,'Escape');
  present('A signed layer rename leaves unfinished native Type input under human control');

  const previousBinding=await confirmed(scoped,'document.inspect',{});
  await photoKeys(page,original,'s',['Control']);
  async function clickPicker(label) {
    const handle=await page.waitForFunction(label=>[...document.querySelectorAll('dialog.codi-file-picker[open] button')]
      .find(button=>!button.disabled && [button.getAttribute('aria-label'),button.textContent.trim()].includes(label)),timeout,label);
    try { await handle.asElement().click(); } finally { await handle.dispose(); }
  }
  await clickPicker('Open folder Pictures');
  await clickPicker('Use this folder');
  const savePrompt='dialog.codi-confirm-dialog[open]:has(input)';
  const form=savePrompt+' input';
  await page.waitForSelector(form,timeout);
  assert.equal(await page.$eval(savePrompt+' h2',heading=>heading.textContent),'Save PhotoCraft project');
  await page.$eval(form,input=>{ input.value='Signed layer'; });
  await page.click(savePrompt+' button[aria-label="Save"]');
  const resource='Pictures/Signed layer.pcraft';
  await page.waitForFunction(async (id,resource)=>(await document.querySelector('.window[data-window="'+id+'"]')?.appView?.inspect())?.resourceId===resource,
    timeout,original,resource);
  assert.match((await dispatch(page,previousBinding.confirmation,previousBinding.intent)).error,/outside the live document contract/);

  const filesId=await page.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
  await page.waitForFunction(id=>typeof document.querySelector('.window[data-window="'+id+'"]')?.appView?.execute==='function',timeout,filesId);
  const stored=await page.$eval(selector(filesId),async (node,path)=>{
    const view=node.appView;
    await view.ready;
    await view.execute('list',{path:'Pictures'});
    const {sha256}=await view.execute('snapshot',{path});
    const result=await view.execute('download',{path,expectedRevision:sha256});
    return {sha256,bytes:Array.from(result.data)};
  },resource);
  const bytes=Buffer.from(stored.bytes);
  assert.equal(createHash('sha256').update(bytes).digest('hex'),stored.sha256);
  const file=path.join(output,'signed-layer.pcraft');
  await writeFile(file,bytes,{mode:0o600});
  const program='import json,sys,zipfile; z=zipfile.ZipFile(sys.argv[1]); print(json.dumps([i["name"] for i in json.loads(z.read("manifest.json"))["document"]["layers"]]))';
  const names=JSON.parse(execFileSync('python3',['-c',program,file],{encoding:'utf8'}));
  assert(names.includes(rename.name) && !names.includes('Do not apply'));
  present('Ordinary PhotoCraft Save persists the authorized native change and fences the previous resource grant');
}

async function deckDispatch(browser) {
  const {page,context} = await login(browser);
  try {
    const id = await editor(page,'deckcraft');
    const baseline = await deckCommand(page,id,'document.inspect');
    const original = baseline.slides[0].id;
    await deckCommand(page,id,'slide.new');
    const pending = approve(page,id,['document.inspect','slide.notes']);
    await page.waitForSelector(modal,timeout);
    await page.click(modal+' button[aria-label="Approve access"]');
    const consent = await pending;
    assert.equal(consent.error,undefined,consent.error);
    const a = consent.result;
    const text = 'Agent notes for the original slide';
    const edit = JSON.stringify(intentFor(a,'slide.notes',{slideId:original,text}));
    const signed = await authorize(a,edit);
    assert.equal(signed.status,200,signed.error);
    await deckCommand(page,id,'slide.move',{from:0,to:1});
    const applied = await dispatch(page,signed.confirmation,edit);
    assert.equal(applied.error,undefined,applied.error);
    assert.deepEqual(applied.result.target,a.document);
    const inspect = JSON.stringify(intentFor(a,'document.inspect',{}));
    const inspection = await authorize(a,inspect);
    assert.equal(inspection.status,200,inspection.error);
    const result = await dispatch(page,inspection.confirmation,inspect);
    assert.equal(result.error,undefined,result.error);
    assert.equal(result.result.result.slides[0].notes,'');
    assert.equal(result.result.result.slides[1].id,original);
    assert.equal(result.result.result.slides[1].notes,text);
    const deleted = await authorize(a,edit);
    assert.equal(deleted.status,200,deleted.error);
    await deckCommand(page,id,'slide.delete',{index:1});
    assert.match((await dispatch(page,deleted.confirmation,edit)).error,/unknown slideId/);
    const remaining = await deckCommand(page,id,'document.inspect');
    assert.equal(remaining.slides.length,1);
    assert.equal(remaining.slides[0].notes,'');
    present('signed DeckCraft notes follow the native slide ID through reordering and reject deletion');
  } finally {
    await context.close();
  }
}

async function labelledButton(page, root, label) {
  const handle = await page.waitForFunction((root,label)=>[...document.querySelectorAll(root+' button')].find(button=>
    !button.disabled && !button.hidden && (button.getAttribute('aria-label') === label || button.textContent.trim() === label)),timeout,root,label);
  try { await handle.asElement().click(); }
  finally { await handle.dispose(); }
}

async function lightcraftDispatch(browser, page, credentials) {
  const first = await editor(page,'lightcraft');
  const native = await editorFrame(page,first);
  await native.evaluate(async ()=>{
    const canvas=document.querySelector('#lightcraft_canvas');
    canvas.tabIndex=0;
    canvas.focus({preventScroll:true});
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  });
  await page.keyboard.press('Escape');
  await native.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const checksInFrame = await native.evaluate(async () => {
    const canvas = document.querySelector('#lightcraft_canvas');
    const source = document.createElement('canvas');
    source.width = source.height = 40;
    const ctx = source.getContext('2d');
    ctx.fillStyle = '#dc387e';
    ctx.fillRect(0,0,40,40);
    const photo = await new Promise(resolve=>source.toBlob(resolve,'image/png'));
    const transfer = new DataTransfer();
    transfer.items.add(new File([photo],'Account swatch.png',{type:'image/png'}));
    canvas.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));
    return {scope:new URL(location.href).searchParams.get('scope'),photoBytes:photo.size};
  });
  assert.match(checksInFrame.scope,/^[0-9a-f]{64}$/);
  assert(checksInFrame.photoBytes>0);
  await page.waitForFunction(id=>{
    const state=document.querySelector('.window[data-window="'+id+'"]')?.appView.lifecycle.snapshot();
    return state?.dirty && !state.pending;
  },timeout,first);

  async function grant(tab,id) {
    const pending = approve(tab,id,['document.inspect','photo.rate']);
    await tab.waitForSelector(modal,timeout);
    await tab.click(modal+' button[aria-label="Approve access"]');
    const reply = await pending;
    assert.equal(reply.error,undefined,reply.error);
    return reply.result;
  }
  async function run(tab,scope,command,args) {
    const intent = JSON.stringify(intentFor(scope,command,args));
    const auth = await authorize(scope,intent);
    assert.equal(auth.status,200,auth.error);
    const reply = await dispatch(tab,auth.confirmation,intent);
    assert.equal(reply.error,undefined,reply.error);
    return reply.result.result;
  }
  const draft = await grant(page,first);
  const blank = await editor(page,'lightcraft');
  const blankGrant = await grant(page,blank);
  assert.equal((await run(page,blankGrant,'document.inspect',{})).photoCount,0);
  const photos = await run(page,draft,'document.inspect',{});
  assert.equal(photos.photoCount,1);
  const [photo] = photos.photos;
  assert.equal(photo.name,'Account swatch.png');
  await run(page,draft,'photo.rate',{ids:[photo.id],rating:4});
  assert.equal((await run(page,draft,'document.inspect',{})).photos[0].rating,4);
  present('LightCraft imports a PNG through the native editor and applies an explicitly scoped native rating');
  await labelledButton(page,selector(blank),'Close');
  await page.waitForSelector(selector(blank),{hidden:true});
  await page.evaluate(id=>{
    const desktop=window.desktopLab.surfaces.get('Desktop');
    desktop.activateWindow(desktop.windows.find(candidate=>candidate.id===id));
  },first);

  async function saveAs(label, name) {
    await labelledButton(page,selector(first),label);
    const picker='dialog.codi-file-picker[open]', prompt='dialog.codi-confirm-dialog[open]';
    await labelledButton(page,picker,'Open folder Documents');
    await labelledButton(page,picker,'Use this folder');
    await page.waitForSelector(prompt+' input',timeout);
    await page.$eval(prompt+' input',(field,value)=>{field.value=value;},name);
    await labelledButton(page,prompt,'Save');
    await page.waitForFunction((id,title)=>{
      const view=document.querySelector('.window[data-window="'+id+'"]');
      const state=view?.appView.lifecycle.snapshot();
      return view?.querySelector('.caption-text')?.textContent===title && !state?.dirty && !state?.pending;
    },timeout,first,name+'.lightcraft — LightCraft');
  }
  await saveAs('Save','Light Lab');
  const named = await grant(page,first);
  await run(page,named,'photo.rate',{ids:[photo.id],rating:5});
  await labelledButton(page,selector(first),'Save');
  await page.waitForFunction(id=>{
    const state=document.querySelector('.window[data-window="'+id+'"]')?.appView.lifecycle.snapshot();
    return state && !state.dirty && !state.pending;
  },timeout,first);
  await saveAs('Save As','Light Copy');
  present('LightCraft confirms account Save and Save As and updates the active canonical name');

  const copy = await grant(page,first);
  await run(page,copy,'photo.rate',{ids:[photo.id],rating:2});
  await page.waitForFunction(async ()=>{
    const name='webos-lightcraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db=>db.name===name)) return false;
    const db=await new Promise((resolve,reject)=>{
      const request=indexedDB.open(name);
      request.onsuccess=()=>resolve(request.result);
      request.onerror=()=>reject(request.error);
    });
    try {
      const rows=await new Promise((resolve,reject)=>{
        const request=db.transaction('drafts').objectStore('drafts').getAll();
        request.onsuccess=()=>resolve(request.result);
        request.onerror=()=>reject(request.error);
      });
      return rows.some(row=>row.path==='Documents/Light Copy.lightcraft' && row.bytes instanceof Blob && row.bytes.size>0);
    } finally { db.close(); }
  },timeout);
  const accept = dialog=>{ void dialog.accept(); };
  page.on('dialog',accept);
  try { await page.reload({waitUntil:'domcontentloaded'}); }
  finally { page.off('dialog',accept); }
  await page.waitForFunction(id=>document.querySelector('.window[data-window="'+id+'"]')?.appView?.inspect?.()?.instanceId,timeout,first);
  const recovered=await grant(page,first);
  assert.equal((await run(page,recovered,'document.inspect',{})).photos[0].rating,2);
  await labelledButton(page,selector(first),'Close');
  await labelledButton(page,'dialog.webos-lightcraft-session[open]','Discard');
  await page.waitForSelector(selector(first),{hidden:true,timeout:120_000});
  present('LightCraft refresh recovers the edited native catalog and Discard finalizes only the recovered view');

  const fresh = await login(browser,credentials);
  try {
    await fresh.page.evaluate(()=>{
      window.lightcraftOriginalReads = [];
      window.addEventListener('message',event=>{
        if (event.origin===location.origin && event.data?.type==='lightcraft:account-original-read') {
          window.lightcraftOriginalReads.push(event.data.digest);
        }
      });
    });
    const filesId=await fresh.page.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    await fresh.page.waitForFunction(id=>typeof document.querySelector('.window[data-window="'+id+'"]')?.appView?.execute==='function',timeout,filesId);
    await fresh.page.$eval(selector(filesId),async node=>{
      await node.appView.ready;
      await node.appView.execute('list',{path:'Documents'});
      await node.appView.execute('open',{path:'Documents/Light Copy.lightcraft'});
    });
    const windowId=await fresh.page.waitForFunction(path=>window.desktopLab.surfaces.get('Desktop').windows.find(window=>
      window.app==='lightcraft' && document.querySelector('.window[data-window="'+window.id+'"]')?.appView?.inspect?.()?.resourceId===path)?.id,
    timeout,'Documents/Light Copy.lightcraft');
    const newId=await windowId.jsonValue();
    await windowId.dispose();
    await fresh.page.waitForFunction(id=>document.querySelector('.window[data-window="'+id+'"]')?.appView?.inspect?.()?.instanceId,timeout,newId);
    const opened=await grant(fresh.page,newId);
    const contents=await run(fresh.page,opened,'document.inspect',{});
    assert.equal(contents.photos[0].rating,5);
    assert.equal(contents.photos[0].name,'Account swatch.png');
    const view=await editorFrame(fresh.page,newId);
    await view.waitForFunction(()=>document.querySelector('#lightcraft_canvas')?.width>0,timeout);
    await fresh.page.waitForFunction(()=>window.lightcraftOriginalReads.length>0,timeout);
    const canvas=await view.$('#lightcraft_canvas');
    try {
      let pixels=0;
      for (let attempt=0;attempt<24 && pixels<100;attempt++) {
        const screenshot=await canvas.screenshot({encoding:'base64'});
        pixels=await view.evaluate(async png=>{
          const bytes=Uint8Array.from(atob(png),character=>character.charCodeAt(0));
          const image=await createImageBitmap(new Blob([bytes],{type:'image/png'}));
          const buffer=new OffscreenCanvas(image.width,image.height);
          const context=buffer.getContext('2d');
          context.drawImage(image,0,0);
          const {data}=context.getImageData(0,0,image.width,image.height);
          image.close();
          let matching=0;
          for(let offset=0;offset<data.length;offset+=4) {
            if(Math.abs(data[offset]-220)<8 && Math.abs(data[offset+1]-56)<8 && Math.abs(data[offset+2]-126)<8) matching++;
          }
          return matching;
        },screenshot);
        if (pixels<100) await view.evaluate(()=>new Promise(resolve=>setTimeout(resolve,250)));
      }
      assert(pixels>=100,`The reopened original was not painted (${pixels} swatch pixels).`);
    } finally { await canvas.dispose(); }
    present('A fresh browser opens the LightCraft copy through Files, retrieves and renders the detached original, and sees the saved rating');
  } finally { await fresh.context.close(); }
}

let browser;
try {
  browser = await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true,args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],
    defaultViewport:{width:1540,height:960}
  });
  if (lightOnly) {
    const {page,context,credentials} = await login(browser);
    try { await lightcraftDispatch(browser,page,credentials); }
    catch (error) {
      await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
      await writeFile(path.join(output,'result.json'),JSON.stringify({status:'FAIL',checks,error:error.message},null,2)+'\n',{mode:0o600});
      throw error;
    }
    finally { await context.close(); }
  }
  if (!lightOnly && !disabled && graphicsOnly) {
    for (const app of graphics) {
      const {page,context} = await login(browser);
      try { await graphicsDispatch(page,app); }
      finally { await context.close(); }
    }
  }
  if (!lightOnly && !disabled && !graphicsOnly && photoProfile) {
    const {page,context} = await login(browser);
    try { await photoDispatch(page); }
    finally { await context.close(); }
  }
  const {page,context} = !lightOnly && (disabled || officeProfile && !graphicsOnly) ? await login(browser) : {};
  if (!lightOnly && disabled) {
    assert.equal(await page.evaluate(() => window.desktopLab.agentOperations === undefined), true);
    present('default server profile has no agent bridge');
  } else if (!lightOnly && officeProfile && !graphicsOnly) {
    const first = await editor(page,'gridcraft');
    const second = await editor(page,'gridcraft');
    const commands = ['document.inspect','cell.get','cell.set'];
    assert.match((await approve(page,first,['file.saveAs'])).error,/Unsupported/);
    const denied = approve(page,first,commands);
    await page.waitForSelector(modal,timeout);
    await page.$eval(modal+' button[aria-label="Approve access"]',button=>button.click());
    assert(await page.$(modal),'Synthetic click must not count as consent.');
    await page.click(modal+' button[aria-label="Cancel"]');
    assert.match((await denied).error,/cancelled/);
    assert.deepEqual(await page.evaluate(() => window.desktopLab.agentOperations.list()),{delegations:[]});
    present('only the trusted owner click authorizes an allowed native command scope');

    const pending = approve(page,first,commands);
    await page.waitForSelector(modal,timeout);
    await page.click(modal+' button[aria-label="Approve access"]');
    const consent = await pending;
    assert.equal(consent.error,undefined,consent.error);
    const a = consent.result;
    assert.equal(a.grant.scope.commands.length,3);
    const listed = await page.evaluate(() => window.desktopLab.agentOperations.list());
    assert.equal(listed.delegations[0]?.id,a.grant.id);
    assert(!JSON.stringify(listed).includes(a.grant.agent_token));
    const before = await native(page, first, 'document.inspect', {});
    const sheet = before.sheets[0].name;
    const args = {sheet,cell:'A1',input:'=7*6'};
    const setting = intentFor(a,'cell.set',args), intent = JSON.stringify(setting);
    assert.equal((await authorize(a,intent,otherAgent)).status,401);
    const signed = await authorize(a,intent);
    assert.equal(signed.status,200,signed.error);
    assert.match((await dispatch(page,signed.confirmation,intent.replace('7*6','7*7'))).error,/intent changed/i);
    const captured = await dispatch(page,signed.confirmation,intent);
    assert.equal(captured.error,undefined,captured.error);
    assert.equal(captured.result.actor.id,a.grant.id);
    assert.deepEqual(captured.result.target,a.document);
    assert.equal((await native(page,first,'cell.get',{sheet,cell:'A1'})).value,42);
    assert.equal((await native(page,second,'cell.get',{sheet,cell:'A1'})).type,'empty');
    assert.match((await dispatch(page,signed.confirmation,intent)).error,/already consumed/i);
    present('independent agent key edits one live WASM workbook exactly once');

    const reading = JSON.stringify(intentFor(a,'cell.get',{sheet,cell:'A1'}));
    const readGrant = await authorize(a,reading);
    assert.equal(readGrant.status,200,readGrant.error);
    const {page:other,context:otherContext} = await login(browser);
    assert.match((await dispatch(other,readGrant.confirmation,reading)).error,/no longer available/);
    await otherContext.close();
    await page.bringToFront();
    const read = await dispatch(page,readGrant.confirmation,reading);
    assert.equal(read.error,undefined,read.error);
    assert.equal(read.result.result.formula,'=7*6');
    const inspectIntent = JSON.stringify(intentFor(a,'document.inspect',{}));
    const inspectGrant = await authorize(a,inspectIntent);
    assert.equal(inspectGrant.status,200,inspectGrant.error);
    assert.equal((await dispatch(page,inspectGrant.confirmation,inspectIntent)).result.result.sheets[0].name,sheet);
    present('a separate browser account cannot consume or read the owner’s grant');

    const wrongSheet = JSON.stringify(intentFor(a,'cell.set',{cell:'A1',input:'999'}));
    const incomplete = await authorize(a,wrongSheet);
    assert.equal(incomplete.status,200,incomplete.error);
    assert.match((await dispatch(page,incomplete.confirmation,wrongSheet)).error,/outside the live document contract/);
    const unapproved = JSON.stringify(intentFor(a,'file.saveAs',{path:'Documents/agent.xlsx'}));
    assert.equal((await authorize(a,unapproved)).status,403);
    const blanket = await page.$eval(selector(first), (node,request) =>
      node.appView.execute(request,{}).then(()=>null,error=>error.message), setting.request);
    assert.match(blanket,/denied/i);
    present('arguments require an explicit sheet and direct calls cannot borrow human file authority');

    const frame = await editorFrame(page,first);
    await frame.evaluate(() => window.gridcraft.request('ui.edit.begin',{text:'=12*12'}));
    const whileEditing = await authorize(a,intent);
    assert.equal(whileEditing.status,200,whileEditing.error);
    assert.match((await dispatch(page,whileEditing.confirmation,intent)).error,/Finish the active GridCraft edit/);
    const edit = await frame.evaluate(() => window.gridcraft.request('ui.inspect',{}));
    assert.equal(edit.editor.text,'=12*12');
    assert.equal((await native(page,first,'cell.get',{sheet,cell:'A1'})).value,42);
    await frame.evaluate(() => window.gridcraft.request('ui.edit.cancel',{}));
    present('a signed edit preserves the owner’s unfinished native formula');

    const oldBinding = await authorize(a,reading);
    assert.equal(oldBinding.status,200,oldBinding.error);
    const raceIntent = JSON.stringify(intentFor(a,'cell.set',{sheet,cell:'A1',input:'999'}));
    const raceGrant = await authorize(a,raceIntent);
    assert.equal(raceGrant.status,200,raceGrant.error);
    const connection = await page.createCDPSession();
    try {
      await connection.send('Fetch.enable',{patterns:[{urlPattern:origin+'/api/v1/agents/consume'}]});
      const intercepted = new Promise((resolve,reject) => {
        const deadline = setTimeout(() => reject(Error('Operation consume did not reach the server.')),8000);
        connection.once('Fetch.requestPaused', ({requestId}) => {clearTimeout(deadline);resolve(requestId);});
      });
      const running = dispatch(page,raceGrant.confirmation,raceIntent);
      const requestId = await intercepted;
      await native(page,first,'file.saveAs',{path:'Documents/approved.xlsx'});
      await page.waitForFunction(async id => (await document.querySelector('.window[data-window="'+id+'"]')?.appView?.inspect())?.resourceId === 'Documents/approved.xlsx', {timeout:8000}, first);
      await connection.send('Fetch.continueRequest',{requestId});
      assert.match((await running).error,/no longer available/);
      assert.equal((await native(page,first,'cell.get',{sheet,cell:'A1'})).value,42);
    } finally {
      await connection.detach();
    }
    assert.match((await dispatch(page,oldBinding.confirmation,reading)).error,/outside the live document contract/);
    const nextApproval = approve(page,first,commands);
    await page.waitForSelector(modal,timeout);
    await page.click(modal+' button[aria-label="Approve access"]');
    const next = await nextApproval;
    assert.equal(next.error,undefined,next.error);
    const after = next.result;
    const updated = JSON.stringify(intentFor(after,'cell.get',{sheet,cell:'A1'}));
    const toRevoke = await authorize(after,updated);
    assert.equal(toRevoke.status,200,toRevoke.error);
    assert.equal((await page.evaluate(id => window.desktopLab.agentOperations.revoke(id),after.grant.id)).revoked,true);
    assert.match((await dispatch(page,toRevoke.confirmation,updated)).error,/unavailable|revoked/i);
    present('Save As fences in-flight and unused grants and revocation fences issued grants');
  }
  await context?.close();
  if (!lightOnly && !disabled && !graphicsOnly && officeProfile) await deckDispatch(browser);
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks},null,2)+'\n',{mode:0o600});
} finally {
  await browser?.close();
}
