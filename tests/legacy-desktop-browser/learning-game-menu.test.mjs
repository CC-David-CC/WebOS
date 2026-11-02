import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const url = process.env.CODI_TEST_URL || 'http://127.0.0.1:19479/';
if (!['http://127.0.0.1:19479', 'https://ksu.codes'].includes(new URL(url).origin)) throw Error('Unexpected test origin.');
const browser = await puppeteer.connect({browserURL: 'http://127.0.0.1:19255'});
try {
  for (const phone of [false, true]) {
    const context = await browser.createBrowserContext();
    try {
      const page = await context.newPage();
      await page.setViewport(phone ? {width: 390, height: 844, isMobile: true, hasTouch: true} : {width: 1440, height: 900});
      await page.goto(url);
      await page.waitForSelector('.login-toggle');
      await page.click('.login-toggle');
      const username = 'tilemenu' + Date.now().toString().slice(-8) + (phone ? 'b' : 'a');
      if (process.env.CODI_CLEANUP === '1') console.log('TEST_ACCOUNT ' + username);
      await page.type('[aria-label=Username]', username);
      await page.type('[aria-label=Password]', 'test1234');
      await page.type('[aria-label="Confirm password"]', 'test1234');
      await page.click('.login-form button[type=submit]');
      await page.waitForFunction(() => window.desktopLab?.session?.kind === 'registered');
      if (process.env.CODI_CLEANUP === '1') console.log('CLEANUP_ACCOUNT ' + username + ' ' + await page.evaluate(() => signedInSubject()));
      await page.evaluate(() => document.querySelector('[aria-label=Applications]').click());
      for (const label of ['Games', 'Learning & Strategy (in development)']) {
        await page.evaluate(label => {
          const item = [...document.querySelectorAll('.menu-pane button')].find(e => e.getAttribute('aria-label') === label);
          if (!item) throw Error('Missing menu: ' + label);
          item.click();
        }, label);
      }
      const items = await page.$$eval('.menu-pane[data-depth="2"] button', buttons => buttons.map(button => ({label: button.getAttribute('aria-label'), disabled: button.disabled})));
      for (const name of ['Math Path', 'Fraction Farm', 'Word Weaver', 'Rule Detective', 'Market Math', 'Pocket Conquest', 'Tile Islands']) {
        assert.ok(items.some(item => item.label === `${name} (in development)` && item.disabled), name);
      }
    } finally { await context.close(); }
  }
  console.log('PASS seven disabled learning games on desktop and emulated phone');
} finally { await browser.disconnect(); }
