import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19262',
});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [];
const external = [];
const base = process.env.CODI_SNAKE_URL || 'http://127.0.0.1:18337/';
page.on('pageerror', error => errors.push(error.message));
page.on('dialog', dialog => dialog.accept());
page.on('request', request => {
  if (/^https?:/.test(request.url()) && new URL(request.url()).origin !== new URL(base).origin) {
    external.push(request.url());
  }
});

const click = label => page.evaluate(label => {
  const first = document.querySelectorAll('.snake-garden')[0];
  const button = [...first.querySelectorAll('button')].find(node => node.textContent === label);
  if (!button) throw Error('Missing button: ' + label);
  button.click();
}, label);

try {
  await page.setViewport(process.env.CODI_PHONE
    ? {width: 412, height: 915, isMobile: true, hasTouch: true}
    : {width: 1366, height: 900});
  const manifest = JSON.parse(await readFile(
    process.env.CODI_SNAKE_MANIFEST || '.build/snake-garden-test/apps.json',
    'utf8',
  ));
  const entry = '/' + manifest.apps[0].path.replace(/^assets\/desktop\//, '');
  await page.goto(base + '?app=' + encodeURIComponent(entry));
  await page.waitForFunction(() => window.instances?.length === 2);
  await page.waitForFunction(() => document.querySelectorAll('.snake-board canvas').length === 2, {timeout: 30000});
  assert.equal(await page.$$eval('.snake-board canvas', nodes => nodes.length), 2);
  assert.match(await page.$$eval('.snake-rive-pending', nodes => nodes[0].textContent), /Rive artwork pending/);
  assert.match(await page.$$eval('.snake-summary', nodes => nodes[0].textContent), /Paused/);

  await page.select('.snake-garden [aria-label="Game mode"]', 'campaign');
  await page.select('.snake-garden [aria-label="Garden"]', '1');
  await page.select('.snake-garden [aria-label="Speed"]', '3');
  await click('Start game');
  await page.waitForFunction(() => document.querySelector('.snake-summary')?.textContent.includes('Playing'));
  await page.focus('.snake-board');
  await page.keyboard.press('ArrowUp');
  await new Promise(resolve => setTimeout(resolve, 250));
  await click('Pause');
  assert.match(await page.$eval('.snake-summary', node => node.textContent), /Paused/);
  await click('Resume');
  assert.match(await page.$eval('.snake-summary', node => node.textContent), /Playing/);

  await page.click('.snake-settings summary');
  assert.equal(await page.$eval('[aria-label="Sound"]', node => node.checked), false);
  await page.click('[aria-label="Sound"]');
  await page.waitForFunction(() => document.querySelector('[aria-label="Sound"]')?.checked);
  await page.$eval('[aria-label="Volume"]', node => {
    node.value = '60';
    node.dispatchEvent(new Event('input', {bubbles: true}));
  });
  assert.equal(JSON.parse(await page.evaluate(() => localStorage.getItem('snake-garden-settings:test'))).volume, 60);
  if (process.env.CODI_PHONE) {
    const right = await (await page.$('.snake-garden [aria-label="Right ▶"]')).boundingBox();
    await page.touchscreen.tap(right.x + right.width / 2, right.y + right.height / 2);
    await new Promise(resolve => setTimeout(resolve, 180));
  }

  await page.evaluate(() => document.querySelector('.snake-save').open = true);
  await page.$eval('[aria-label="Snake save path"]', node => node.value = '/Snake Garden.game.json');
  await click('Save');
  await page.waitForFunction(() => document.querySelector('.app-status')?.textContent.includes('Saved to My files'));
  const saved = await page.evaluate(() => JSON.parse(
    new TextDecoder().decode(window.fileStore.get('/Snake Garden.game.json').data),
  ));
  assert.equal(saved.appId, 'snake-garden');
  assert.equal(saved.payload.speed, 3);
  assert.ok(Array.isArray(saved.payload.snake));
  if (process.env.CODI_PHONE) assert.equal(saved.payload.direction, 'right', 'phone direction button queues a turn');

  await click('Resume');
  await page.keyboard.press('ArrowRight');
  await new Promise(resolve => setTimeout(resolve, 180));
  await page.evaluate(() => window.targetPath = '/Snake Garden.game.json');
  await click('Open');
  await page.waitForFunction(() => document.querySelector('.app-status')?.textContent.includes('loaded and paused'));
  assert.match(await page.$eval('.snake-summary', node => node.textContent), /Paused/);

  await page.evaluate(() => {
    window.fileStore.set('/Bad.game.json', {
      data: new TextEncoder().encode('{"format":"wrong"}'),
      version: 'bad',
    });
    window.targetPath = '/Bad.game.json';
  });
  const beforeBad = await page.$eval('.snake-summary', node => node.textContent);
  await click('Open');
  await page.waitForFunction(() => document.querySelector('.app-status')?.textContent.includes('Could not open'));
  assert.equal(await page.$eval('.snake-summary', node => node.textContent), beforeBad);

  await page.evaluate(() => {
    const first = window.instances[0];
    first.controller.abort();
    first.app.dispose();
    first.app.dispose();
    first.app.element.remove();
  });
  assert.equal(await page.$$('.snake-board canvas').then(nodes => nodes.length), 1);
  await click('Start game');
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log('PASS two independent Phaser gardens, campaign settings, keyboard play, save/load, invalid recovery and disposal');
} finally {
  await context.close();
  await browser.disconnect();
}
