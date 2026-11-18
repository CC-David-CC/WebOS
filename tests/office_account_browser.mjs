/** Native GridCraft/DeckCraft in the classic viewer, against a disposable account server. */
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { randomBytes } from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const origin = process.env.WEBOS_VIEWER_ORIGIN;
const output = process.env.WEBOS_TEST_OUTPUT;
assert(origin && output && path.isAbsolute(output));
const endpoint = new URL(origin);
assert.equal(endpoint.hostname, '127.0.0.1', 'This suite creates accounts and files on an isolated loopback server.');
assert.equal(endpoint.origin, origin);
await mkdir(output, {mode: 0o700});
const credentials = {
  username: 'office' + randomBytes(6).toString('hex'),
  password: randomBytes(12).toString('hex'),
};
const checks = [];
const faults = [];
const options = {timeout: 30_000};
const windowSelector = id => '.window[data-window="' + id + '"]';
const applications = [['gridcraft', 'GridCraft', 'xlsx'], ['deckcraft', 'DeckCraft', 'pptx']];
const only = process.env.WEBOS_TEST_OFFICE_APP;
assert(!only || applications.some(([id]) => id === only), 'Unknown Office app fixture.');

async function button(page, label, scope = '') {
  const handle = await page.waitForFunction((selector, wanted) =>
    [...document.querySelectorAll(selector)].find(node =>
      !node.disabled && (node.querySelector('.row-text') || node).textContent.trim() === wanted),
  options, scope + 'button', label);
  const element = handle.asElement();
  assert(element, label);
  await element.click();
  await handle.dispose();
}

async function login(page, register, identity = credentials) {
  await page.goto(origin, {waitUntil: 'networkidle0'});
  await page.waitForSelector('.login-gate');
  if (register) await page.click('.login-toggle');
  await page.type('[aria-label="Username"]', identity.username);
  await page.type('[aria-label="Password"]', identity.password);
  if (register) await page.type('[aria-label="Confirm password"]', identity.password);
  await button(page, register ? 'Register' : 'Sign in', '.login-gate ');
  await page.waitForFunction(() => !!window.desktopLab?.session && !document.querySelector('.login-gate'), options);
}

async function launch(page, group, name) {
  await page.bringToFront();
  await page.click('.app-menu-button');
  await button(page, group, '.menu-pane ');
  await button(page, name, '.menu-pane ');
}

async function windows(page, app) {
  return page.$$eval('.window:has(.webos-' + app + ')', nodes => nodes.map(node => node.dataset.window));
}

async function ready(page, app) {
  const selector = '.window.focused:has(.webos-' + app + ')';
  await page.waitForSelector(selector, options);
  const id = await page.$eval(selector, node => node.dataset.window);
  await page.waitForFunction(async id => {
    const view = document.querySelector('.window[data-window="' + id + '"]')?.appView;
    return (await view?.inspect())?.phase === 'ready';
  }, {...options, timeout: 120_000}, id);
  return id;
}

async function state(page, id) {
  return page.$eval(windowSelector(id), node => node.appView.inspect());
}

async function documentFrame(page, id) {
  const frameElement = await page.$(windowSelector(id) + ' iframe');
  assert(frameElement);
  const frame = await frameElement.contentFrame();
  await frameElement.dispose();
  assert(frame);
  return frame;
}

async function native(page, id, app, command, args = {}) {
  const frame = await documentFrame(page, id);
  return frame.evaluate(async ({app, command, args}) => {
    const api = window[app];
    if (app === 'gridcraft') {
      const model = await api.request('ui.state', {});
      return api.request('ui.documentHost', {command, params: args, doc: Number(model.hostDocumentState.active)});
    }
    const model = await api.request('ui.inspect', {});
    return api.request('engine.execute', {command, params: args, documentId: model.documentId});
  }, {app, command, args});
}

async function files(page) {
  await launch(page, 'System Tools', 'Files');
  const selector = '.window.focused:has(.webos-files)';
  await page.waitForSelector(selector, options);
  await page.$eval(selector, node => node.appView.ready);
  return page.$eval(selector, node => node.dataset.window);
}

async function file(page, id, operation, args) {
  return page.$eval(windowSelector(id), (node, request) =>
    node.appView.execute(request.operation, request.args), {operation, args});
}

async function openFile(page, filesId, resource) {
  await file(page, filesId, 'list', {path: 'Documents'});
  return file(page, filesId, 'open', {path: resource});
}

async function saveAs(page, id, app, resource) {
  const dialog = '.webos-' + app + '-dialog[data-kind="path"]';
  if (app === 'gridcraft') await native(page, id, app, 'file.saveAs');
  else await native(page, id, app, 'app.saveAsDialog', {format: 'pptx'});
  await page.waitForSelector(dialog + ' input', options);
  await page.$eval(dialog + ' input', (input, value) => { input.value = value; }, resource);
  await button(page, 'Save', dialog + ' ');
  await page.waitForFunction(async ({id, resource}) => {
    const view = document.querySelector('.window[data-window="' + id + '"]')?.appView;
    const model = await view?.inspect();
    return model?.path === resource && /^[a-f0-9]{64}$/.test(model.revision) && !model.dirty;
  }, options, {id, resource});
  return (await state(page, id)).revision;
}

async function waitForSave(page, id, previous, timeout = 30_000) {
  await page.waitForFunction(async ({id, previous}) => {
    const view = document.querySelector('.window[data-window="' + id + '"]')?.appView;
    const model = await view?.inspect();
    return model?.revision && model.revision !== previous && !model.dirty;
  }, {timeout, polling: 100}, {id, previous});
  return (await state(page, id)).revision;
}

async function changeMarker(page, id, app, value) {
  if (app === 'gridcraft') {
    await native(page, id, app, 'cell.set', {sheet: 'Totals', cell: 'C3', input: value});
  } else {
    await native(page, id, app, 'slide.notes', {index: 1, text: value});
  }
}

async function marker(page, id, app) {
  if (app === 'gridcraft') {
    return (await native(page, id, app, 'cell.get', {sheet: 'Totals', cell: 'C3'})).value;
  }
  return (await native(page, id, app, 'slide.inspect', {index: 1})).notes;
}

async function author(page, id, app) {
  const run = (command, args) => native(page, id, app, command, args);
  if (app === 'gridcraft') {
    await run('sheet.rename', {name: 'Inputs'});
    await run('cell.set', {cell: 'A1', input: '7'});
    await run('home.bold', {range: 'A1', on: true});
    await run('home.insertSheet', {name: 'Totals'});
    await run('cell.set', {cell: 'B2', input: '=Inputs!A1*3'});
    return;
  }
  await run('design.theme', {name: 'Ember'});
  await run('shape.insert', {preset: 'rect', rect: [60, 60, 600, 100], text: 'First slide sentinel'});
  await run('slide.notes', {text: 'A persisted speaker note', index: 0});
  await run('slide.new', {layout: 'blank'});
  await run('shape.insert', {preset: 'rect', rect: [60, 60, 600, 100], text: 'Second slide sentinel'});
  const data = await page.evaluate(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 24;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#176e9d';
    ctx.fillRect(0, 0, 32, 24);
    ctx.fillStyle = '#f6aa32';
    ctx.fillRect(8, 6, 16, 12);
    return canvas.toDataURL('image/png').split(',')[1];
  });
  await run('insert.picture', {data, name: 'Native-media-fixture.png', rect: [80, 180, 320, 240]});
}

async function verifyContent(page, id, app) {
  const run = (command, args) => native(page, id, app, command, args);
  if (app === 'gridcraft') {
    const formula = await run('cell.get', {sheet: 'Totals', cell: 'B2'});
    assert.equal(formula.formula, '=Inputs!A1*3');
    assert.equal(formula.value, 21);
    const styled = await run('cell.get', {sheet: 'Inputs', cell: 'A1'});
    assert.equal(styled.style.font.bold, true);
    return;
  }
  const first = await run('slide.inspect', {index: 0});
  const second = await run('slide.inspect', {index: 1});
  assert(first.shapes.some(shape => shape.text === 'First slide sentinel'));
  assert(second.shapes.some(shape => shape.text === 'Second slide sentinel'));
  assert.equal(first.notes, 'A persisted speaker note');
  assert(second.shapes.some(shape => shape.kind === 'picture'));
  const presentation = await run('document.inspect');
  assert.equal(presentation.theme, 'Ember');
  assert(presentation.media.some(asset => asset.type === 'image/png' && asset.bytes > 0));
}

async function waitForConflict(page, id) {
  await page.waitForFunction(async selector => {
    const model = await document.querySelector(selector)?.appView?.inspect();
    return model?.autosave?.state === 'paused' && model.dirty;
  }, options, windowSelector(id));
}

async function verifyPresenter(page, id) {
  const frame = await documentFrame(page, id);
  const popupTarget = page.browser().waitForTarget(target => {
    const url = new URL(target.url() || 'about:blank');
    return url.origin === origin && url.hash.startsWith('#deckcraft-presenter=');
  }, options);
  await frame.evaluate(() => window.deckcraft.request('show.start', {from: 0}));
  const popup = await (await popupTarget).page();
  assert(popup);
  try {
    await popup.waitForSelector('canvas', options);
    assert.equal(await popup.evaluate(() => !!window.opener), true);
    await frame.waitForFunction(async () => !!(await window.deckcraft.request('ui.inspect', {})).showing, options);
    await popup.screenshot({path: path.join(output, 'deckcraft-presenter.png')});
    await frame.evaluate(() => window.deckcraft.request('show.end', {}));
    await frame.waitForFunction(async () => !(await window.deckcraft.request('ui.inspect', {})).showing, options);
    await page.waitForFunction(() => !document.fullscreenElement, options);
    assert.equal(popup.isClosed(), true);
  } finally {
    if (!popup.isClosed()) await popup.close();
  }
}

async function recoverBlankDraft(page, filesId, app, name, ext) {
  const original = await windows(page, app);
  await launch(page, 'Office', name);
  const id = await ready(page, app);
  assert(!original.includes(id));
  const label = 'Private unfinished draft';
  if (app === 'gridcraft') await native(page, id, app, 'cell.set', {cell: 'A1', input: label});
  else await native(page, id, app, 'slide.notes', {index: 0, text: label});
  await page.waitForFunction(async ({id, app}) => {
    const model = await document.querySelector('.window[data-window="' + id + '"]')?.appView?.inspect();
    return model?.dirty && model.path === null && model.recovery === (app === 'gridcraft' ? 'stored' : 'saved');
  }, options, {id, app});
  await file(page, filesId, 'list', {path: 'Documents'});
  const before = (await state(page, filesId)).entries.map(item => item.path);
  assert(!before.includes('Documents/Untitled.' + ext));
  const navigationDialogs = [];
  const accept = async dialog => {
    navigationDialogs.push(dialog.type());
    await dialog.accept();
  };
  page.on('dialog', accept);
  try {
    await page.reload({waitUntil: 'networkidle0'});
    await page.waitForFunction(() => !!window.desktopLab?.session, options);
    await button(page, 'Recover draft', '.webos-' + app + '-dialog[data-kind="recovery"] ');
    const reopened = await ready(page, app);
    assert.equal(reopened, id);
    const model = await state(page, id);
    assert(model.dirty);
    assert.equal(model.path, null);
    const actual = app === 'gridcraft'
      ? (await native(page, id, app, 'cell.get', {cell: 'A1'})).value
      : (await native(page, id, app, 'slide.inspect', {index: 0})).notes;
    assert.equal(actual, label);
    assert.deepEqual(navigationDialogs, ['beforeunload']);
    const close = windowSelector(id) + ' [aria-label="Close"]';
    await page.click(close);
    const choice = '.webos-' + app + '-dialog[data-kind="close"] ';
    await button(page, 'Cancel', choice);
    assert((await state(page, id)).dirty);
    await page.click(close);
    await button(page, 'Discard changes', choice);
    await page.waitForSelector(windowSelector(id), {hidden: true});
    assert.deepEqual(await windows(page, app), original);
    await file(page, filesId, 'list', {path: 'Documents'});
    assert.deepEqual((await state(page, filesId)).entries.map(item => item.path), before);
  } finally {
    page.off('dialog', accept);
  }
}

async function loseSaveConfirmation(page, filesId, id, app, resource) {
  const initial = await state(page, id);
  await changeMarker(page, id, app, 'Confirmed by server only');
  const session = await page.createCDPSession();
  let complete, fail, timer, responses = 0;
  const lost = new Promise((resolve, reject) => { complete = resolve; fail = reject; });
  session.on('Fetch.requestPaused', event => {
    if (event.request.method === 'POST' && event.responseStatusCode >= 200 && event.responseStatusCode < 300) {
      responses++;
      void session.send('Fetch.failRequest', {requestId: event.requestId, errorReason: 'Failed'}).then(complete, fail);
    } else {
      void session.send('Fetch.continueResponse', {requestId: event.requestId}).catch(fail);
    }
  });
  try {
    await session.send('Fetch.enable', {patterns: [{urlPattern: origin + '/gateway/upload', requestStage: 'Response'}]});
    await native(page, id, app, 'file.save');
    await Promise.race([lost, new Promise((_, reject) => {
      timer = setTimeout(() => reject(Error('No committed save response was intercepted.')), 30_000);
    })]);
    await waitForConflict(page, id);
    assert.equal(responses, 1);
    const uncertain = await state(page, id);
    assert.equal(uncertain.path, resource);
    assert.equal(uncertain.revision, initial.revision);
    assert.equal(uncertain.dirty, true);
    assert.match(uncertain.autosave.reason, /unknown|uncertain/i);
    if (app === 'gridcraft') assert(uncertain.documents[0].pendingSaves > 0);
    else assert(uncertain.accountFiles.pending.some(save => save.state === 'unknown'));
  } finally {
    clearTimeout(timer);
    await session.send('Fetch.disable');
    await session.detach();
  }
  const stored = await file(page, filesId, 'snapshot', {path: resource});
  assert.notEqual(stored.sha256, initial.revision);
}

let browser, page, status = 'FAIL';
try {
  browser = await puppeteer.launch({
    executablePath: process.env.WEBOS_TEST_CHROMIUM || '/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless: true,
    args: ['--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'],
    userDataDir: path.join(output, 'browser-profile'),
  });
  const observe = page => {
    page.on('pageerror', error => faults.push(error.message));
    page.on('request', request => {
      const target = new URL(request.url());
      if (['http:', 'https:'].includes(target.protocol) && target.origin !== origin) {
        faults.push('Unexpected external request to ' + target.origin);
      }
    });
    return page.setViewport({width: 1600, height: 1050});
  };
  page = await browser.newPage();
  await observe(page);
  await login(page, true);
  const filesId = await files(page);

  for (const [app, name, ext] of applications.filter(([id]) => !only || only === id)) {
    const resource = 'Documents/Office-browser-roundtrip.' + ext;
    await launch(page, 'Office', name);
    const id = await ready(page, app);
    assert.equal((await state(page, id)).dirty, false);
    await author(page, id, app);
    assert.equal((await state(page, id)).dirty, true);
    let revision = await saveAs(page, id, app, resource);
    await file(page, filesId, 'list', {path: 'Documents'});
    const snapshot = await file(page, filesId, 'snapshot', {path: resource});
    assert.equal(snapshot.sha256, revision);
    checks.push(app + ' native authoring and Save As confirmed by Storage');

    const opened = await openFile(page, filesId, resource);
    assert.equal(opened.status, 'activated');
    assert.deepEqual(await windows(page, app), [id]);
    assert.equal(await ready(page, app), id);
    await verifyContent(page, id, app);
    checks.push(app + ' Files Open activates the existing native editor');
    if (app === 'deckcraft') {
      await verifyPresenter(page, id);
      checks.push(app + ' presenter popup and audience show enter and close together');
    }

    await native(page, id, app, 'file.open');
    const picker = '.webos-' + app + '-dialog[data-kind="open"]';
    await page.waitForSelector(picker + ' button[data-path="' + resource + '"]', options);
    await page.click(picker + ' button[data-path="' + resource + '"]');
    await page.waitForSelector(picker, {hidden: true});
    assert.deepEqual(await windows(page, app), [id]);
    assert.equal(await ready(page, app), id);
    checks.push(app + ' native Open reuses the existing account editor');

    await changeMarker(page, id, app, 'Manual save sentinel');
    assert.equal((await state(page, id)).dirty, true);
    const started = Date.now();
    await native(page, id, app, 'file.save');
    revision = await waitForSave(page, id, revision);
    const manualConfirmed = Date.now();
    assert(manualConfirmed - started < 30_000, 'Manual Save bypassed the automatic cooldown.');
    assert.equal((await file(page, filesId, 'snapshot', {path: resource})).sha256, revision);
    checks.push(app + ' immediate manual Save updates the bound resource');

    await changeMarker(page, id, app, 'AutoSave sentinel');
    assert.equal((await state(page, id)).dirty, true);
    assert.equal((await file(page, filesId, 'snapshot', {path: resource})).sha256, revision);
    revision = await waitForSave(page, id, revision, 95_000);
    assert(Date.now() - manualConfirmed >= 58_000, 'Automatic Save respected the confirmed write interval.');
    assert.equal((await file(page, filesId, 'snapshot', {path: resource})).sha256, revision);
    checks.push(app + ' AutoSave debounces, observes the write interval and adopts the server revision');

    const fresh = await browser.createBrowserContext();
    try {
      const second = await fresh.newPage();
      await observe(second);
      await login(second, false);
      const secondFiles = await files(second);
      await openFile(second, secondFiles, resource);
      const secondId = await ready(second, app);
      assert.equal((await state(second, secondId)).revision, revision);
      await verifyContent(second, secondId, app);
      assert.equal(await marker(second, secondId, app), 'AutoSave sentinel');
      await second.screenshot({path: path.join(output, app + '-reopened.png')});
      checks.push(app + ' native parse preserves the saved content in a fresh browser context');

      await changeMarker(second, secondId, app, 'Other browser save');
      await native(second, secondId, app, 'file.save');
      const winner = await waitForSave(second, secondId, revision);
      await page.bringToFront();
      await changeMarker(page, id, app, 'Conflicting edit retained locally');
      await native(page, id, app, 'file.save');
      await waitForConflict(page, id);
      assert.equal((await state(page, id)).revision, revision);
      assert.equal((await file(page, filesId, 'snapshot', {path: resource})).sha256, winner);
      assert.equal(await marker(page, id, app), 'Conflicting edit retained locally');
      const rescue = 'Documents/Conflict-rescue.' + ext;
      const rescued = await saveAs(page, id, app, rescue);
      await file(page, filesId, 'list', {path: 'Documents'});
      assert.equal((await file(page, filesId, 'snapshot', {path: rescue})).sha256, rescued);
      assert.equal((await file(page, filesId, 'snapshot', {path: resource})).sha256, winner);
      checks.push(app + ' conditional Save refuses a stale write and Save As rescues later edits');
    } finally {
      await fresh.close();
    }

    const other = await browser.createBrowserContext();
    try {
      const separate = await other.newPage();
      await observe(separate);
      await login(separate, true, {
        username: 'officeother' + randomBytes(6).toString('hex'),
        password: randomBytes(12).toString('hex'),
      });
      const separateFiles = await files(separate);
      await file(separate, separateFiles, 'list', {path: 'Documents'});
      const listing = await state(separate, separateFiles);
      assert.equal(listing.entries.some(item => item.name === resource.split('/').at(-1)), false);
      await launch(separate, 'Office', name);
      const separateId = await ready(separate, app);
      assert.equal((await state(separate, separateId)).dirty, false);
      assert.equal((await state(separate, separateId)).path, null);
      await saveAs(separate, separateId, app, resource);
      assert.notEqual((await file(page, filesId, 'snapshot', {path: resource})).sha256,
        (await state(separate, separateId)).revision);
      checks.push(app + ' concurrent accounts can independently save the same relative path');
    } finally {
      await other.close();
    }
    await recoverBlankDraft(page, filesId, app, name, ext);
    checks.push(app + ' refresh recovers an untitled draft and close Cancel/Discard preserves server contents');
    const rescuedPath = 'Documents/Conflict-rescue.' + ext;
    await openFile(page, filesId, rescuedPath);
    const resumed = await ready(page, app);
    await loseSaveConfirmation(page, filesId, resumed, app, rescuedPath);
    checks.push(app + ' a lost save response retains local edits and pauses automatic writes');
  }
  assert.deepEqual(faults, []);
  status = 'PASS';
  console.log(JSON.stringify({status: 'PASS', checks}));
} catch (error) {
  await page?.screenshot({path: path.join(output, 'failure.png')}).catch(() => {});
  console.error(JSON.stringify({status: 'FAIL', error: error.message, checks, faults}));
  throw error;
} finally {
  await browser?.close();
  await writeFile(path.join(output, 'result.json'), JSON.stringify({status, checks, faults}, null, 2));
}
