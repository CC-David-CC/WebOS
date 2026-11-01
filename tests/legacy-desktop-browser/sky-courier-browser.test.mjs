import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19262'});
const context = await browser.createBrowserContext();
const page = await context.newPage();
const errors = [];
page.on('pageerror', error => errors.push(error.message));
page.on('dialog', dialog => dialog.accept());

const clickFirst = label => page.evaluate(label => {
 const root = document.querySelectorAll('.sky-courier')[0];
 const button = [...root.querySelectorAll('button')].find(node => node.textContent === label);
 if (!button) throw Error('Missing button: ' + label);
 button.click();
}, label);

try {
 const phone = process.env.CODI_PHONE === '1';
 await page.setViewport(phone ? {width: 412, height: 915, isMobile: true, hasTouch: true, deviceScaleFactor: 2} : {width: 1366, height: 900});
 const manifest = JSON.parse(await readFile(process.env.CODI_SKY_MANIFEST || '.build/sky-courier-test/apps.json', 'utf8'));
 const entry = '/' + manifest.apps[0].path.replace(/^assets\/desktop\//, '');
 await page.goto((process.env.CODI_SKY_URL || 'http://127.0.0.1:18345/') + '?app=' + encodeURIComponent(entry));
 await page.waitForFunction(() => window.instances?.length === 2);
 await page.waitForFunction(() => document.querySelectorAll('.sky-stage canvas').length === 2, {timeout: 30000});
 assert.match(await page.$eval('.sky-summary', node => node.textContent), /Stage 1/);
 await clickFirst('Resume');
 await page.waitForFunction(() => document.querySelector('.sky-summary')?.textContent.includes('route 0%') === false);
 await page.evaluate(() => document.querySelectorAll('.window')[0].classList.remove('focused'));
 await page.waitForFunction(() => document.querySelectorAll('.sky-courier')[0].querySelector('.sky-status')?.textContent.includes('lost attention'));
 await page.evaluate(() => document.querySelectorAll('.window')[0].classList.add('focused'));
 await clickFirst('Resume');
 if (phone) {
  const button = await page.$('.sky-controls [aria-label="Right ▶"]');
  await button.tap();
 } else {
  await page.focus('.sky-stage');
  await page.keyboard.down('ArrowRight');
  await new Promise(resolve => setTimeout(resolve, 180));
  await page.keyboard.up('ArrowRight');
 }
 await clickFirst('Fire');
 await page.waitForFunction(() => document.querySelectorAll('.sky-courier')[0].querySelector('.sky-summary')?.textContent.includes('route'));
 await page.evaluate(() => document.querySelectorAll('.sky-courier')[0].querySelector('.sky-save').open = true);
 await page.$eval('[aria-label="Sky Courier save path"]', node => node.value = '/Sky Courier.game.json');
 await clickFirst('Save checkpoint');
 await page.waitForFunction(() => document.querySelector('.sky-status')?.textContent.includes('Checkpoint saved'));
 const saved = await page.evaluate(() => JSON.parse(new TextDecoder().decode(window.fileStore.get('/Sky Courier.game.json').data)));
 assert.equal(saved.appId, 'sky-courier');
 assert.equal(saved.payload.paused, true);
 assert.equal(saved.payload.lives, 3);

 await page.evaluate(() => window.fileStore.set('/Bad.game.json', {data: new TextEncoder().encode('{bad'), version: 'bad', status: 'synced'}));
 await page.evaluate(() => window.target = '/Bad.game.json');
 await clickFirst('Open from My files');
 await page.waitForFunction(() => document.querySelector('.sky-status')?.textContent.includes('Could not open checkpoint'));
 await page.evaluate(() => window.target = '/Sky Courier.game.json');
 await clickFirst('Open from My files');
 await page.waitForFunction(() => document.querySelector('.sky-status')?.textContent.includes('Checkpoint loaded and paused'));
 assert.equal(await page.$eval('[aria-label="Sky Courier save path"]', node => node.value), '/Sky Courier.game.json');

 await page.evaluate(() => {
  const first = window.instances[0];
  first.controller.abort();
  first.app.dispose();
  first.app.dispose();
  first.app.element.remove();
 });
 assert.equal(await page.$$('.sky-stage canvas').then(nodes => nodes.length), 1);
 assert.deepEqual(errors, []);
 console.log(`PASS ${phone ? 'phone' : 'desktop'} Sky Courier render, steer/fire, checkpoint save/open, invalid recovery and disposal`);
} catch (error) {
 console.error('Diagnostics:', await page.evaluate(() => document.body.innerText.slice(0, 2000)).catch(() => ''));
 throw error;
} finally {
 await context.close();
 await browser.disconnect();
}
