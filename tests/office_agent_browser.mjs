import assert from 'node:assert/strict';
import {randomBytes} from 'node:crypto';
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
await mkdir(output, {mode:0o700});
const checks = [];
const agent = await makeKey();
const otherAgent = await makeKey();
const present = (name) => { checks.push(name); console.log('PASS '+name); };
const timeout = {timeout:120_000};
const modal = 'dialog[open]';
const selector = windowId => '.window[data-window="'+windowId+'"]';

async function login(browser) {
  const context = await browser.createBrowserContext();
  const page = await context.newPage();
  const marker = randomBytes(6).toString('hex');
  await page.goto(origin, {waitUntil:'networkidle0'});
  await page.click('.login-toggle');
  await page.type('[aria-label="Username"]', 'office'+marker);
  await page.type('[aria-label="Password"]', marker+marker);
  await page.type('[aria-label="Confirm password"]', marker+marker);
  await page.click('.login-gate button[type="submit"]');
  const status = await page.waitForFunction(() => window.desktopLab.session && !document.querySelector('.login-gate')
    ? 'signed in' : document.querySelector('.login-error')?.textContent || false, timeout);
  assert.equal(await status.jsonValue(), 'signed in');
  return {page, context};
}

async function editor(page, app) {
  const id = await page.evaluate(app => window.desktopLab.surfaces.get('Desktop').launch(app).id, app);
  const status = await page.waitForFunction(async id => {
    const model = await document.querySelector('.window[data-window="'+id+'"]')?.appView?.inspect();
    return model && ['ready','failed','unavailable'].includes(model.phase) ? model.phase : false;
  }, timeout, id);
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

let browser;
try {
  browser = await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true,args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader'],
    defaultViewport:{width:1540,height:960}
  });
  const {page,context} = await login(browser);
  if (process.env.WEBOS_AGENT_DISABLED_TEST === '1') {
    assert.equal(await page.evaluate(() => window.desktopLab.agentOperations === undefined), true);
    present('default server profile has no agent bridge');
  } else {
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
  await context.close();
  if (process.env.WEBOS_AGENT_DISABLED_TEST !== '1') await deckDispatch(browser);
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks},null,2)+'\n',{mode:0o600});
} finally {
  await browser?.close();
}
