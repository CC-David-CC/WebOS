import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19262',
  protocolTimeout: 120000,
});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
page.on('dialog', dialog => dialog.accept());

const click = label => page.evaluate(label => {
  const root = document.querySelector('.crystal-view');
  const button = [...root.querySelectorAll('button')].find(node =>
    node.textContent === label || node.getAttribute('aria-label') === label);
  if (!button) throw new Error('Missing button: ' + label);
  button.click();
}, label);

try {
  await page.setViewport({width: 1366, height: 900});
  const manifest = JSON.parse(await readFile(
    process.env.CODI_CRYSTAL_MANIFEST || '.build/crystal-defense/apps.json',
    'utf8',
  ));
  const entry = '/' + manifest.apps[0].path.replace(/^assets\/desktop\//, '');
  await page.goto((process.env.CODI_CRYSTAL_URL || 'http://127.0.0.1:18348/') + '?app=' + encodeURIComponent(entry));
  await page.waitForFunction(() => window.instances?.length === 2);
  await page.waitForFunction(() => document.querySelectorAll('.crystal-stage canvas').length === 2, {timeout: 60000});

  await click('Socket 3');
  await click('Build Spark');
  await click('Resume');
  await page.waitForFunction(() => document.querySelector('.crystal-status')?.textContent.includes('Wave 1 started'));

  await page.evaluate(() => window.instances[0].windowElement.classList.remove('focused'));
  await page.waitForFunction(() => document.querySelector('.crystal-view button[aria-label="Resume"]'));
  assert.match(await page.$eval('.crystal-status', node => node.textContent), /lost attention/);
  await page.evaluate(() => window.instances[0].windowElement.classList.add('focused'));

  await page.evaluate(() => {
    document.querySelector('.crystal-save').open = true;
    document.querySelector('[aria-label="Crystal Defense save path"]').value = '/Safety.game.json';
    const files = window.crystalFiles;
    const write = files.write.bind(files);
    files.write = async (...args) => {
      window.writeStarted = true;
      await new Promise(resolve => { window.releaseWrite = resolve; });
      files.write = write;
      return write(...args);
    };
  });
  await click('Save to My files');
  await page.waitForFunction(() => window.writeStarted);
  assert.equal(await page.evaluate(() => window.instances[0].w.crystalDefense.dirty), true, 'pending save keeps close protection active');
  await page.evaluate(() => window.releaseWrite());
  await page.waitForFunction(() => document.querySelector('.crystal-status')?.textContent.includes('syncing with the server'));
  assert.equal(await page.evaluate(() => window.instances[0].w.crystalDefense.dirty), false);

  await page.evaluate(() => {
    window.fileStore.set('/Bad.game.json', {data: new TextEncoder().encode('{bad'), version: 'bad', status: 'synced'});
    window.targetPath = '/Bad.game.json';
  });
  await click('Open from My files');
  await page.waitForFunction(() => document.querySelector('.crystal-status')?.textContent.includes('Could not open defense'));
  assert.match(await page.$eval('.crystal-note', node => node.textContent), /Wave 1\/8/);

  await page.evaluate(() => {
    const first = window.instances[0];
    first.controller.abort();
    first.app.dispose();
    first.app.dispose();
    first.windowElement.remove();
  });
  assert.equal(await page.$$eval('.crystal-view', nodes => nodes.length), 1);
  assert.deepEqual(errors, []);
  console.log('PASS window-focus pause, pending-save close protection, invalid-file preservation and idempotent disposal');
} finally {
  await context.close();
  await browser.disconnect();
}
