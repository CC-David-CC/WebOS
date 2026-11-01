import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base = process.env.CODI_TEST_URL || 'http://127.0.0.1:18336/';
const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19262',
  protocolTimeout: 120000,
});
const username = process.env.CODI_TEST_USER || 'owl' + Date.now().toString().slice(-9);
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
  if (register) console.log('Test account', user, await page.evaluate(() => signedInSubject()));
}

async function launch(page) {
  await page.evaluate(() => surfaces.get('Desktop').launch('owl-companion'));
  await page.waitForSelector('.owl-character', {timeout: 30000});
}

const click = (page, label) => page.evaluate(label => {
  const button = [...document.querySelectorAll('.owl-companion button')].find(node => node.textContent === label);
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
  await page.select('[aria-label="Activity"]', 'blink');
  await click(page, 'Start activity');
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Blink sequence'));
  const sequence = await page.$eval('.owl-prompt', node => node.textContent
    .split('Blink sequence: ')[1].split(' · ')[0].split(' → '));
  for (const eye of sequence) await click(page, eye);
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Round complete'));
  await page.evaluate(() => {
    document.querySelector('.owl-save').open = true;
    document.querySelector('[aria-label="Owl save path"]').value = '/Owl Companion.game.json';
  });
  await click(page, 'Save');
  await page.waitForFunction(() => document.querySelector('.owl-status')?.textContent.includes('Saved to My files'));
  await page.evaluate(async () => (await mirrorFileContext()).files.sync());
  const saved = await page.evaluate(async () => JSON.parse(new TextDecoder().decode(
    (await (await serverFileContext()).files.read('Owl Companion.game.json')).data,
  )));
  assert.equal(saved.appId, 'owl-companion');
  assert.ok(saved.payload.totalScore > 0);
  await page.evaluate(() => document.querySelector('.owl-companion').closest('.window')
    .querySelector('[aria-label=Close]').click());
  await page.waitForFunction(() => !document.querySelector('.owl-companion'));
  await page.evaluate(() => openMirrorDocument(
    surfaces.get('Desktop'), signedInSubject(), '/Owl Companion.game.json'));
  await page.waitForFunction(() => document.querySelector('.owl-status')?.textContent.includes('loaded and paused'));
  assert.equal(await page.$eval('[aria-label="Owl save path"]', node => node.value), '/Owl Companion.game.json');
  await page.evaluate(() => document.querySelector('.owl-companion').closest('.window')
    .querySelector('[aria-label=Close]').click());
  await page.waitForFunction(() => !document.querySelector('.owl-companion'));

  const fresh = await browser.createBrowserContext();
  contexts.push(fresh);
  const reloaded = await fresh.newPage();
  await reloaded.setViewport({width: 412, height: 915, isMobile: true, hasTouch: true});
  await login(reloaded, false);
  await reloaded.evaluate(async () => {
    await (await mirrorFileContext()).files.sync();
  });
  await launch(reloaded);
  await reloaded.evaluate(() => document.querySelector('.owl-save').open = true);
  await click(reloaded, 'Open');
  await reloaded.waitForSelector('[aria-label="Choose file Owl Companion.game.json"]', {visible: true});
  await reloaded.click('[aria-label="Choose file Owl Companion.game.json"]');
  await reloaded.waitForFunction(() => document.querySelector('.owl-status')?.textContent.includes('loaded and paused'));
  assert.equal(await reloaded.$eval('[aria-label="Owl save path"]', node => node.value), '/Owl Companion.game.json');
  assert.match(await reloaded.$eval('.owl-prompt', node => node.textContent), /Round complete/);

  const isolation = await browser.createBrowserContext();
  contexts.push(isolation);
  const other = await isolation.newPage();
  await other.setViewport({width: 390, height: 844, isMobile: true, hasTouch: true});
  await login(other, true, username + 'b');
  assert.equal(await other.evaluate(async () => {
    try {
      await (await mirrorFileContext()).files.read('/Owl Companion.game.json');
      return true;
    } catch {
      return false;
    }
  }), false);

  await reloaded.evaluate(async () => {
    const context = await mirrorFileContext();
    const file = await context.files.read('/Owl Companion.game.json');
    await context.files.remove('/Owl Companion.game.json', file.version);
    await context.files.sync();
  });
  assert.deepEqual(errors, []);
  console.log('PASS real account save, sync, phone-sized reload, paused restore and account isolation');
} finally {
  for (const context of contexts) await context.close();
  await browser.disconnect();
}
