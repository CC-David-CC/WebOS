/** Actual Save As Browse button, account identity, and all thirteen export writers. */
import assert from 'node:assert/strict';
import {mkdir, writeFile} from 'node:fs/promises';
import {randomBytes, createHash} from 'node:crypto';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const origin = process.env.WEBOS_VIEWER_ORIGIN;
const output = process.env.WEBOS_TEST_OUTPUT;
const engine = process.env.WEBOS_ENGINE_COMMIT;
assert(origin && path.isAbsolute(output) && engine);
await mkdir(output, {mode: 0o700});
const credentials = {username: 'wcbrowse' + randomBytes(6).toString('hex'), password: randomBytes(12).toString('hex')};
await writeFile(path.join(output, 'credentials.json'), JSON.stringify(credentials), {mode: 0o600});
const checks = [], exports = [], errors = [];
let browser, page, frame, id, filesId;
const windowSelector = () => '.window[data-window="' + id + '"]';
async function button(label, parent = '') {
  for (const n of await page.$$(parent + 'button')) {
    if (await n.evaluate((n, label) => (n.querySelector('.row-text') || n).textContent.trim() === label, label)) {
      await n.click(); return;
    }
  }
  throw Error('Missing button: ' + label);
}
async function launch(group, name) {
  await page.click('.app-menu-button'); await button(group, '.menu-pane '); await button(name, '.menu-pane ');
}
async function native(command, params = {}) {
  return frame.evaluate(async (command, params) => {
    const state = await window.wordcraft.uiInspect();
    return window.wordcraft.request('engine.execute', {command, params, doc: state.document});
  }, command, params);
}
async function ui() { return frame.evaluate(() => window.wordcraft.uiInspect()); }
async function state() { return page.evaluate(id => document.querySelector('.window[data-window="' + id + '"]').appView.inspect(), id); }
async function settled() { await frame.waitForFunction(async () => !(await window.wordcraft.uiInspect()).pendingSaves); }
async function editor() { await frame.waitForFunction(async () => !(await window.wordcraft.uiInspect()).ui.backstage); }
async function focus() {
  await page.evaluate(id => {
    for (const desktop of window.desktopLab.surfaces.values()) {
      const w = desktop.windows.find(w => String(w.id) === id);
      if (w) { desktop.activateWindow(w); document.querySelector('.window[data-window="' + id + '"]').appView.focus(); return; }
    }
    throw Error('Missing WordCraft window');
  }, id);
}
async function file(operation, args) {
  return page.evaluate(async ({id, operation, args}) => document.querySelector('.window[data-window="' + id + '"]').appView.execute(operation, args), {id: filesId, operation, args});
}
async function download(name) {
  await file('list', {path: name.includes('/') ? name.slice(0, name.lastIndexOf('/')) : ''});
  const info = await file('snapshot', {path: name});
  const data = await file('download', {path: name, expectedRevision: info.sha256});
  const bytes = Buffer.from(Object.values(data.data));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), info.sha256);
  return {sha256: info.sha256, bytes};
}
async function browse() {
  await focus(); await native('ui.backstage', {value: true, page: 'saveAs'});
  assert.equal((await ui()).ui.backstagePage, 'saveAs');
  await frame.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  // Actual egui button in this pinned English Backstage layout (200pt sidebar,
  // 40pt page padding). Native kittest independently locates it by its label.
  const canvas = await frame.$('#wordcraft_canvas');
  const box = await canvas.boundingBox();
  const size = (await ui()).window;
  await page.mouse.click(box.x + 280 * box.width / size[0], box.y + 100 * box.height / size[1]);
  await page.waitForSelector('.webos-wordcraft-dialog[data-kind="path"] input');
}
async function destination(name) {
  await page.$eval('.webos-wordcraft-dialog[data-kind="path"] input', (input, value) => {input.value = value;}, name);
  await button('Save', '.webos-wordcraft-dialog[data-kind="path"] ');
}
async function binding(name) {
  await page.waitForFunction(async ({id, name}) => {
    const s = await document.querySelector('.window[data-window="' + id + '"]').appView.inspect();
    return s.path === name && s.pendingSaves === 0;
  }, {}, {id, name});
  await settled();
  const s = await ui();
  assert.equal(s.documents.find(d => d.id === s.document).path, name);
  const caption = await page.$eval(windowSelector() + ' .caption-text', n => n.textContent);
  assert(caption.startsWith(name.split('/').at(-1) + ' — WordCraft'));
}
async function check(name, fn) {
  await fn(); checks.push(name); console.log(JSON.stringify({check: name, status: 'PASS'}));
}
try {
  browser = await puppeteer.launch({executablePath: '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true,
    args: ['--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'], userDataDir: path.join(output, 'browser-profile')});
  page = await browser.newPage(); await page.setViewport({width: 1500, height: 1150}); page.setDefaultTimeout(45000);
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(origin, {waitUntil: 'networkidle0'});
  assert.equal(await page.evaluate(async () => (await (await fetch('/viewer-build.json')).json()).engine.sourceCommit), engine);
  await page.waitForSelector('.login-gate'); await page.click('.login-toggle');
  await page.type('[aria-label="Username"]', credentials.username); await page.type('[aria-label="Password"]', credentials.password);
  await page.type('[aria-label="Confirm password"]', credentials.password); await button('Register', '.login-gate ');
  await page.waitForFunction(() => !!window.desktopLab?.session && !document.querySelector('.login-gate'));
  await launch('System Tools', 'Files');
  await page.waitForSelector('.window.focused:has(.webos-files)');
  filesId = await page.$eval('.window.focused:has(.webos-files)', n => n.dataset.window);
  await page.evaluate(id => document.querySelector('.window[data-window="' + id + '"]').appView.ready, filesId);
  await launch('Office', 'WordCraft'); await page.waitForSelector('.webos-wordcraft');
  id = await page.$eval('.window:has(.webos-wordcraft)', n => n.dataset.window);
  await page.waitForFunction(async id => {try { return (await document.querySelector('.window[data-window="' + id + '"]').appView.inspect()).phase === 'ready'; } catch { return false; }}, {timeout: 120000}, id);
  frame = await (await page.$(windowSelector() + ' iframe[title="WordCraft document"]')).contentFrame();
  await native('para.heading1'); await native('text.insert', {text: 'Synthetic export heading'});
  await native('text.newParagraph'); await native('para.normal'); await native('text.insert', {text: 'Synthetic export paragraph.'});
  await native('text.newParagraph'); await native('para.bullets'); await native('text.insert', {text: 'Synthetic list item'});
  await check('Actual Browse opens the account chooser; cancellation leaves an untitled dirty document', async () => {
    await browse(); await page.screenshot({path: path.join(output, 'browse-untitled.png')});
    assert.equal(await page.$eval('.webos-wordcraft-dialog[data-kind="path"] input', n => n.value), 'Documents/Untitled.docx');
    await button('Cancel', '.webos-wordcraft-dialog[data-kind="path"] ');
    assert.equal((await state()).path, null); assert.equal((await ui()).dirty, true); assert.equal((await ui()).ui.backstage, true);
  });
  await check('Accepting the suggested new filename without editing it saves successfully', async () => {
    await browse(); await button('Save', '.webos-wordcraft-dialog[data-kind="path"] ');
    await binding('Documents/Untitled.docx'); await editor(); assert.equal((await ui()).dirty, false);
    assert((await download('Documents/Untitled.docx')).bytes.length > 0);
  });
  await check('Browse accepts a chosen account filename, confirms identity and returns typing focus', async () => {
    await browse(); await destination('Documents/Chosen original.docx'); await binding('Documents/Chosen original.docx'); await editor();
    assert.equal((await ui()).dirty, false);
    await page.keyboard.type(' Keyboard focus works.');
    await frame.waitForFunction(async () => (await window.wordcraft.docInspect({text: true})).blocks.some(b => b.text?.includes('Keyboard focus works.')));
  });
  const original = await download('Documents/Chosen original.docx');
  await check('Browse on an existing document suggests its full path; cancellation does not save', async () => {
    await browse(); assert.equal(await page.$eval('.webos-wordcraft-dialog[data-kind="path"] input', n => n.value), 'Documents/Chosen original.docx');
    await button('Cancel', '.webos-wordcraft-dialog[data-kind="path"] ');
    assert.equal((await state()).path, 'Documents/Chosen original.docx'); assert.equal((await ui()).dirty, true);
    assert.equal((await download('Documents/Chosen original.docx')).sha256, original.sha256);
  });
  await check('Invalid account paths stay in the chooser without changing document identity', async () => {
    await browse(); await destination('../Outside.docx');
    assert(await page.$('.webos-wordcraft-dialog[data-kind="path"]'));
    assert.match(await page.$eval('.webos-wordcraft-dialog [role="alert"]', n => n.textContent), /relative/);
    assert.equal((await state()).path, 'Documents/Chosen original.docx');
    await button('Cancel', '.webos-wordcraft-dialog[data-kind="path"] ');
  });
  await check('Browse can change filename and folder; the original account file stays unchanged', async () => {
    await browse(); await destination('Digital Projects/Renamed copy.docx'); await binding('Digital Projects/Renamed copy.docx'); await editor();
    assert.equal((await ui()).dirty, false); assert.equal((await download('Documents/Chosen original.docx')).sha256, original.sha256);
    assert.notEqual((await download('Digital Projects/Renamed copy.docx')).sha256, original.sha256);
    await page.screenshot({path: path.join(output, 'browse-saved.png')});
  });
  await check('Ordinary Save after Browse writes the chosen file, preserving the original', async () => {
    const before = await download('Digital Projects/Renamed copy.docx');
    await native('text.insert', {text: ' Subsequent ordinary save.'}); await native('file.save'); await settled();
    assert.equal((await ui()).dirty, false); assert.equal((await state()).path, 'Digital Projects/Renamed copy.docx');
    assert.notEqual((await download('Digital Projects/Renamed copy.docx')).sha256, before.sha256);
    assert.equal((await download('Documents/Chosen original.docx')).sha256, original.sha256);
  });
  await check('Keeping the suggested existing path saves that file without requiring a rename', async () => {
    const before = await download('Digital Projects/Renamed copy.docx');
    await native('text.insert', {text: ' Keep the suggested filename.'}); await browse();
    assert.equal(await page.$eval('.webos-wordcraft-dialog[data-kind="path"] input', n => n.value), 'Digital Projects/Renamed copy.docx');
    await button('Save', '.webos-wordcraft-dialog[data-kind="path"] ');
    await binding('Digital Projects/Renamed copy.docx'); await editor(); assert.equal((await ui()).dirty, false);
    assert.notEqual((await download('Digital Projects/Renamed copy.docx')).sha256, before.sha256);
    assert.equal((await download('Documents/Chosen original.docx')).sha256, original.sha256);
  });
  await check('A name collision after Browse keeps the dirty original identity and existing target bytes', async () => {
    await native('text.insert', {text: ' Preserve on collision.'}); await browse(); await destination('Documents/Chosen original.docx'); await settled();
    await page.waitForFunction(() => [...document.querySelectorAll('.webos-wordcraft-status')].some(n => /conflict|exists|precondition/i.test(n.textContent)));
    assert.equal((await state()).path, 'Digital Projects/Renamed copy.docx'); assert.equal((await ui()).dirty, true); assert.equal((await ui()).ui.backstage, true);
    assert.equal((await download('Documents/Chosen original.docx')).sha256, original.sha256);
  });
  // Native kittest clicks every visible export button and reimports ten formats.
  // This browser pass qualifies the same writers through actual WASM/account delivery,
  // records identity effects, and retains every output for independent structure checks.
  const formats = [
    ['PDF', 'pdf', false], ['Word', 'docx', true], ['Word XML', 'xml', true], ['Word 2003 XML', 'xml', true, 'wordml2003'],
    ['OpenDocument', 'odt', true], ['OpenDocument Template', 'ott', true], ['Flat OpenDocument', 'fodt', true],
    ['RTF', 'rtf', true], ['HTML', 'html', false], ['Markdown', 'md', false], ['LaTeX', 'tex', false], ['Text', 'txt', false], ['PNG', 'png', false]
  ];
  for (const [index, [label, ext, rebinds, format]] of formats.entries()) {
    await check(label + ' writer delivers an account file; identity behavior is recorded', async () => {
      const source = 'Documents/Export source ' + index + '.docx', target = 'Documents/Export result ' + index + '.' + ext;
      await native('file.saveAs', {path: source}); await binding(source);
      await native('text.insert', {text: ' Export sentinel ' + index + '.'});
      const before = await download(source);
      await native('ui.backstage', {value: true, page: 'export'});
      await native(ext === 'png' ? 'file.exportPng' : 'file.saveAs', {path: target, ...(format ? {format} : {})});
      await settled(); await editor();
      const result = await download(target); assert(result.bytes.length > 0);
      assert.equal((await download(source)).sha256, before.sha256);
      assert.equal((await state()).path, rebinds ? target : source); assert.equal((await ui()).dirty, !rebinds);
      await writeFile(path.join(output, 'export-' + index + '.' + ext), result.bytes, {mode: 0o600});
      exports.push({label, extension: ext, format: format || null, bytes: result.bytes.length, sha256: result.sha256, rebinds, retainsDirty: !rebinds});
    });
  }
  await native('file.save'); await settled();
  assert.deepEqual(errors, []);
  await writeFile(path.join(output, 'result.json'), JSON.stringify({status: 'PASS', engine, checks, exports, pageErrors: errors}, null, 2) + '\n');
  console.log(JSON.stringify({status: 'PASS', checks: checks.length}));
} catch (error) {
  await writeFile(path.join(output, 'failure.json'), JSON.stringify({error: error.message, checks, exports, pageErrors: errors}, null, 2) + '\n');
  await page?.screenshot({path: path.join(output, 'failure.png')}).catch(() => {}); throw error;
} finally { await browser?.close(); }
