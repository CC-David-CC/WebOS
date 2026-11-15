import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const ids = [
  'falling-blocks', 'owl-companion', 'physics-playground', 'snake-garden',
  'clockwork-room', 'chess-study', 'solitaire', 'sky-courier', 'marble-works',
  'stack-balance', 'crystal-defense', 'drone-circuit', 'reactive-control-desk',
  'story-cards', 'expression-puppet', 'rhythm-garden', 'lantern-leap',
  'garden-defense', 'pocket-rally', 'sling-targets', 'gravity-pinball',
  'kinetic-relay', 'tabletop-bot-arena', 'pocket-golf', 'target-garden',
  'orbital-courier', 'clockwork-quest', 'memory-garden',
];
const base = process.env.CODI_TEST_URL || 'http://127.0.0.1:18530/';
const target = new URL(base);
if (!['127.0.0.1', 'localhost', '[::1]'].includes(target.hostname)) {
  throw Error('Isolated loopback preview required');
}

const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19528',
  protocolTimeout: 180000,
});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [], external = [];
let current = 'login';
page.on('pageerror', error => errors.push({app: current, error: error.message}));
page.on('request', request => {
  const url = request.url();
  if (/^https?:/.test(url) && new URL(url).origin !== target.origin) {
    external.push({app: current, url});
  }
});

async function waitReady(count) {
  await page.waitForFunction(n => {
    const windows = [...document.querySelectorAll('.window')];
    if (windows.length !== n) return false;
    const text = windows.at(-1)?.innerText || '';
    return text.trim().length > 30 && !/(?:Loading|Starting|Preparing)/i.test(text.slice(0, 220));
  }, {timeout: 45000, polling: 200}, count);
}

try {
  await page.setViewport({width: 1366, height: 900});
  await page.goto(base);
  await page.waitForSelector('.login-toggle');
  await page.click('.login-toggle');
  const username = 'lifecycle' + Date.now().toString().slice(-8);
  await page.type('[aria-label=Username]', username);
  await page.type('[aria-label=Password]', 'test1234');
  await page.type('[aria-label="Confirm password"]', 'test1234');
  await page.click('.login-form button[type=submit]');
  await page.waitForFunction(() => window.desktopLab?.session?.kind === 'registered', {timeout: 30000});

  const results = [];
  for (const id of ids) {
    current = id;
    const started = performance.now();
    await page.evaluate(id => surfaces.get('Desktop').launch(id), id);
    await waitReady(1);
    await page.evaluate(id => surfaces.get('Desktop').launch(id), id);
    await waitReady(2);
    assert.equal(await page.$$eval(`.window`, nodes => nodes.length), 2, `${id}: two independent windows`);

    await page.evaluate(() => document.querySelectorAll('.window')[1].querySelector('[aria-label=Close]').click());
    await page.waitForFunction(() => document.querySelectorAll('.window').length === 1, {timeout: 10000});
    assert.ok(await page.$('.window'), `${id}: closing one window leaves its sibling mounted`);

    await page.evaluate(() => document.querySelector('.window [aria-label=Close]').click());
    await page.waitForFunction(() => document.querySelectorAll('.window').length === 0, {timeout: 10000});
    results.push({id, twoWindowStartupMs: Math.round(performance.now() - started)});
  }

  for (const id of ids) {
    current = id;
    await page.evaluate(id => {
      surfaces.get('Desktop').launch(id);
      document.querySelector('.window [aria-label=Close]')?.click();
    }, id);
    await page.waitForFunction(() => document.querySelectorAll('.window').length === 0, {timeout: 10000});
    await new Promise(resolve => setTimeout(resolve, 250));
    assert.equal(
      await page.$$eval('.window', nodes => nodes.length),
      0,
      `${id}: startup close must not revive the window`,
    );
  }

  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log(JSON.stringify({
    pass: `two-window startup, independent close, startup close and clean teardown for ${ids.length} previews`,
    results,
  }));
} finally {
  await context.close();
  await browser.disconnect();
}
