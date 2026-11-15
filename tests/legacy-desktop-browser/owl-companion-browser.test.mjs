import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19255',
});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [];
let dismiss = false;
page.on('pageerror', error => errors.push(error.message));
page.on('dialog', dialog => (dismiss ? dialog.dismiss() : dialog.accept()));

const click = label => page.evaluate(label => {
  const button = [...document.querySelectorAll('.owl-companion button')].find(node => node.textContent === label);
  if (!button) throw Error('Missing button: ' + label);
  button.click();
}, label);

try {
  await page.setViewport(process.env.CODI_PHONE
    ? {width: 412, height: 915, isMobile: true, hasTouch: true}
    : {width: 1366, height: 900});
  const manifest = JSON.parse(await readFile(process.env.CODI_OWL_MANIFEST || '.build/owl-app/apps.json', 'utf8'));
  const entry = '/' + manifest.apps[0].path.replace(/^assets\/desktop\//, '');
  await page.goto((process.env.CODI_OWL_URL || 'http://127.0.0.1:18335/') + '?app=' + encodeURIComponent(entry));
  await page.waitForFunction(() => window.instances?.length === 2);
  await page.waitForSelector('.owl-character', {timeout: 30000});
  assert.equal(await page.$$eval('.owl-character', nodes => nodes.length), 2);
  assert.match(await page.$$eval('.owl-fallback-label', nodes => nodes[0].textContent), /Rive artwork pending/);

  await page.select('[aria-label="Activity"]', 'blink');
  await page.select('[aria-label="Difficulty"]', '1');
  await click('Start activity');
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Blink sequence'));
  const sequence = await page.$eval('.owl-prompt', node => {
    const text = node.textContent.split('Blink sequence: ')[1].split(' · ')[0];
    return text.split(' → ');
  });
  for (const eye of sequence) {
    await click(eye);
  }
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Round complete'));
  assert.match(await page.$eval('.owl-prompt', node => node.textContent), /Score: \d+/);

  await click('Next round');
  await click('Pause');
  assert.equal(await page.$eval('[aria-label="Resume"]', node => node.textContent), 'Resume');
  await click('Resume');
  await page.evaluate(() => window.dispatchEvent(new Event('blur')));
  await page.waitForFunction(() => document.querySelector('.owl-companion [aria-label="Resume"]'));
  await click('Resume');

  await page.select('[aria-label="Activity"]', 'firefly');
  await click('Start activity');
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Catch firefly'));
  await click('Catch current firefly');
  assert.match(await page.$eval('.owl-status', node => node.textContent), /firefly/i);

  await page.select('[aria-label="Activity"]', 'match');
  await click('Start activity');
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Choose the'));
  const expression = await page.$eval('.owl-prompt', node => node.textContent.match(/Choose the (\w+) face/)[1]);
  await click(expression);
  await page.waitForFunction(() => document.querySelector('.owl-prompt')?.textContent.includes('Round complete'));

  await page.evaluate(() => document.querySelector('.owl-save').open = true);
  await page.$eval('[aria-label="Owl save path"]', node => node.value = '/Owl Test.game.json');
  await click('Save');
  await page.waitForFunction(() => document.querySelector('.owl-status')?.textContent.includes('Saved to My files'));
  assert.match(await page.evaluate(() => new TextDecoder().decode(window.fileStore.get('/Owl Test.game.json').data)), /"appId":"owl-companion"/);

  await page.evaluate(() => window.fileStore.set('/Bad.game.json', {
    data: new TextEncoder().encode('{"format":"wrong"}'),
    version: 'bad',
  }));
  await page.evaluate(() => window.targetPath = '/Bad.game.json');
  await click('Open');
  await page.waitForFunction(() => document.querySelector('.owl-status')?.textContent.includes('Could not open'));
  assert.match(await page.$eval('.owl-prompt', node => node.textContent), /Round complete/);

  await page.evaluate(() => {
    const first = window.instances[0];
    first.controller.abort();
    first.app.dispose();
    first.app.dispose();
    first.app.element.remove();
  });
  assert.equal(await page.$$('.owl-character').then(nodes => nodes.length), 1);
  await click('Start activity');
  assert.deepEqual(errors, []);
  console.log('PASS two independent owl instances, three activities, pause, save, invalid load and disposal');
} finally {
  await context.close();
  await browser.disconnect();
}
