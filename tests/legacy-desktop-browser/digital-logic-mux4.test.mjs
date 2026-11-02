import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';

const base = process.env.CODI_TEST_URL || 'http://127.0.0.1:19492/';
if (!['http://127.0.0.1:19492', 'https://ksu.codes'].includes(new URL(base).origin)) throw Error('Unexpected test origin');
const browser = await puppeteer.launch({executablePath: '/snap/chromium/current/usr/lib/chromium-browser/chrome', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage']});
const errors = [];
try {
  for (const phone of [false, true]) {
    const username = 'muxfour' + Date.now().toString().slice(-8) + (phone ? 'p' : 'd');
    if (process.env.CODI_CLEANUP === '1') console.log('TEST_ACCOUNT ' + username);
    const context = await browser.createBrowserContext();
    let fresh;
    try {
      const p = await context.newPage();
      p.on('pageerror', e => errors.push(e.message));
      async function login(page, register) {
        await page.setViewport(phone ? {width: 412, height: 915, isMobile: true, hasTouch: true} : {width: 1366, height: 900});
        await page.goto(base); await page.waitForSelector('.login-toggle');
        if (register) await page.click('.login-toggle');
        await page.type('[aria-label=Username]', username); await page.type('[aria-label=Password]', 'test1234');
        if (register) await page.type('[aria-label="Confirm password"]', 'test1234');
        await page.click('.login-form button[type=submit]');
        await page.waitForFunction(() => window.desktopLab?.session?.kind === 'registered');
      }
      const button = async (page, label) => page.evaluate(label => {
        const item = [...document.querySelectorAll('.digital-logic button')].find(e => e.textContent === label);
        if (!item) throw Error('Missing button ' + label); item.click();
      }, label);
      async function verifyTruth(page) {
        await button(page, 'Calculate truth table');
        await page.waitForFunction(() => document.querySelectorAll('.logic-truth-output tbody tr').length === 64, {timeout: 30000});
        const headers = await page.$$eval('.logic-truth-output thead th', cells => cells.map(c => c.textContent));
        const rows = await page.$$eval('.logic-truth-output tbody tr', rows => rows.map(r => [...r.cells].map(c => c.textContent)));
        assert.deepEqual(headers, ['D0', 'D1', 'D2', 'D3', 'S1', 'S0', 'Output']);
        assert.equal(new Set(rows.map(row => row.slice(0, 6).join(''))).size, 64);
        for (const row of rows) assert.equal(row[6], row[Number(row[4]) * 2 + Number(row[5])], row.join(','));
        return rows;
      }
      await login(p, true);
      await p.evaluate(() => surfaces.get('Desktop').launch('digital-logic'));
      await p.waitForFunction(() => document.querySelector('.logic-status')?.textContent.startsWith('Simulation running'));
      await p.select('[aria-label="Gate example"]', 'MUX4'); await button(p, 'Load example');
      await p.waitForSelector('[aria-label="D2 input: off"]');
      const rows = await verifyTruth(p);
      await p.click('[aria-label="D2 input: off"]'); await p.click('[aria-label="S1 input: off"]');
      await p.waitForFunction(() => document.querySelector('.logic-output-values')?.textContent === 'Output: 1');
      await p.click('[aria-label="S0 input: off"]');
      await p.waitForFunction(() => document.querySelector('.logic-output-values')?.textContent === 'Output: 0');
      await button(p, 'Save truth table CSV'); await p.waitForFunction(() => document.querySelector('.logic-status')?.textContent.startsWith('Truth table saved'));
      await button(p, 'Save to My files'); await p.waitForFunction(() => document.querySelector('.logic-status')?.textContent.startsWith('Saved /4-to-1-multiplexer.logic.json'));
      await p.evaluate(async () => await (await mirrorFileContext()).files.sync());
      const saved = await p.evaluate(async () => {const f = (await serverFileContext()).files;return {circuit: JSON.parse(new TextDecoder().decode((await f.read('4-to-1-multiplexer.logic.json')).data)), csv: new TextDecoder().decode((await f.read('Truth-table.csv')).data)};});
      assert.equal(saved.circuit.devices.combine.inputs, 4);
      assert.equal(saved.csv, ['"D0","D1","D2","D3","S1","S0","Output"', ...rows.map(row => row.map(x => '"' + x + '"').join(',')), ''].join('\r\n'));
      await p.evaluate(() => document.querySelector('.digital-logic').closest('.window').querySelector('[aria-label=Close]').click());
      await p.waitForSelector('.digital-logic', {hidden: true});
      fresh = await browser.createBrowserContext(); const q = await fresh.newPage(); await login(q, false);
      await q.evaluate(async () => {await (await mirrorFileContext()).files.sync();openMirrorDocument(surfaces.get('Desktop'), signedInSubject(), '/4-to-1-multiplexer.logic.json');});
      await q.waitForSelector('[aria-label="D2 input: off"]', {timeout: 30000}); await verifyTruth(q);
      await q.evaluate(() => document.querySelector('.digital-logic').closest('.window').querySelector('[aria-label=Close]').click());
      await q.waitForSelector('.digital-logic', {hidden: true});
      assert.deepEqual(errors, []);
      if (process.env.CODI_CLEANUP === '1') {
        await fresh.close(); fresh = null;
        const subject = await p.evaluate(async () => {
          const c = await mirrorFileContext();
          for (const path of ['/4-to-1-multiplexer.logic.json', '/Truth-table.csv']) {
            const file = await c.files.stat(path); await c.files.remove(path, file.version);
          }
          await c.files.sync(); return c.owner;
        });
        console.log('CLEANUP_ACCOUNT ' + username + ' ' + subject);
      }
    } finally { await fresh?.close(); await context.close(); }
  }
  console.log('PASS 64 mux rows, controls, CSV and project sync, fresh reopen and cleanup on desktop/phone');
} finally { await browser.close(); }
