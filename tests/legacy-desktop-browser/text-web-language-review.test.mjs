import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base = process.env.CODI_TEST_URL || 'http://127.0.0.1:19496/';
if (!['http://127.0.0.1:19496', 'https://ksu.codes'].includes(new URL(base).origin)) throw Error('Unexpected test origin');
const fixtures = {
  '/index.HTML': '<h1>Hello</h1>',
  '/site.css': 'body { color: red; }',
  '/data.json': '{"name": "student", "count": 1}',
  '/query.sql': 'SELECT id FROM students WHERE id = 1;',
  '/notes.md': '# Project notes\n\n**important** work',
  '/code.py': 'def calculate():\n    return 42',
  '/code.js': 'const answer = 42;',
  '/sketch.ino': 'int answer = 42;',
  '/plain.txt': 'SELECT id FROM students WHERE id = 1;',
};
const highlightedTokens = {'/index.HTML': 'h1', '/site.css': 'body', '/data.json': 'student', '/query.sql': 'SELECT', '/notes.md': 'Project notes', '/code.py': 'def', '/code.js': 'const', '/sketch.ino': 'int'};
const user = 'weblang' + Date.now().toString().slice(-8) + process.pid;
const browser = await puppeteer.connect({browserURL: 'http://127.0.0.1:19255', protocolTimeout: 120000});
const ctx = await browser.createBrowserContext(); let fresh;
try {
  if (process.env.CODI_CLEANUP === '1') console.log('TEST_ACCOUNT ' + user);
  const p = await ctx.newPage(), errors = [];
  p.on('pageerror', e => errors.push(e.message));
  async function login(page, register) {
    await page.setViewport(process.env.CODI_PHONE ? {width: 412, height: 915, isMobile: true, hasTouch: true} : {width: 1366, height: 900});
    await page.goto(base); await page.waitForSelector('.login-toggle');
    if (register) await page.click('.login-toggle');
    await page.type('[aria-label=Username]', user); await page.type('[aria-label=Password]', 'test1234');
    if (register) await page.type('[aria-label="Confirm password"]', 'test1234');
    await page.click('.login-form button[type=submit]'); await page.waitForFunction(() => window.desktopLab?.session?.kind === 'registered');
  }
  async function open(page, path, content, highlighted) {
    await page.evaluate(path => openMirrorDocument(surfaces.get('Desktop'), signedInSubject(), path), path);
    await page.waitForFunction(text => document.querySelector('.cm-content')?.innerText.includes(text), {timeout: 30000}, content);
    await page.waitForFunction(want => !!document.querySelector('.cm-content span[class]') === want, {timeout: 30000}, highlighted);
    if (highlightedTokens[path]) await page.waitForFunction(token => [...document.querySelectorAll('.cm-content span[class]')].some(span => span.textContent.includes(token)), {timeout: 30000}, highlightedTokens[path]);
  }
  async function close(page) {
    await page.evaluate(() => document.querySelector('.codi-text-editor').closest('.window').querySelector('[aria-label=Close]').click());
    await page.waitForFunction(() => !document.querySelector('.codi-text-editor'));
  }
  await login(p, true);
  await p.evaluate(async fixtures => {const files = (await mirrorFileContext()).files;for (const [path, text] of Object.entries(fixtures)) await files.write(path, text, null);await files.sync();}, fixtures);
  for (const [path, text] of Object.entries(fixtures)) {
    console.log('CHECK', path);
    await open(p, path, text.split('\n')[0], path !== '/plain.txt');
    if (path === '/query.sql') {
      await p.click('.cm-content'); await p.keyboard.down('Control'); await p.keyboard.press('End'); await p.keyboard.up('Control');
      await p.keyboard.type('\n-- student note');
      await p.evaluate(() => document.querySelector('.ce-toolbar [data-command=save]').click());
      await p.waitForFunction(async () => new TextDecoder().decode((await (await mirrorFileContext()).files.read('/query.sql')).data).includes('student note'));
      await p.evaluate(async () => await (await mirrorFileContext()).files.sync());
    }
    await close(p);
  }
  assert.match(await p.evaluate(async () => new TextDecoder().decode((await (await serverFileContext()).files.read('query.sql')).data)), /student note/);
  fresh = await browser.createBrowserContext(); const q = await fresh.newPage(); await login(q, false);
  await q.evaluate(async () => await (await mirrorFileContext()).files.sync());
  await open(q, '/query.sql', 'student note', true); await close(q); await fresh.close(); fresh = null;
  assert.deepEqual(errors, []);
  if (process.env.CODI_CLEANUP === '1') {
    const subject = await p.evaluate(async paths => {const c = await mirrorFileContext();for (const path of paths) {const f = await c.files.stat(path);await c.files.remove(path, f.version)}await c.files.sync();return c.owner;}, Object.keys(fixtures));
    console.log('CLEANUP_ACCOUNT ' + user + ' ' + subject);
  }
  console.log('PASS web-language highlighting, plain text, SQL edit, account sync, reopen and close');
} finally { await fresh?.close(); await ctx.close(); await browser.disconnect(); }
