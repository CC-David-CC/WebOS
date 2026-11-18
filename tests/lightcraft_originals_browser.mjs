/** Prove detached LightCraft originals through the real account Storage service. */
import assert from 'node:assert/strict';
import {createHash,randomBytes} from 'node:crypto';
import {mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {build} from 'esbuild';
import puppeteer from 'puppeteer-core';

const {WEBOS_VIEWER_ORIGIN:origin,WEBOS_TEST_OUTPUT:output} = process.env;
assert.equal(new URL(origin).hostname,'127.0.0.1');
assert(path.isAbsolute(output));
assert.equal((await (await fetch(origin+'/healthz')).json()).scope,'development');
await mkdir(output,{mode:0o700});

const {outputFiles:[bundle]} = await build({
  entryPoints:['assembly/viewer/lightcraft-account-originals.mjs'],
  bundle:true,write:false,format:'iife',globalName:'lightCraftStorageFixture',platform:'browser',
});
const credentials = () => ({username:'lc'+randomBytes(6).toString('hex'),password:randomBytes(12).toString('hex')});
const checks = [];
let browser;

async function openFiles(credentials, register) {
  const context = await browser.createBrowserContext();
  const page = await context.newPage();
  await page.goto(origin,{waitUntil:'domcontentloaded'});
  await page.waitForSelector('.login-gate button[type=submit]');
  if (register) await page.click('.login-toggle');
  await page.type('[aria-label="Username"]',credentials.username);
  await page.type('[aria-label="Password"]',credentials.password);
  if (register) await page.type('[aria-label="Confirm password"]',credentials.password);
  await page.click('.login-gate button[type="submit"]');
  await page.waitForFunction(()=>window.desktopLab?.session && !document.querySelector('.login-gate'));
  await page.evaluate(bundle.text);
  await page.evaluate(async ()=>{
    const desktop = window.desktopLab.surfaces.get('Desktop');
    const model = desktop.launch('files');
    const host = await publicAppHost(desktop,model,'files');
    const context = await host.storage.accountFileContext();
    window.originalsFixture = lightCraftStorageFixture.createLightCraftOriginalStore({
      files:context.files,valid:()=>desktop.windows.includes(model) && context.valid(),signal:host.signal,
    });
  });
  return {context,page};
}

try {
  browser = await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true,args:['--disable-dev-shm-usage','--disable-background-networking'],
  });
  const account = credentials();
  const bytes = Array.from(randomBytes(128));
  const digest = createHash('sha256').update(Buffer.from(bytes)).digest('hex');
  const first = await openFiles(account,true);
  const writes = await first.page.evaluate(bytes=>Promise.all([
    originalsFixture.store(Uint8Array.from(bytes)), originalsFixture.store(Uint8Array.from(bytes)),
  ]),bytes);
  assert.deepEqual(writes,[digest,digest]);
  checks.push('Identical originals share one digest under the signed account');
  await first.context.close();

  const fresh = await openFiles(account,false);
  const reopened = await fresh.page.evaluate(async digest=>Array.from(await originalsFixture.read(digest)),digest);
  assert.deepEqual(reopened,bytes);
  checks.push('A fresh Chromium context verifies and reopens the account original');
  await fresh.context.close();

  const other = await openFiles(credentials(),true);
  const denied = await other.page.evaluate(digest=>originalsFixture.read(digest).then(
    ()=>false,error=>error.status===404,
  ),digest);
  assert.equal(denied,true);
  checks.push('A separate account cannot retrieve the original using its digest');
  await other.context.close();
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks})+'\n',{flag:'wx',mode:0o600});
} catch (error) {
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'FAIL',checks,error:error.message})+'\n',{flag:'wx',mode:0o600});
  throw error;
} finally {
  await browser?.close();
}
