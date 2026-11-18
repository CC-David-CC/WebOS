import assert from 'node:assert/strict';
import {createHash, randomBytes} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
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
const selected = Object.entries({
  lightcraft:lightcraftDispatch, designcraft:designcraftDispatch,
  soundcraft:soundcraftDispatch, filmcraft:filmcraftDispatch,
  effectcraft:effectcraftDispatch, cadcraft:cadcraftDispatch,
}).filter(([app])=>process.env['WEBOS_'+app.toUpperCase()+'_TEST']==='1');
assert(selected.length<=1);
const singleEditor = selected[0];
const soundOnly = singleEditor?.[0]==='soundcraft';
const graphics = ['figcraft','vectorcraft','anicraft'].filter(app=>apps.includes(app));
assert(singleEditor ? apps.includes(singleEditor[0]) : graphicsOnly ? graphics.length : disabled || photoProfile || officeProfile);
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
  if (soundOnly) await observeSoundOutput(page);
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
    if (['photocraft','figcraft','vectorcraft','anicraft','lightcraft','designcraft','soundcraft','filmcraft','effectcraft','cadcraft'].includes(app)) return model?.instanceId ? 'ready' : false;
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

async function designcraftDispatch(browser, page, credentials) {
  const artworkFixture=process.env.WEBOS_DESIGNCRAFT_ARTWORK_FIXTURE;
  const commands=['document.inspect','frame.create','edit.undo',...(artworkFixture ? ['links.relink','pdf.export'] : [])];
  const authorizeEditor=async (tab,id)=>{
    const pending=approve(tab,id,commands);
    await tab.waitForSelector(modal,timeout);
    await tab.click(modal+' button[aria-label="Approve access"]');
    const approved=await pending;
    assert.equal(approved.error,undefined,approved.error);
    return approved.result;
  };
  async function edit(tab,grant,command,args={}) {
    const intent=JSON.stringify(intentFor(grant,command,args));
    const signed=await authorize(grant,intent);
    assert.equal(signed.status,200,signed.error);
    const reply=await dispatch(tab,signed.confirmation,intent);
    assert.equal(reply.error,undefined,reply.error);
    return reply.result.result;
  }
  const id=await editor(page,'designcraft');
  const initial=await authorizeEditor(page,id);
  const count=(await edit(page,initial,'document.inspect')).stories;
  await edit(page,initial,'frame.create',{rect:[48,52,355,215],text:'Account publication'});
  assert.equal((await edit(page,initial,'document.inspect')).stories,count+1);
  await edit(page,initial,'edit.undo');
  assert.equal((await edit(page,initial,'document.inspect')).stories,count);
  await edit(page,initial,'frame.create',{rect:[48,52,355,215],text:'Account publication'});
  present('DesignCraft starts in Desktop and authorized frame creation and Undo use the native editor');

  const frame=await editorFrame(page,id);
  async function saveAs(name,copy) {
    await page.bringToFront();
    await frame.$eval('#designcraft_canvas',canvas=>{canvas.tabIndex=0;canvas.focus({preventScroll:true});});
    await page.keyboard.down('Control');
    if (copy) await page.keyboard.down('Shift');
    try { await page.keyboard.press(copy ? 'S' : 's'); }
    finally {
      if (copy) await page.keyboard.up('Shift');
      await page.keyboard.up('Control');
    }
    const picker='dialog.codi-file-picker[open]', prompt='dialog.codi-confirm-dialog[open]';
    await labelledButton(page,picker,'Open folder Documents');
    await labelledButton(page,picker,'Use this folder');
    await page.waitForSelector(prompt+' input',timeout);
    await page.$eval(prompt+' input',(field,value)=>{field.value=value;},name);
    await labelledButton(page,prompt,'Save');
    await page.waitForFunction((view,title)=>{
      const window=document.querySelector(view);
      const state=window?.appView?.lifecycle.snapshot();
      return state && !state.dirty && !state.pending && window.querySelector('.caption-text')?.textContent===title;
    },timeout,selector(id),name+'.designcraft — DesignCraft');
  }
  await saveAs('Catalog',false);
  await saveAs('Catalog Copy',true);
  present('The native DesignCraft Save and Save As commands adopt the confirmed account path');

  const named=await authorizeEditor(page,id);
  await edit(page,named,'frame.create',{rect:[52,246,340,415],text:'Recovered publication edit'});
  await page.waitForFunction(async ()=>{
    const store='webos-designcraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db=>db.name===store)) return false;
    const db=await new Promise((resolve,reject)=>{
      const request=indexedDB.open(store);
      request.onsuccess=()=>resolve(request.result);
      request.onerror=()=>reject(request.error);
    });
    try {
      const rows=await new Promise((resolve,reject)=>{
        const request=db.transaction('drafts').objectStore('drafts').getAll();
        request.onsuccess=()=>resolve(request.result);
        request.onerror=()=>reject(request.error);
      });
      return rows.some(row=>row.path==='Documents/Catalog Copy.designcraft' && row.bytes instanceof Blob && row.bytes.size>0);
    } finally { db.close(); }
  },timeout);
  const accept=dialog=>{void dialog.accept();};
  page.on('dialog',accept);
  try { await page.reload({waitUntil:'domcontentloaded'}); }
  finally { page.off('dialog',accept); }
  await page.waitForFunction(view=>document.querySelector(view)?.appView?.inspect?.()?.instanceId,timeout,selector(id));
  const recovered=await authorizeEditor(page,id);
  const recoveredState=await edit(page,recovered,'document.inspect');
  assert.equal(recoveredState.stories,count+2);
  assert.equal(recoveredState.dirty,true);
  await labelledButton(page,selector(id),'Close');
  await labelledButton(page,'dialog.webos-designcraft-session[open]','Discard');
  await page.waitForSelector(selector(id),{hidden:true,timeout:120_000});
  present('DesignCraft restores the local unpublished edit after refresh and discards only the recovered view');

  const fresh=await login(browser,credentials);
  try {
    const files=await fresh.page.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    await fresh.page.waitForFunction(view=>typeof document.querySelector(view)?.appView?.execute==='function',timeout,selector(files));
    await fresh.page.$eval(selector(files),async window=>{
      await window.appView.ready;
      await window.appView.execute('list',{path:'Documents'});
      await window.appView.execute('open',{path:'Documents/Catalog Copy.designcraft'});
    });
    const target=await fresh.page.waitForFunction(()=>[...document.querySelectorAll('.window[data-window]')].find(window=>
      window.appView?.inspect?.()?.resourceId==='Documents/Catalog Copy.designcraft')?.dataset.window,timeout);
    const opened=await authorizeEditor(fresh.page,await target.jsonValue());
    await target.dispose();
    const saved=await edit(fresh.page,opened,'document.inspect');
    assert.equal(saved.stories,count+1);
    assert.equal(saved.dirty,false);
    present('A fresh DesignCraft browser opens the saved publication from Files');
    if (artworkFixture) await designcraftArtwork(browser,fresh,credentials,files,artworkFixture,authorizeEditor,edit);
  } finally { await fresh.context.close(); }
}

async function designcraftArtwork(browser, session, credentials, files, fixture, authorizeEditor, edit) {
  assert(path.isAbsolute(fixture));
  const publication='Linked Publication.designcraft', original='Press Original.png';
  const resource='Documents/'+publication;
  const fixtures=await Promise.all([publication,original].map(async name=>({name,bytes:[...await readFile(path.join(fixture,name))]})));
  await session.page.$eval(selector(files), (window,fixtures)=>{
    const transfer=new DataTransfer();
    for (const {name,bytes} of fixtures) transfer.items.add(new File([Uint8Array.from(bytes)],name));
    const files=window.querySelector('.webos-files-browser');
    files.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));
  },fixtures);
  await session.page.waitForFunction(view=>document.querySelector(view+' .webos-files-status')?.textContent.includes('Saved 2 files'),timeout,selector(files));

  async function open(tab,filesId) {
    await tab.waitForFunction(view=>typeof document.querySelector(view)?.appView?.execute==='function',timeout,selector(filesId));
    await tab.$eval(selector(filesId),async (window,resource)=>{
      await window.appView.ready;
      await window.appView.execute('list',{path:'Documents'});
      await window.appView.execute('open',{path:resource});
    },resource);
    const target=await tab.waitForFunction(resource=>[...document.querySelectorAll('.window[data-window]')].find(window=>
      window.appView?.inspect?.()?.resourceId===resource)?.dataset.window,timeout,resource);
    try { return await target.jsonValue(); }
    finally { await target.dispose(); }
  }
  const id=await open(session.page,files);
  const grant=await authorizeEditor(session.page,id);
  const [missing]= (await edit(session.page,grant,'document.inspect')).graphics;
  assert.equal(missing.name,'Missing image.png');
  assert.deepEqual(missing.pixels,[48,32]);
  assert.match(missing.storage,/^linked$/i);
  await edit(session.page,grant,'links.relink',{asset:missing.id});
  const picker='dialog.codi-file-picker[open]';
  await labelledButton(session.page,picker,'Open folder Documents');
  await labelledButton(session.page,picker,'Choose file '+original);
  await session.page.waitForFunction(view=>{
    const state=document.querySelector(view)?.appView.lifecycle.snapshot();
    return state?.dirty && !state.pending;
  },timeout,selector(id));
  const [embedded]= (await edit(session.page,grant,'document.inspect')).graphics;
  assert.equal(embedded.id,missing.id);
  assert.equal(embedded.name,original);
  assert.deepEqual(embedded.pixels,[192,128]);
  assert.match(embedded.storage,/^embedded$/i);

  await session.page.bringToFront();
  const canvas=await editorFrame(session.page,id);
  await canvas.$eval('#designcraft_canvas',node=>{node.tabIndex=0;node.focus({preventScroll:true});});
  await session.page.keyboard.down('Control');
  try { await session.page.keyboard.press('s'); }
  finally { await session.page.keyboard.up('Control'); }
  await session.page.waitForFunction(view=>{
    const state=document.querySelector(view)?.appView.lifecycle.snapshot();
    return state && !state.dirty && !state.pending;
  },timeout,selector(id));
  present('DesignCraft selects a missing graphic’s full original through the account picker and saves it embedded');

  const cold=await login(browser,credentials);
  try {
    const filesId=await cold.page.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    const id=await open(cold.page,filesId);
    const grant=await authorizeEditor(cold.page,id);
    assert.deepEqual((await edit(cold.page,grant,'document.inspect')).graphics,[embedded]);
    const downloads=path.join(output,'pdf-export');
    await mkdir(downloads,{mode:0o700});
    const cdp=await browser.target().createCDPSession();
    let timer;
    try {
      await cdp.send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloads,browserContextId:cold.context.id,eventsEnabled:true});
      const completed=new Promise((resolve,reject)=>{
        timer=setTimeout(()=>reject(Error('The native DesignCraft PDF did not download.')),45_000);
        let handle;
        cdp.on('Browser.downloadWillBegin',event=>{handle=event;});
        cdp.on('Browser.downloadProgress',event=>{
          if (event.guid===handle?.guid && event.state==='completed') resolve(handle.suggestedFilename);
        });
      });
      const [name,exported]=await Promise.all([completed,edit(cold.page,grant,'pdf.export')]);
      assert.equal(name,'Linked Publication.pdf');
      const pdf=await readFile(path.join(downloads,name));
      assert.equal(pdf.length,exported.bytes);
      assert.equal(pdf.subarray(0,4).toString(),'%PDF');
      const headers=pdf.toString('latin1').split(/\d+\s+\d+\s+obj\b/).map(object=>object.split(/\bstream[\r\n]/,1)[0]);
      assert(headers.some(header=>/\/Subtype\s*\/Image\b/.test(header) && /\/Width\s+192\b/.test(header) && /\/Height\s+128\b/.test(header)),
        'The PDF must include the full-size artwork image.');
      present('Cold DesignCraft reopen exports a downloaded PDF with the full-resolution account artwork');
    } finally { clearTimeout(timer); await cdp.detach(); }
  } finally { await cold.context.close(); }
}

function soundFixture() {
  const rate = 48_000;
  const frames = rate / 10;
  const bytes = Buffer.alloc(44 + frames * 2);
  bytes.write('RIFF',0);
  bytes.writeUInt32LE(bytes.length - 8,4);
  bytes.write('WAVEfmt ',8);
  bytes.writeUInt32LE(16,16);
  bytes.writeUInt16LE(1,20);
  bytes.writeUInt16LE(1,22);
  bytes.writeUInt32LE(rate,24);
  bytes.writeUInt32LE(rate * 2,28);
  bytes.writeUInt16LE(2,32);
  bytes.writeUInt16LE(16,34);
  bytes.write('data',36);
  bytes.writeUInt32LE(frames * 2,40);
  for (let i=0; i<frames; i++) bytes.writeInt16LE(i % 48 < 24 ? 8192 : -8192,44 + i * 2);
  return {bytes, rate, frames};
}

async function observeSoundOutput(page) {
  await page.evaluateOnNewDocument(()=>{
    if (location.pathname !== '/soundcraft/index.html' || typeof AudioNode === 'undefined') return;
    const connect = AudioNode.prototype.connect;
    const outputs = new WeakSet();
    window.soundcraftTestAudio = {peak:0};
    AudioNode.prototype.connect = function(destination,...params) {
      const result = connect.call(this,destination,...params);
      if (destination !== this.context.destination || outputs.has(this)) return result;
      outputs.add(this);
      const analyser = this.context.createAnalyser();
      analyser.fftSize = 512;
      connect.call(this,analyser);
      const signal = new Float32Array(analyser.fftSize);
      setInterval(()=>{
        analyser.getFloatTimeDomainData(signal);
        for (const sample of signal) window.soundcraftTestAudio.peak = Math.max(window.soundcraftTestAudio.peak,Math.abs(sample));
      },15);
      return result;
    };
  });
}

async function soundcraftDispatch(browser, page, credentials) {
  const app = 'soundcraft';
  const track = 'Authorized voice track';
  const copy = 'Documents/Account mix copy.scraftz';
  const first = await editor(page,app);
  const commands = ['document.inspect','track.new','edit.undo'];
  async function grant(tab,id) {
    const pending = approve(tab,id,commands);
    await tab.waitForSelector(modal,timeout);
    await tab.click(modal+' button[aria-label="Approve access"]');
    const approved = await pending;
    assert.equal(approved.error,undefined,approved.error);
    return approved.result;
  }
  async function edit(tab,approval,command,args={}) {
    const intent = JSON.stringify(intentFor(approval,command,args));
    const signed = await authorize(approval,intent);
    assert.equal(signed.status,200,signed.error);
    const result = await dispatch(tab,signed.confirmation,intent);
    assert.equal(result.error,undefined,result.error);
    return result.result.result;
  }
  const approval = await grant(page,first);
  const initial = await edit(page,approval,'document.inspect');
  assert.equal(initial.dirty,false);
  await edit(page,approval,'track.new',{name:track});
  assert((await edit(page,approval,'document.inspect')).tracks.some(row=>row.name===track));
  await edit(page,approval,'edit.undo');
  assert.deepEqual((await edit(page,approval,'document.inspect')).tracks,initial.tracks);
  await edit(page,approval,'track.new',{name:track});
  present('SoundCraft scoped track creation and Undo use the native engine');

  const fixture = soundFixture();
  const native = await editorFrame(page,first);
  const previous = await page.$eval(selector(first),node=>node.appView.lifecycle.snapshot().revision);
  await native.$eval('#soundcraft_canvas',(canvas,bytes)=>{
    const transfer = new DataTransfer();
    transfer.items.add(new File([Uint8Array.from(bytes)],'Account tone.wav',{type:'audio/wav'}));
    canvas.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));
  },[...fixture.bytes]);
  await page.waitForFunction((view,revision)=>{
    const state = document.querySelector(view)?.appView?.lifecycle.snapshot();
    return state?.dirty && state.revision !== revision;
  },timeout,selector(first),previous);

  const press = async (tab,id,key,shift=false)=>{
    const frame = await editorFrame(tab,id);
    await tab.bringToFront();
    await frame.$eval('#soundcraft_canvas',canvas=>{canvas.tabIndex=0;canvas.focus({preventScroll:true});});
    await tab.keyboard.down('Control');
    if (shift) await tab.keyboard.down('Shift');
    try { await tab.keyboard.press(key); }
    finally {
      if (shift) await tab.keyboard.up('Shift');
      await tab.keyboard.up('Control');
    }
  };
  const picker = 'dialog.codi-file-picker[open]', prompt = 'dialog.codi-confirm-dialog[open]';
  async function saveAs(tab,id,name,copy) {
    await press(tab,id,copy ? 'S' : 's',copy);
    await labelledButton(tab,picker,'Open folder Documents');
    await labelledButton(tab,picker,'Use this folder');
    await tab.waitForSelector(prompt+' input',timeout);
    await tab.$eval(prompt+' input',(field,value)=>{field.value=value;},name);
    await labelledButton(tab,prompt,'Save');
    await tab.waitForFunction((view,title)=>{
      const node = document.querySelector(view);
      const state = node?.appView?.lifecycle.snapshot();
      return state && !state.dirty && !state.pending && node.querySelector('.caption-text')?.textContent===title;
    },timeout,selector(id),name+'.scraftz — SoundCraft');
  }

  async function accountFiles(tab) {
    const id = await tab.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    await tab.waitForFunction(view=>typeof document.querySelector(view)?.appView?.execute==='function',timeout,selector(id));
    await invoke(tab,id,'list',{path:'Documents'});
    return id;
  }
  async function invoke(tab,id,command,args) {
    return tab.$eval(selector(id),async (node,{command,args})=>{
      await node.appView.ready;
      return node.appView.execute(command,args);
    },{command,args});
  }
  async function validateAudio(tab,id,resource,label) {
    await invoke(tab,id,'list',{path:resource.slice(0,resource.lastIndexOf('/'))});
    const revision = (await invoke(tab,id,'snapshot',{path:resource})).sha256;
    const downloaded = await invoke(tab,id,'download',{path:resource,expectedRevision:revision});
    const bytes = Buffer.from(Object.values(downloaded.data));
    assert.equal(createHash('sha256').update(bytes).digest('hex'),revision);
    const artifact = path.join(output,label+'.scraftz');
    await writeFile(artifact,bytes,{mode:0o600,flag:'wx'});
    const files = execFileSync('unzip',['-Z1',artifact],{encoding:'utf8'}).trim().split('\n');
    const audio = files.filter(file=>file.startsWith('Audio Files/') && file.endsWith('.wav'));
    assert.equal(audio.length,1);
    const wave = execFileSync('unzip',['-p',artifact,audio[0]]);
    assert.equal(wave.toString('ascii',0,4),'RIFF');
    assert.equal(wave.toString('ascii',8,12),'WAVE');
    const chunks = new Map();
    for (let cursor=12; cursor+8<=wave.length;) {
      const size = wave.readUInt32LE(cursor+4);
      assert(cursor+8+size<=wave.length);
      chunks.set(wave.toString('ascii',cursor,cursor+4),wave.subarray(cursor+8,cursor+8+size));
      cursor += 8 + size + (size & 1);
    }
    const format = chunks.get('fmt '), samples = chunks.get('data');
    assert.equal(format.readUInt16LE(2),1);
    assert.equal(format.readUInt32LE(4),fixture.rate);
    assert.equal(format.readUInt16LE(14),32);
    assert.equal(samples.length,fixture.frames * 4);
    for (let i=0; i<fixture.frames; i++) assert(Math.abs(samples.readFloatLE(i * 4) - (i % 48 < 24 ? .25 : -.25)) < .00001);
    return revision;
  }
  await saveAs(page,first,'Account mix',false);
  await saveAs(page,first,'Account mix copy',true);
  const files = await accountFiles(page);
  const firstRevision = await validateAudio(page,files,copy,'confirmed');
  present('Native audio import and confirmed Save and Save As preserve all 4,800 WAV samples');

  await press(page,first,'o');
  await labelledButton(page,picker,'Open folder Documents');
  await labelledButton(page,picker,'Choose file Account mix copy.scraftz');
  await page.waitForSelector(picker,{hidden:true,...timeout});
  assert.equal(await page.$$eval('.window:has(.webos-soundcraft)',nodes=>nodes.length),1);
  present('Native Open activates the existing portable account project');

  const named = await grant(page,first);
  await edit(page,named,'track.new',{name:'Saved percussion'});
  await page.waitForFunction(view=>document.querySelector(view)?.appView?.lifecycle.snapshot().dirty,timeout,selector(first));
  await press(page,first,'s');
  await page.waitForFunction(view=>{
    const state = document.querySelector(view)?.appView?.lifecycle.snapshot();
    return state && !state.dirty && !state.pending;
  },timeout,selector(first));
  const revision = await validateAudio(page,files,copy,'ordinary-save');
  assert.notEqual(revision,firstRevision);
  present('Ordinary native Save advances the bound account revision and preserves the audio');

  await edit(page,named,'track.new',{name:'Unsaved percussion'});
  await page.waitForFunction(async resource=>{
    const store = 'webos-soundcraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db=>db.name===store)) return false;
    const db = await new Promise((resolve,reject)=>{
      const request = indexedDB.open(store);
      request.onsuccess = ()=>resolve(request.result);
      request.onerror = ()=>reject(request.error);
    });
    try {
      const rows = await new Promise((resolve,reject)=>{
        const read = db.transaction('drafts').objectStore('drafts').getAll();
        read.onsuccess = ()=>resolve(read.result);
        read.onerror = ()=>reject(read.error);
      });
      return rows.some(row=>row.path===resource && row.bytes instanceof Blob && row.bytes.size>0);
    } finally { db.close(); }
  },timeout,copy);
  const accept = dialog=>{void dialog.accept();};
  page.on('dialog',accept);
  try { await page.reload({waitUntil:'domcontentloaded'}); }
  finally { page.off('dialog',accept); }
  await page.waitForFunction(view=>document.querySelector(view)?.appView?.inspect?.()?.instanceId,timeout,selector(first));
  const recovered = await edit(page,await grant(page,first),'document.inspect');
  assert(recovered.dirty && recovered.tracks.some(row=>row.name==='Unsaved percussion'));
  await labelledButton(page,selector(first),'Close');
  await labelledButton(page,'dialog.webos-soundcraft-session[open]','Discard');
  await page.waitForSelector(selector(first),{hidden:true,...timeout});
  present('Refreshing recovers the edited SoundCraft bundle and discard preserves the saved version');

  const fresh = await login(browser,credentials);
  try {
    const id = await accountFiles(fresh.page);
    await invoke(fresh.page,id,'open',{path:copy});
    const target = await fresh.page.waitForFunction(resource=>[...document.querySelectorAll('.window[data-window]')].find(node=>
      node.appView?.inspect?.()?.resourceId===resource)?.dataset.window,timeout,copy);
    const reopened = await target.jsonValue();
    await target.dispose();
    const state = await edit(fresh.page,await grant(fresh.page,reopened),'document.inspect');
    assert(!state.dirty && state.tracks.some(row=>row.name===track) && state.tracks.some(row=>row.name==='Saved percussion') &&
      !state.tracks.some(row=>row.name==='Unsaved percussion'));
    assert.equal(await validateAudio(fresh.page,id,copy,'fresh-context'),revision);
    const view = await editorFrame(fresh.page,reopened);
    await fresh.page.bringToFront();
    await view.$eval('#soundcraft_canvas',canvas=>{canvas.tabIndex=0;canvas.focus({preventScroll:true});});
    await fresh.page.keyboard.press('Space');
    await view.waitForFunction(()=>window.soundcraftTestAudio?.peak > .05,{timeout:30_000});
    present('Playback of the reopened project produces the expected signal through Chromium WebAudio');
    await saveAs(fresh.page,reopened,'Reopened mix',true);
    await validateAudio(fresh.page,id,'Documents/Reopened mix.scraftz','reopened-and-saved');
    await labelledButton(fresh.page,selector(reopened),'Close');
    await fresh.page.waitForSelector(selector(reopened),{hidden:true,...timeout});
    present('A fresh browser opens from Files and the reopened engine can resave the same audio samples');
  } finally { await fresh.context.close(); }
}

async function filmcraftDispatch(browser, page, credentials) {
  const folder = process.env.WEBOS_FILMCRAFT_MEDIA_FIXTURE;
  assert(path.isAbsolute(folder));
  const fixture = JSON.parse(await readFile(path.join(folder,'receipt.json'),'utf8'));
  const video = await readFile(path.join(folder,fixture.filename));
  assert.equal(createHash('sha256').update(video).digest('hex'),fixture.sha256);
  const first = await editor(page,'filmcraft');
  const commands = ['document.inspect','file.newSequence','edit.undo'];
  async function grant(tab,id) {
    const pending = approve(tab,id,commands);
    await tab.waitForSelector(modal,timeout);
    await tab.click(modal+' button[aria-label="Approve access"]');
    const approved = await pending;
    assert.equal(approved.error,undefined,approved.error);
    return approved.result;
  }
  async function execute(tab,approval,command,args={}) {
    const intent = JSON.stringify(intentFor(approval,command,args));
    const signed = await authorize(approval,intent);
    assert.equal(signed.status,200,signed.error);
    const reply = await dispatch(tab,signed.confirmation,intent);
    assert.equal(reply.error,undefined,reply.error);
    return reply.result.result;
  }
  const approval = await grant(page,first);
  const blank = await execute(page,approval,'document.inspect');
  assert.equal(blank.sequenceCount,0);
  await execute(page,approval,'file.newSequence',{name:'Browser cut'});
  assert.equal((await execute(page,approval,'document.inspect')).sequenceCount,1);
  await execute(page,approval,'edit.undo');
  assert.equal((await execute(page,approval,'document.inspect')).sequenceCount,0);
  await execute(page,approval,'file.newSequence',{name:'Browser cut'});
  present('FilmCraft runs the native editor and authorized sequence creation and Undo');

  const frame = await editorFrame(page,first);
  const beforeImport = await page.$eval(selector(first),node=>node.appView.lifecycle.snapshot().revision);
  await frame.$eval('#filmcraft_canvas',(canvas,{bytes,name})=>{
    const transfer = new DataTransfer();
    transfer.items.add(new File([Uint8Array.from(bytes)],name,{type:'video/webm'}));
    canvas.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));
  },{bytes:[...video],name:fixture.filename});
  await page.waitForFunction((view,revision)=>{
    const state = document.querySelector(view)?.appView?.lifecycle.snapshot();
    return state?.dirty && !state.pending && state.revision !== revision;
  },timeout,selector(first),beforeImport);
  assert.equal((await execute(page,approval,'document.inspect')).mediaCount,1);

  const picker = 'dialog.codi-file-picker[open]', prompt = 'dialog.codi-confirm-dialog[open]';
  async function controlKey(key,shift=false) {
    await page.bringToFront();
    await frame.$eval('#filmcraft_canvas',canvas=>{canvas.tabIndex=0;canvas.focus({preventScroll:true});});
    await page.keyboard.down('Control');
    if (shift) await page.keyboard.down('Shift');
    try { await page.keyboard.press(key); }
    finally {
      if (shift) await page.keyboard.up('Shift');
      await page.keyboard.up('Control');
    }
  }
  async function save(name,copy) {
    await controlKey(copy ? 'S' : 's',copy);
    await labelledButton(page,picker,'Open folder Video');
    await labelledButton(page,picker,'Use this folder');
    await page.waitForSelector(prompt+' input',timeout);
    await page.$eval(prompt+' input',(field,value)=>{field.value=value;},name);
    await labelledButton(page,prompt,'Save');
    await page.waitForFunction((view,title)=>{
      const node = document.querySelector(view);
      const state = node?.appView?.lifecycle.snapshot();
      return state && !state.dirty && !state.pending && node.querySelector('.caption-text')?.textContent===title;
    },timeout,selector(first),name+'.fcproj — FilmCraft');
  }
  await save('Browser cut',false);
  await save('Browser cut copy',true);
  const resource = 'Video/Browser cut copy.fcproj';
  const original = 'Video/FilmCraft Originals/'+fixture.sha256+'.original';
  async function applyFile(tab,id,command,args) {
    return tab.$eval(selector(id),async (node,{command,args})=>{
      await node.appView.ready;
      return node.appView.execute(command,args);
    },{command,args});
  }
  async function files(tab) {
    const id = await tab.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    await tab.waitForFunction(view=>typeof document.querySelector(view)?.appView?.execute==='function',timeout,selector(id));
    return id;
  }
  async function download(tab,id,object) {
    await applyFile(tab,id,'list',{path:object.slice(0,object.lastIndexOf('/'))});
    const bound = await applyFile(tab,id,'snapshot',{path:object});
    const data = await applyFile(tab,id,'download',{path:object,expectedRevision:bound.sha256});
    const contents = Buffer.from(Object.values(data.data));
    assert.equal(createHash('sha256').update(contents).digest('hex'),bound.sha256);
    return contents;
  }
  const ownFiles = await files(page);
  assert.deepEqual(await download(page,ownFiles,original),video);
  const saved = (await download(page,ownFiles,resource)).toString('utf8');
  assert(saved.includes('/files/webos-originals/'+fixture.sha256+'/'+fixture.filename));
  assert(JSON.parse(saved).view);
  const prior = JSON.parse((await download(page,ownFiles,'Video/Browser cut.fcproj')).toString('utf8'));
  assert.equal(prior.project.name,'Browser cut');
  assert.equal(JSON.parse(saved).project.name,'Browser cut copy');
  present('FilmCraft native Save and Save As confirm editable projects with the video stored under its input hash');

  await controlKey('o');
  await labelledButton(page,picker,'Open folder Video');
  await labelledButton(page,picker,'Choose file Browser cut copy.fcproj');
  await page.waitForSelector(picker,{hidden:true,...timeout});
  assert.equal(await page.$$eval('.window:has(.webos-filmcraft)',nodes=>nodes.length),1);
  present('Native Open activates the existing FilmCraft window for the same account project');

  const named = await grant(page,first);
  await execute(page,named,'file.newSequence',{name:'Recovered alternate cut'});
  await page.waitForFunction(async resource=>{
    const database = 'webos-filmcraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db=>db.name===database)) return false;
    const db = await new Promise((resolve,reject)=>{
      const open = indexedDB.open(database);
      open.onsuccess = ()=>resolve(open.result);
      open.onerror = ()=>reject(open.error);
    });
    try {
      const records = await new Promise((resolve,reject)=>{
        const read = db.transaction('drafts').objectStore('drafts').getAll();
        read.onsuccess = ()=>resolve(read.result);
        read.onerror = ()=>reject(read.error);
      });
      return records.some(record=>record.path===resource && record.bytes instanceof Blob && record.bytes.size>0);
    } finally { db.close(); }
  },timeout,resource);
  const handleUnload = dialog=>{void dialog.accept();};
  page.on('dialog',handleUnload);
  try { await page.reload({waitUntil:'domcontentloaded'}); }
  finally { page.off('dialog',handleUnload); }
  await page.waitForFunction(view=>document.querySelector(view)?.appView?.inspect?.()?.instanceId,timeout,selector(first));
  const restored = await execute(page,await grant(page,first),'document.inspect');
  assert(restored.dirty && restored.sequenceCount===2 && restored.mediaCount===1);
  await labelledButton(page,selector(first),'Close');
  await labelledButton(page,'dialog.webos-filmcraft-session[open]','Discard');
  await page.waitForSelector(selector(first),{hidden:true,...timeout});
  present('Refreshing restores the edited project and linked media while discard preserves the server revision');

  const fresh = await login(browser,credentials);
  try {
    await fresh.page.evaluate(()=>{
      window.filmcraftTestOriginalReads = [];
      addEventListener('message',event=>{
        if (event.origin===location.origin && event.data?.type==='filmcraft:account-original-read') {
          window.filmcraftTestOriginalReads.push(event.data.digest);
        }
      });
    });
    const id = await files(fresh.page);
    await applyFile(fresh.page,id,'list',{path:'Video'});
    await applyFile(fresh.page,id,'open',{path:resource});
    const target = await fresh.page.waitForFunction(resource=>[...document.querySelectorAll('.window[data-window]')].find(node=>
      node.appView?.inspect?.()?.resourceId===resource)?.dataset.window,timeout,resource);
    const reopened = await target.jsonValue();
    await target.dispose();
    assert.deepEqual(await fresh.page.evaluate(()=>window.filmcraftTestOriginalReads),[fixture.sha256]);
    const loaded = await execute(fresh.page,await grant(fresh.page,reopened),'document.inspect');
    assert.equal(loaded.sequenceCount,1);
    assert.equal(loaded.mediaCount,1);
    assert.equal(loaded.dirty,false);
    await fresh.page.screenshot({path:path.join(output,'filmcraft-fresh-browser.png')});
    present('A fresh browser opens the saved native FilmCraft project and requests the matching original from account storage');
    const iframe = await fresh.page.$(selector(reopened)+' iframe');
    assert(iframe);
    try {
      async function swatches(upper) {
        const png = await iframe.screenshot({encoding:'base64'});
        return fresh.page.evaluate(async ({png,upper})=>{
          const bytes = Uint8Array.from(atob(png),value=>value.charCodeAt(0));
          const decoded = await createImageBitmap(new Blob([bytes],{type:'image/png'}));
          const canvas = document.createElement('canvas');
          canvas.width = decoded.width;
          canvas.height = decoded.height;
          const context = canvas.getContext('2d');
          context.drawImage(decoded,0,0);
          decoded.close();
          const half = Math.floor(canvas.height/2);
          const columns = upper ? canvas.width : Math.floor(canvas.width/3);
          const skip = upper ? 0 : half;
          const {data} = context.getImageData(0,skip,columns,half);
          let red=0, yellow=0, x=0, y=0;
          for (let i=0;i<data.length;i+=4) {
            const [r,g,b] = [data[i],data[i+1],data[i+2]];
            if (r > 150 && g < 110 && b < 125 && r > g * 1.7) red++;
            if (r < 180 || g < 155 || b > 155 || r < b * 1.6 || g < b * 1.4) continue;
            yellow++;
            x += (i/4) % columns;
            y += Math.floor(i/4/columns) + skip;
          }
          return {red,yellow,x:x/Math.max(1,yellow),y:y/Math.max(1,yellow),
            width:canvas.width,height:canvas.height};
        },{png,upper});
      }
      let thumbnail;
      for (let retry=0; retry<12; retry++) {
        thumbnail = await swatches(false);
        if (thumbnail.red>800 && thumbnail.yellow>80) break;
        await fresh.page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,250)));
      }
      assert(thumbnail.red>800 && thumbnail.yellow>80,'Expected the decoded account video thumbnail.');
      const rect = await iframe.boundingBox();
      assert(rect);
      const x = rect.x+thumbnail.x*rect.width/thumbnail.width;
      const y = rect.y+thumbnail.y*rect.height/thumbnail.height;
      await fresh.page.bringToFront();
      await fresh.page.mouse.click(x,y);
      await new Promise(resolve=>setTimeout(resolve,65));
      await fresh.page.mouse.click(x,y);
      let source;
      for (let retry=0; retry<12; retry++) {
        source = await swatches(true);
        if (source.red>800 && source.yellow>80) break;
        await fresh.page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,250)));
      }
      await fresh.page.screenshot({path:path.join(output,'filmcraft-decoded-source.png')});
      assert(source.red>800 && source.yellow>80,'Expected the decoded source in the native monitor.');
      present('The fresh browser decodes the stored video and shows its test colors in the native Source Monitor');
      // In the fixed test viewport, use Source Monitor's More menu and its native export dialog.
      const rendered = ()=>fresh.page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      await fresh.page.mouse.click(rect.x+rect.width*.28,rect.y+rect.height*.556);
      await rendered();
      await fresh.page.mouse.click(rect.x+rect.width*.33,rect.y+rect.height*.715);
      await rendered();
      await iframe.screenshot({path:path.join(output,'filmcraft-native-export-dialog.png')});
      const downloads = path.join(output,'filmcraft-exports');
      await mkdir(downloads,{mode:0o700});
      const cdp = await browser.target().createCDPSession();
      let timer;
      try {
        await cdp.send('Browser.setDownloadBehavior',{
          behavior:'allow',downloadPath:downloads,browserContextId:fresh.context.id,eventsEnabled:true,
        });
        const completed = new Promise((resolve,reject)=>{
          timer = setTimeout(()=>reject(Error('The FilmCraft Source Monitor frame did not download.')),30_000);
          let handle;
          cdp.on('Browser.downloadWillBegin',event=>{handle=event;});
          cdp.on('Browser.downloadProgress',event=>{
            if (event.guid===handle?.guid && event.state==='completed') resolve(handle.suggestedFilename);
          });
        });
        await fresh.page.mouse.click(rect.x+rect.width*.675,rect.y+rect.height*.579);
        const filename = await completed;
        assert.equal(filename,'FilmCraft color clip.png');
        const png = await readFile(path.join(downloads,filename));
        assert.equal(png.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
        assert.equal(png.readUInt32BE(16),fixture.width);
        assert.equal(png.readUInt32BE(20),fixture.height);
        const colors = await fresh.page.evaluate(async encoded=>{
          const bytes = Uint8Array.from(atob(encoded),value=>value.charCodeAt(0));
          const image = await createImageBitmap(new Blob([bytes],{type:'image/png'}));
          const canvas = document.createElement('canvas');
          canvas.width=image.width; canvas.height=image.height;
          const context = canvas.getContext('2d');
          context.drawImage(image,0,0);
          image.close();
          return [[20,20],[80,48]].map(([x,y])=>Array.from(context.getImageData(x,y,1,1).data));
        },png.toString('base64'));
        assert(colors[0][0]>150 && colors[0][1]<115 && colors[0][2]<125);
        assert(colors[1][0]>200 && colors[1][1]>175 && colors[1][2]<155);
        present('FilmCraft exports a full-resolution PNG of the reopened source with the expected pixels');
      } finally {
        clearTimeout(timer);
        await cdp.detach();
      }
    } finally { await iframe.dispose(); }
  } finally { await fresh.context.close(); }
}

async function cadcraftDispatch(browser,page,credentials) {
  const commands=['document.inspect','line','circle','dimlinear','edit.undo'];
  const picker='dialog.codi-file-picker[open]', prompt='dialog.codi-confirm-dialog[open]';
  const appWindow='.window:has(.webos-cadcraft)';
  const nativeCanvas='#cadcraft_canvas';
  const original='Documents/Dimensioned drawing.dxf';
  const copy='Documents/Dimensioned copy.dxf';

  async function grant(tab,id) {
    const pending=approve(tab,id,commands);
    await tab.waitForSelector(modal,timeout);
    await tab.click(modal+' button[aria-label="Approve access"]');
    const approval=await pending;
    assert.equal(approval.error,undefined,approval.error);
    return approval.result;
  }
  async function edit(tab,approval,command,args={}) {
    const intent=JSON.stringify(intentFor(approval,command,args));
    const signed=await authorize(approval,intent);
    assert.equal(signed.status,200,signed.error);
    const result=await dispatch(tab,signed.confirmation,intent);
    assert.equal(result.error,undefined,result.error);
    return result.result.result;
  }
  async function files(tab) {
    const id=await tab.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    await tab.waitForFunction(view=>typeof document.querySelector(view)?.appView?.execute==='function',timeout,selector(id));
    return id;
  }
  async function file(tab,id,command,args) {
    return tab.$eval(selector(id),async (node,{command,args})=>{
      await node.appView.ready;
      return node.appView.execute(command,args);
    },{command,args});
  }
  async function read(tab,id,path) {
    await file(tab,id,'list',{path:path.slice(0,path.lastIndexOf('/'))});
    const snapshot=await file(tab,id,'snapshot',{path});
    const data=await file(tab,id,'download',{path,expectedRevision:snapshot.sha256});
    const bytes=Buffer.from(Object.values(data.data));
    assert.equal(createHash('sha256').update(bytes).digest('hex'),snapshot.sha256);
    return bytes;
  }
  async function shortcut(tab,id,key,shift=false) {
    await tab.bringToFront();
    await tab.evaluate(id=>{
      const surface=window.desktopLab.surfaces.get('Desktop');
      surface.activateWindow(surface.windows.find(window=>String(window.id)===String(id)));
    },id);
    const frame=await editorFrame(tab,id);
    await frame.$eval(nativeCanvas,canvas=>{canvas.tabIndex=0;canvas.focus({preventScroll:true});});
    await tab.keyboard.down('Control');
    if (shift) await tab.keyboard.down('Shift');
    try { await tab.keyboard.press(key); }
    finally {
      if (shift) await tab.keyboard.up('Shift');
      await tab.keyboard.up('Control');
    }
  }
  async function bound(tab,id,title) {
    await tab.waitForFunction((view,title)=>{
      const node=document.querySelector(view);
      const state=node?.appView?.lifecycle.snapshot();
      return state && !state.dirty && !state.pending && node.querySelector('.caption-text')?.textContent===title+' — CADCraft';
    },timeout,selector(id),title);
  }
  async function saveAs(tab,id,name,copy) {
    await shortcut(tab,id,copy?'S':'s',copy);
    await labelledButton(tab,picker,'Open folder Documents');
    await labelledButton(tab,picker,'Use this folder');
    await tab.waitForSelector(prompt+' input',timeout);
    await tab.$eval(prompt+' input',(field,value)=>{field.value=value;},name);
    await labelledButton(tab,prompt,'Save');
    await bound(tab,id,name+'.dxf');
  }
  function dxfEntities(bytes) {
    const lines=bytes.toString('utf8').trimEnd().split(/\r?\n/);
    assert.equal(lines.length%2,0);
    let inEntities=false;
    const entities=[];
    for (let i=0;i<lines.length;i+=2) {
      const code=Number(lines[i].trim()), value=lines[i+1].trim();
      if (code===2 && value==='ENTITIES') {inEntities=true; continue;}
      if (!inEntities) continue;
      if (code===0 && value==='ENDSEC') break;
      if (code===0) entities.push({type:value,fields:new Map()});
      else if (entities.length) entities.at(-1).fields.set(code,value);
    }
    return entities;
  }

  const first=await editor(page,'cadcraft');
  const frame=await editorFrame(page,first);
  await frame.waitForSelector(nativeCanvas,timeout);
  assert.equal(await frame.evaluate(()=>typeof window.cadcraft),'undefined');
  const approval=await grant(page,first);
  assert.equal((await edit(page,approval,'document.inspect')).entityCount,0);
  await edit(page,approval,'line',{points:[[1,2],[7,2]]});
  await edit(page,approval,'circle',{center:[9,4],radius:2});
  const dimension={p1:[1,2],p2:[7,2],at:[4,5]};
  await edit(page,approval,'dimlinear',dimension);
  assert.equal((await edit(page,approval,'document.inspect')).entityCount,3);
  await edit(page,approval,'edit.undo');
  assert.equal((await edit(page,approval,'document.inspect')).entityCount,2);
  await edit(page,approval,'dimlinear',dimension);
  present('CADCraft runs scoped native line, circle, dimension and Undo commands');

  const filesId=await files(page);
  await saveAs(page,first,'Dimensioned drawing',false);
  const saved=await read(page,filesId,original);
  const entities=dxfEntities(saved);
  assert.deepEqual(entities.map(entity=>entity.type),['LINE','CIRCLE','DIMENSION']);
  const numeric=(index,codes)=>codes.map(code=>Number(entities[index].fields.get(code)));
  assert.deepEqual(numeric(0,[10,20,11,21]),[1,2,7,2]);
  assert.deepEqual(numeric(1,[10,20,40]),[9,4,2]);
  assert.deepEqual(numeric(2,[13,23,14,24]),[1,2,7,2]);
  await saveAs(page,first,'Dimensioned copy',true);
  assert.deepEqual(dxfEntities(await read(page,filesId,copy)),entities);
  assert.deepEqual(await read(page,filesId,original),saved);
  present('CADCraft Save and Save As write editable DXF with the expected coordinates, radius and dimension');

  await shortcut(page,first,'o');
  await labelledButton(page,picker,'Open folder Documents');
  await labelledButton(page,picker,'Choose file Dimensioned copy.dxf');
  await page.waitForSelector(picker,{hidden:true,...timeout});
  assert.equal(await page.$$eval(appWindow,nodes=>nodes.length),1);
  await file(page,filesId,'open',{path:copy});
  assert.equal(await page.$$eval(appWindow,nodes=>nodes.length),1);
  present('CADCraft native Open and Files reuse the same account drawing window');

  await edit(page,await grant(page,first),'circle',{center:[23,5],radius:3});
  await page.waitForFunction(async path=>{
    const name='webos-cadcraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db=>db.name===name)) return false;
    const db=await new Promise((resolve,reject)=>{
      const open=indexedDB.open(name);
      open.onsuccess=()=>resolve(open.result);
      open.onerror=()=>reject(open.error);
    });
    try {
      const drafts=await new Promise((resolve,reject)=>{
        const request=db.transaction('drafts').objectStore('drafts').getAll();
        request.onsuccess=()=>resolve(request.result);
        request.onerror=()=>reject(request.error);
      });
      return drafts.some(draft=>draft.path===path && draft.bytes instanceof Blob && draft.bytes.size>0);
    } finally {db.close();}
  },timeout,copy);
  const accept=dialog=>{void dialog.accept();};
  page.on('dialog',accept);
  try {await page.reload({waitUntil:'domcontentloaded'});}
  finally {page.off('dialog',accept);}
  await page.waitForFunction(view=>document.querySelector(view)?.appView?.inspect?.()?.instanceId,timeout,selector(first));
  const recovered=await edit(page,await grant(page,first),'document.inspect');
  assert.deepEqual([recovered.entityCount,recovered.dirty],[4,true]);
  await labelledButton(page,selector(first),'Close');
  await labelledButton(page,'dialog.webos-cadcraft-session[open]','Discard');
  await page.waitForSelector(selector(first),{hidden:true,...timeout});
  present('CADCraft restores an unsaved native geometry edit on refresh and supports explicit discard');

  const fresh=await login(browser,credentials);
  try {
    const freshFiles=await files(fresh.page);
    await file(fresh.page,freshFiles,'list',{path:'Documents'});
    await file(fresh.page,freshFiles,'open',{path:copy});
    const view=appWindow+' iframe:not([inert])';
    const frameElement=await fresh.page.waitForSelector(view,timeout);
    const reopened=await fresh.page.$eval(appWindow,node=>node.dataset.window);
    const native=await frameElement.contentFrame();
    await native.waitForSelector(nativeCanvas,timeout);
    const freshApproval=await grant(fresh.page,reopened);
    const drawing=await edit(fresh.page,freshApproval,'document.inspect');
    assert.deepEqual([drawing.entityCount,drawing.dirty],[3,false]);
    assert.deepEqual(dxfEntities(await read(fresh.page,freshFiles,copy)),entities);
    await labelledButton(fresh.page,selector(reopened),'Maximize');
    await fresh.page.waitForFunction(view=>document.querySelector(view)?.getBoundingClientRect().width>1000,timeout,view);
    const expanded=await fresh.page.waitForSelector(view,timeout);
    await expanded.screenshot({path:path.join(output,'cadcraft-reopened-drawing.png')});
    await expanded.dispose();
    const previousRevision=(await file(fresh.page,freshFiles,'snapshot',{path:copy})).sha256;
    await edit(fresh.page,freshApproval,'line',{points:[[19,9],[24,10]]});
    await shortcut(fresh.page,reopened,'s');
    await fresh.page.waitForFunction((id,revision)=>{
      const target=window.desktopLab.surfaces.get('Desktop').windows.find(window=>String(window.id)===String(id));
      return target?.launchContext?.sha256 && target.launchContext.sha256!==revision;
    },timeout,reopened,previousRevision);
    await bound(fresh.page,reopened,'Dimensioned copy.dxf');
    assert.equal(dxfEntities(await read(fresh.page,freshFiles,copy)).length,4);
    present('CADCraft reopens editable account geometry from Files in a fresh browser and saves a later revision');
  } finally {
    await fresh.context.close();
  }
}

async function effectcraftDispatch(browser,page,credentials) {
  const commands = ['document.inspect','comp.new','edit.undo'];
  const picker = 'dialog.codi-file-picker[open]', prompt = 'dialog.codi-confirm-dialog[open]';
  const fixtureName = 'EffectCraft color plate.png';
  const bytes = await page.evaluate(async () => {
    const plate = document.createElement('canvas');
    plate.width=160;
    plate.height=96;
    const ctx=plate.getContext('2d');
    ctx.fillStyle='#dd2040'; ctx.fillRect(0,0,160,96);
    ctx.fillStyle='#ffd830'; ctx.fillRect(60,24,40,48);
    const blob=await new Promise(resolve=>plate.toBlob(resolve,'image/png'));
    return [...new Uint8Array(await blob.arrayBuffer())];
  });
  const digest=createHash('sha256').update(Buffer.from(bytes)).digest('hex');
  const sentinel = 'files%2Fstandalone-account-boundary.png';
  await page.evaluate(async ({sentinel,bytes}) => {
    const root=await navigator.storage.getDirectory();
    const folder=await root.getDirectoryHandle('effectcraft',{create:true});
    const file=await folder.getFileHandle(sentinel,{create:true});
    const write=await file.createWritable();
    await write.write(Uint8Array.from(bytes));
    await write.close();
  },{sentinel,bytes});

  async function grant(tab,id) {
    const pending=approve(tab,id,commands);
    await tab.waitForSelector(modal,timeout);
    await tab.click(modal+' button[aria-label="Approve access"]');
    const approval=await pending;
    assert.equal(approval.error,undefined,approval.error);
    return approval.result;
  }
  async function edit(tab,approval,command,args={}) {
    const intent=JSON.stringify(intentFor(approval,command,args));
    const signed=await authorize(approval,intent);
    assert.equal(signed.status,200,signed.error);
    const result=await dispatch(tab,signed.confirmation,intent);
    assert.equal(result.error,undefined,result.error);
    return result.result.result;
  }
  async function files(tab) {
    const id=await tab.evaluate(()=>window.desktopLab.surfaces.get('Desktop').launch('files').id);
    await tab.waitForFunction(view=>typeof document.querySelector(view)?.appView?.execute==='function',timeout,selector(id));
    return id;
  }
  async function file(tab,id,command,args) {
    return tab.$eval(selector(id),async (node,{command,args})=>{
      await node.appView.ready;
      return node.appView.execute(command,args);
    },{command,args});
  }
  async function read(tab,id,resource) {
    await file(tab,id,'list',{path:resource.slice(0,resource.lastIndexOf('/'))});
    const snapshot=await file(tab,id,'snapshot',{path:resource});
    const data=await file(tab,id,'download',{path:resource,expectedRevision:snapshot.sha256});
    const result=Buffer.from(Object.values(data.data));
    assert.equal(createHash('sha256').update(result).digest('hex'),snapshot.sha256);
    return result;
  }
  const first=await editor(page,'effectcraft');
  const approval=await grant(page,first);
  const frame=await editorFrame(page,first);
  assert.equal(await frame.evaluate(()=>typeof window.effectcraft),'undefined');
  assert.equal(await page.$eval(selector(first)+' .webos-effectcraft', root =>
    Array.from(root.querySelectorAll('button')).some(button=>!button.hidden && button.textContent==='AutoSave')),false);
  const original=await edit(page,approval,'document.inspect');
  assert.deepEqual([original.compositionCount,original.mediaCount,original.dirty],[0,0,false]);
  const composition={name:'Linked account composition',width:160,height:96};
  await edit(page,approval,'comp.new',composition);
  assert.equal((await edit(page,approval,'document.inspect')).compositionCount,1);
  await edit(page,approval,'edit.undo');
  assert.equal((await edit(page,approval,'document.inspect')).compositionCount,0);
  await edit(page,approval,'comp.new',composition);
  present('EffectCraft starts blank and runs an authorized native composition edit and Undo');

  const before=await page.$eval(selector(first),node=>node.appView.lifecycle.snapshot().revision);
  await frame.$eval('#effectcraft_canvas',(canvas,{bytes,fixtureName})=>{
    const transfer=new DataTransfer();
    transfer.items.add(new File([Uint8Array.from(bytes)],fixtureName,{type:'image/png'}));
    canvas.dispatchEvent(new DragEvent('drop',{dataTransfer:transfer,bubbles:true,cancelable:true}));
  },{bytes,fixtureName});
  await page.waitForFunction((view,before)=>{
    const state=document.querySelector(view)?.appView?.lifecycle.snapshot();
    return state?.dirty && !state.pending && state.revision!==before;
  },timeout,selector(first),before);
  assert.equal((await edit(page,approval,'document.inspect')).mediaCount,1);
  const filesId=await files(page);
  assert.deepEqual(await read(page,filesId,'Video/EffectCraft Originals/'+digest+'.original'),Buffer.from(bytes));
  const standalone=await page.evaluate(async sentinel=>{
    const root=await navigator.storage.getDirectory();
    const folder=await root.getDirectoryHandle('effectcraft');
    const folders=[];
    for await (const name of root.keys()) folders.push(name);
    const entries=[];
    for await (const name of folder.keys()) entries.push(name);
    const file=await (await folder.getFileHandle(sentinel)).getFile();
    return {entries,folders,bytes:[...new Uint8Array(await file.arrayBuffer())],
      databases:(await indexedDB.databases()).map(row=>row.name)};
  },sentinel);
  assert.deepEqual(standalone.entries,[sentinel]);
  assert.deepEqual(standalone.bytes,bytes);
  assert(!standalone.folders.some(name=>name.startsWith('effectcraft-')));
  assert(!standalone.databases.some(name=>name.startsWith('effectcraft')));
  assert.doesNotMatch(await page.$eval(selector(first)+' .webos-effectcraft [role="status"]',status=>status.textContent),
    /could not update the browser draft/);
  await page.screenshot({path:path.join(output,'effectcraft-native-import.png')});
  present('A native media drop stores the verified account original without touching standalone browser storage');

  const importedView=await page.$(selector(first)+' iframe');
  try {
    const rect=await importedView.boundingBox();
    assert(rect);
    const revision=await page.$eval(selector(first),node=>node.appView.lifecycle.snapshot().revision);
    // Drag the footage row in the Project panel into the visible composition.
    await page.mouse.move(rect.x+rect.width*.16,rect.y+rect.height*.253);
    await page.mouse.down();
    try {
      await page.mouse.move(rect.x+rect.width*.50,rect.y+rect.height*.34,{steps:12});
    } finally { await page.mouse.up(); }
    await page.waitForFunction((view,revision)=>
      document.querySelector(view)?.appView?.lifecycle.snapshot()?.revision!==revision,
    timeout,selector(first),revision);
    await importedView.screenshot({path:path.join(output,'effectcraft-added-composition-layer.png')});
  } finally { await importedView.dispose(); }

  async function controlKey(key,shift=false) {
    await page.bringToFront();
    await page.evaluate(id=>{
      const desktop=window.desktopLab.surfaces.get('Desktop');
      const target=desktop.windows.find(candidate=>String(candidate.id)===String(id));
      if (desktop.active!==target.id) desktop.activateWindow(target);
    },first);
    await frame.$eval('#effectcraft_canvas',canvas=>{canvas.tabIndex=0;canvas.focus({preventScroll:true});});
    await page.keyboard.down('Control');
    if (shift) await page.keyboard.down('Shift');
    try { await page.keyboard.press(key); }
    finally {
      if (shift) await page.keyboard.up('Shift');
      await page.keyboard.up('Control');
    }
  }
  async function save(name,copy) {
    await controlKey(copy?'S':'s',copy);
    await labelledButton(page,picker,'Open folder Video');
    await labelledButton(page,picker,'Use this folder');
    await page.waitForSelector(prompt+' input',timeout);
    await page.$eval(prompt+' input',(field,value)=>{field.value=value;},name);
    await labelledButton(page,prompt,'Save');
    await page.waitForFunction((view,title)=>{
      const node=document.querySelector(view);
      const state=node?.appView?.lifecycle.snapshot();
      return state && !state.dirty && !state.pending && node.querySelector('.caption-text')?.textContent===title;
    },timeout,selector(first),name+'.ecproj — EffectCraft');
  }
  await save('Composition',false);
  await save('Composition copy',true);
  const resource='Video/Composition copy.ecproj';
  const saved=(await read(page,filesId,resource)).toString('utf8');
  assert(saved.includes('/files/webos-originals/'+digest+'/'+fixtureName));
  assert(saved.includes(composition.name));
  present('Native Save and Save As preserve the editable composition and its linked footage');

  await controlKey('o');
  await labelledButton(page,picker,'Open folder Video');
  await labelledButton(page,picker,'Choose file Composition copy.ecproj');
  await page.waitForSelector(picker,{hidden:true,...timeout});
  assert.equal(await page.$$eval('.window:has(.webos-effectcraft)',nodes=>nodes.length),1);
  present('Native Open activates the existing EffectCraft window for the same account project');

  await edit(page,await grant(page,first),'comp.new',{...composition,name:'Recovered alternate'});
  await page.waitForFunction(async resource=>{
    const name='webos-effectcraft-recovery-v1';
    if (!(await indexedDB.databases()).some(db=>db.name===name)) return false;
    const db=await new Promise((resolve,reject)=>{
      const open=indexedDB.open(name);
      open.onsuccess=()=>resolve(open.result);
      open.onerror=()=>reject(open.error);
    });
    try {
      const drafts=await new Promise((resolve,reject)=>{
        const request=db.transaction('drafts').objectStore('drafts').getAll();
        request.onsuccess=()=>resolve(request.result);
        request.onerror=()=>reject(request.error);
      });
      return drafts.some(draft=>draft.path===resource && draft.bytes instanceof Blob && draft.bytes.size>0);
    } finally { db.close(); }
  },timeout,resource);
  const accept=dialog=>{void dialog.accept();};
  page.on('dialog',accept);
  try { await page.reload({waitUntil:'domcontentloaded'}); }
  finally { page.off('dialog',accept); }
  await page.waitForFunction(view=>document.querySelector(view)?.appView?.inspect?.()?.instanceId,timeout,selector(first));
  const recovered=await edit(page,await grant(page,first),'document.inspect');
  assert.deepEqual([recovered.compositionCount,recovered.mediaCount,recovered.dirty],[2,1,true]);
  await labelledButton(page,selector(first),'Close');
  await labelledButton(page,'dialog.webos-effectcraft-session[open]','Discard');
  await page.waitForSelector(selector(first),{hidden:true,...timeout});
  present('Refresh restores the unsaved composition and linked media, and Discard closes the draft');

  const fresh=await login(browser,credentials);
  try {
    await fresh.page.evaluate(()=>{
      window.effectcraftOriginalReads=[];
      addEventListener('message',event=>{
        if (event.origin===location.origin && event.data?.type==='effectcraft:account-original-read') {
          window.effectcraftOriginalReads.push(event.data.digest);
        }
      });
    });
    const id=await files(fresh.page);
    await file(fresh.page,id,'list',{path:'Video'});
    await file(fresh.page,id,'open',{path:resource});
    const reopened=await fresh.page.waitForFunction(resource=>[...document.querySelectorAll('.window[data-window]')].find(node=>
      node.appView?.inspect?.()?.resourceId===resource)?.dataset.window,timeout,resource);
    const openId=await reopened.jsonValue();
    await reopened.dispose();
    const loaded=await edit(fresh.page,await grant(fresh.page,openId),'document.inspect');
    assert.deepEqual([loaded.compositionCount,loaded.mediaCount,loaded.dirty],[1,1,false]);
    assert.deepEqual(await fresh.page.evaluate(()=>window.effectcraftOriginalReads),[digest]);
    present('A fresh browser reopens the native composition from Files and fetches its original digest');
    const native=await fresh.page.$(selector(openId)+' iframe');
    try {
      let colors;
      for (let i=0;i<20;i++) {
        const png=await native.screenshot({encoding:'base64'});
        colors=await fresh.page.evaluate(async png=>{
          const bytes=Uint8Array.from(atob(png),char=>char.charCodeAt(0));
          const image=await createImageBitmap(new Blob([bytes],{type:'image/png'}));
          const canvas=document.createElement('canvas');
          canvas.width=image.width; canvas.height=image.height;
          const ctx=canvas.getContext('2d');
          ctx.drawImage(image,0,0);
          image.close();
          const {data}=ctx.getImageData(Math.floor(canvas.width*.43),Math.floor(canvas.height*.23),
            Math.floor(canvas.width*.14),Math.floor(canvas.height*.25));
          let red=0,yellow=0;
          for (let n=0;n<data.length;n+=4) {
            if (data[n]>180 && data[n+1]<74 && data[n+2]>38 && data[n+2]<96) red++;
            if (data[n]>220 && data[n+1]>185 && data[n+2]<76) yellow++;
          }
          return {red,yellow};
        },png);
        if (colors.red>900 && colors.yellow>150) break;
        await new Promise(resolve=>setTimeout(resolve,300));
      }
      await native.screenshot({path:path.join(output,'effectcraft-fresh-composition.png')});
      assert(colors.red>900 && colors.yellow>150,'The reopened composition should render the original with its expected colors.');
      present('The reopened EffectCraft composition renders the original’s expected pixels');
    } finally { await native.dispose(); }

    const frameWorkers=()=>fresh.page.workers().filter(worker=>new URL(worker.url()).pathname==='/effectcraft/worker.js');
    assert(frameWorkers().length>0,'The native composition should have a frame worker.');
    await labelledButton(fresh.page,selector(openId),'Close');
    await fresh.page.waitForSelector(selector(openId),{hidden:true,...timeout});
    for (let i=0;i<40 && frameWorkers().length;i++) await new Promise(resolve=>setTimeout(resolve,100));
    assert.equal(frameWorkers().length,0,'Closing the window should terminate its frame workers.');
    present('Closing the native editor retires its browser frame workers');
  } finally {
    await fresh.context.close();
  }
}

let browser;
try {
  browser = await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true,args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],
    defaultViewport:{width:1540,height:960}
  });
  if (singleEditor) {
    const {page,context,credentials} = await login(browser);
    try { await singleEditor[1](browser,page,credentials); }
    catch (error) {
      await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});
      await writeFile(path.join(output,'result.json'),JSON.stringify({status:'FAIL',checks,error:error.message},null,2)+'\n',{mode:0o600});
      throw error;
    }
    finally { await context.close(); }
  }
  if (!singleEditor && !disabled && graphicsOnly) {
    for (const app of graphics) {
      const {page,context} = await login(browser);
      try { await graphicsDispatch(page,app); }
      finally { await context.close(); }
    }
  }
  if (!singleEditor && !disabled && !graphicsOnly && photoProfile) {
    const {page,context} = await login(browser);
    try { await photoDispatch(page); }
    finally { await context.close(); }
  }
  const {page,context} = !singleEditor && (disabled || officeProfile && !graphicsOnly) ? await login(browser) : {};
  if (!singleEditor && disabled) {
    assert.equal(await page.evaluate(() => window.desktopLab.agentOperations === undefined), true);
    present('default server profile has no agent bridge');
  } else if (!singleEditor && officeProfile && !graphicsOnly) {
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
  if (!singleEditor && !disabled && !graphicsOnly && officeProfile) await deckDispatch(browser);
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks},null,2)+'\n',{mode:0o600});
} finally {
  await browser?.close();
}
