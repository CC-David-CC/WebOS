import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {readFile} from 'node:fs/promises';
const browser=await puppeteer.connect({browserURL:process.env.CODI_TEST_CDP||'http://127.0.0.1:19255'}),ctx=await browser.createBrowserContext(),page=await ctx.newPage();
try{
 await page.evaluateOnNewDocument(()=>{const Original=window.AudioContext;window.audioContexts=[];window.AudioContext=class extends Original{constructor(...args){super(...args);window.audioContexts.push(this)}}});
 const manifest=JSON.parse(await readFile(process.env.CODI_BLOCKS_MANIFEST||'.build/falling-test/apps.json','utf8'));
 const entry='/'+manifest.apps.find(a=>a.id==='falling-blocks').path.replace(/^assets\/desktop\//,'');
 await page.goto((process.env.CODI_BLOCKS_URL||'http://127.0.0.1:18302/')+'?app='+encodeURIComponent(entry));
 await page.waitForFunction(()=>document.querySelectorAll('.blocks-settings').length===2);
 await page.evaluate(()=>document.querySelectorAll('.blocks-settings').forEach(s=>s.open=true));
 const toggles=await page.$$('[aria-label="Sound effects"]');
 await toggles[0].click();await page.waitForFunction(()=>window.audioContexts.length===1&&window.audioContexts[0].state==='running');
 await toggles[1].click();await page.waitForFunction(()=>window.audioContexts.length===2&&window.audioContexts[1].state==='running');
 await toggles[0].click();await page.waitForFunction(()=>window.audioContexts[0].state==='suspended');
 assert.equal(await page.evaluate(()=>window.audioContexts[1].state),'running');
 await page.evaluate(()=>window.instances[0].app.dispose());
 await page.waitForFunction(()=>window.audioContexts[0].state==='closed');
 assert.equal(await page.evaluate(()=>window.audioContexts[1].state),'running');
 await page.evaluate(()=>window.instances[1].app.dispose());await page.waitForFunction(()=>window.audioContexts[1].state==='closed');
 console.log('PASS independent real browser AudioContexts, mute, and cleanup in two windows');
} finally {await ctx.close();await browser.disconnect()}
