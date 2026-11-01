import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base = process.env.CODI_TEST_URL || 'http://127.0.0.1:18312/';
const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19262',
  protocolTimeout: 120000,
});
const username = process.env.CODI_TEST_USER || 'snake' + Date.now().toString().slice(-9);
const contexts = [];
const errors = [];

async function login(page, register, user = username) {
  page.on('pageerror', error => errors.push(error.message));
  page.on('dialog', dialog => dialog.accept());
  await page.evaluateOnNewDocument(() => {
    const original = window.fetch;
    window.fetch = (url, ...args) => String(url).endsWith('assets/terminal/v2/image.json')
      ? Promise.resolve(new Response('', {status: 404}))
      : original(url, ...args);
  });
  await page.goto(base);
  await page.waitForSelector('.login-toggle');
  if (register) await page.click('.login-toggle');
  await page.type('[aria-label=Username]', user);
  await page.type('[aria-label=Password]', 'test1234');
  if (register) await page.type('[aria-label="Confirm password"]', 'test1234');
  await page.click('.login-form button[type=submit]');
  await page.waitForFunction(() => window.desktopLab?.session?.kind === 'registered', {timeout: 30000});
}

async function launch(page) {
  await page.evaluate(() => surfaces.get('Desktop').launch('snake-garden'));
  await page.waitForSelector('.snake-board canvas', {timeout: 30000});
}

const click = (page, label) => page.evaluate(label => {
  const button = [...document.querySelectorAll('.snake-garden button')].find(node => node.textContent === label);
  if (!button) throw Error('Missing button: ' + label);
  button.click();
}, label);

try {
  const first = await browser.createBrowserContext();
  contexts.push(first);
  const page = await first.newPage();
  await page.setViewport({width: 1366, height: 900});
  await login(page, true);
  await launch(page);
  await page.select('[aria-label="Garden"]', '1');
  await page.select('[aria-label="Speed"]', '3');
  await click(page, 'Start game');
  await page.waitForFunction(() => document.querySelector('.snake-summary')?.textContent.includes('Playing'));
  await page.focus('.snake-board');
  await page.keyboard.press('ArrowUp');
  await new Promise(resolve => setTimeout(resolve, 240));
  await page.evaluate(() => {
    document.querySelector('.snake-save').open = true;
    document.querySelector('[aria-label="Snake save path"]').value = '/Snake Garden.game.json';
  });
  await click(page, 'Save');
  await page.waitForFunction(() => document.querySelector('.app-status')?.textContent.includes('Saved to My files'));
  await page.evaluate(async () => (await mirrorFileContext()).files.sync());
  const saved = await page.evaluate(async () => JSON.parse(new TextDecoder().decode(
    (await (await serverFileContext()).files.read('Snake Garden.game.json')).data,
  )));
  assert.equal(saved.appId, 'snake-garden');
  assert.equal(saved.payload.gardenId, 1);
  assert.equal(saved.payload.speed, 3);
  assert.equal(saved.payload.paused, true);
  await page.evaluate(() => document.querySelector('.snake-garden').closest('.window')
    .querySelector('[aria-label=Close]').click());
  await page.waitForFunction(() => !document.querySelector('.snake-garden'));
  await page.evaluate(() => openMirrorDocument(
    surfaces.get('Desktop'), signedInSubject(), '/Snake Garden.game.json'));
  await page.waitForFunction(() => document.querySelector('.app-status')?.textContent.includes('Garden loaded and paused'));
  assert.equal(await page.$eval('[aria-label="Snake save path"]', node => node.value), '/Snake Garden.game.json');
  await page.evaluate(() => document.querySelector('.snake-garden').closest('.window')
    .querySelector('[aria-label=Close]').click());
  await page.waitForFunction(() => !document.querySelector('.snake-garden'));

  const fresh = await browser.createBrowserContext();
  contexts.push(fresh);
  const reloaded = await fresh.newPage();
  await reloaded.setViewport({width: 412, height: 915, isMobile: true, hasTouch: true});
  await login(reloaded, false);
  await reloaded.evaluate(async () => (await mirrorFileContext()).files.sync());
  await launch(reloaded);
  await reloaded.evaluate(() => document.querySelector('.snake-save').open = true);
  await click(reloaded, 'Open');
  await reloaded.waitForSelector('[aria-label="Choose file Snake Garden.game.json"]', {visible: true});
  await reloaded.click('[aria-label="Choose file Snake Garden.game.json"]');
  await reloaded.waitForFunction(() => document.querySelector('.app-status')?.textContent.includes('loaded and paused'));
  assert.equal(await reloaded.$eval('[aria-label="Snake save path"]', node => node.value), '/Snake Garden.game.json');
  assert.match(await reloaded.$eval('.snake-summary', node => node.textContent), /Paused/);

  const isolation = await browser.createBrowserContext();
  contexts.push(isolation);
  const other = await isolation.newPage();
  await other.setViewport({width: 390, height: 844, isMobile: true, hasTouch: true});
  await login(other, true, username + 'b');
  assert.equal(await other.evaluate(async () => {
    try {
      await (await mirrorFileContext()).files.read('/Snake Garden.game.json');
      return true;
    } catch {
      return false;
    }
  }), false);

  await reloaded.evaluate(async () => {
    const context = await mirrorFileContext();
    const file = await context.files.read('/Snake Garden.game.json');
    await context.files.remove('/Snake Garden.game.json', file.version);
    await context.files.sync();
  });
  assert.deepEqual(errors, []);
  console.log('PASS real account save, sync, phone-sized paused reload and account isolation');
} finally {
  for (const context of contexts) await context.close();
  await browser.disconnect();
}
