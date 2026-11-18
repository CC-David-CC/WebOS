/** Qualify the linked FigCraft editor inside an actual account desktop. */
import assert from 'node:assert/strict';
import {randomBytes} from 'node:crypto';
import {mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const {WEBOS_VIEWER_ORIGIN:origin,WEBOS_TEST_OUTPUT:output} = process.env;
assert(path.isAbsolute(output) && new URL(origin).hostname === '127.0.0.1');
assert.equal((await (await fetch(origin+'/healthz')).json()).scope,'development');
await mkdir(output,{mode:0o700});
const username = 'fig' + randomBytes(6).toString('hex');
const password = randomBytes(12).toString('hex');
const selector = '.window:has(.webos-figcraft)';
const files = '.window:has(.webos-files)';
const project = 'Documents/Browser.figcraft';
const checks = [], errors = [];

async function button(page, scope, label) {
  const handle = await page.waitForFunction((container,label) =>
    [...document.querySelectorAll(container+' button')].find(node => !node.disabled &&
      [node.getAttribute('aria-label'),(node.querySelector('.row-text')||node).textContent.trim()].includes(label)),
  {}, scope, label);
  try { await handle.asElement().click(); }
  finally { await handle.dispose(); }
}

async function launch(page, menu, app) {
  await page.click('.app-menu-button');
  await button(page,'.menu-pane',menu);
  await button(page,'.menu-pane',app);
}

async function login(page, register) {
  await page.setViewport({width:1440,height:1000});
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(origin,{waitUntil:'networkidle0'});
  await page.waitForSelector('.login-gate');
  if (register) await page.click('.login-toggle');
  await page.type('[aria-label="Username"]',username);
  await page.type('[aria-label="Password"]',password);
  if (register) await page.type('[aria-label="Confirm password"]',password);
  await button(page,'.login-gate',register?'Register':'Sign in');
  await page.waitForFunction(()=>!!window.desktopLab?.session && !document.querySelector('.login-gate'));
}

async function ready(page) {
  await page.waitForSelector(selector,{timeout:30_000});
  await page.$eval(selector,window=>window.appView?.ready);
  return page.waitForSelector(selector+' iframe:not([inert])',{timeout:120_000});
}

let browser, page;
try {
  browser = await puppeteer.launch({
    executablePath:process.env.WEBOS_TEST_CHROMIUM||'/snap/chromium/current/usr/lib/chromium-browser/chrome',
    headless:true,
    args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-background-networking'],
  });
  page = await browser.newPage();
  await login(page,true);
  await launch(page,'Graphics','FigCraft');
  const iframe = await ready(page);
  const frame = await iframe.contentFrame();
  await frame.waitForSelector('canvas#figcraft_canvas');
  checks.push('FigCraft starts from the classic Desktop menu');

  const bounds = await iframe.boundingBox();
  assert(bounds && bounds.width>400 && bounds.height>300);
  await page.mouse.click(bounds.x+bounds.width*.51,bounds.y+bounds.height*.49);
  await page.keyboard.press('r');
  await page.mouse.move(bounds.x+bounds.width*.45,bounds.y+bounds.height*.43);
  await page.mouse.down();
  await page.mouse.move(bounds.x+bounds.width*.61,bounds.y+bounds.height*.65,{steps:10});
  await page.mouse.up();
  await page.waitForFunction(view=>document.querySelector(view)?.appView.lifecycle.snapshot().dirty===true,{},selector);
  checks.push('Drawing on the native canvas changes the document');

  await page.keyboard.down('Control');
  await page.keyboard.press('s');
  await page.keyboard.up('Control');
  const picker = 'dialog.codi-file-picker[open]', prompt = 'dialog.codi-confirm-dialog[open]';
  await button(page,picker,'Open folder Documents');
  await button(page,picker,'Use this folder');
  await page.waitForSelector(prompt+' input');
  await page.$eval(prompt+' input',input=>{input.value='Browser';});
  await button(page,prompt,'Save');
  const title = 'Browser.figcraft — FigCraft';
  await page.waitForFunction((view,title)=>document.querySelector(view+' .caption-text')?.textContent===title,{},selector,title);
  checks.push('Native Save creates an account-backed FigCraft project');

  const fresh = await browser.createBrowserContext();
  page = await fresh.newPage();
  await login(page,false);
  await launch(page,'System Tools','Files');
  await page.waitForFunction(files=>!!document.querySelector(files)?.appView,{},files);
  const saved = await page.$eval(files,async (window,project)=>{
    await window.appView.ready;
    await window.appView.execute('list',{path:'Documents'});
    const receipt = await window.appView.execute('snapshot',{path:project});
    await window.appView.execute('open',{path:project});
    return receipt.sha256;
  },project);
  assert.match(saved,/^[a-f0-9]{64}$/);
  await ready(page);
  assert.equal(await page.$eval(selector+' .caption-text',node=>node.textContent),title);
  assert.equal(await page.$eval(selector,node=>[...window.desktopLab.surfaces.values()]
    .flatMap(surface=>surface.windows).find(window=>String(window.id)===node.dataset.window)?.launchContext?.sha256),saved);
  checks.push('A fresh browser signs in and opens the server revision from Files');
  assert.deepEqual(errors,[]);
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'PASS',checks,errors})+'\n');
} catch (error) {
  const status = await page?.$eval(selector+' [role=status]',node=>node.textContent).catch(()=>null);
  await writeFile(path.join(output,'result.json'),JSON.stringify({status:'FAIL',checks,errors,error:error.message,editorStatus:status})+'\n');
  throw error;
} finally {
  await browser?.close();
}
