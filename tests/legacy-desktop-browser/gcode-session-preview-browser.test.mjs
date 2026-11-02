import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile,realpath} from 'node:fs/promises';
import {resolve,sep,extname} from 'node:path';
import {createRequire} from 'node:module';

// An isolated host stand-in makes the file-session change deterministic while
// the actual bundled preview, renderer and parse worker execute in Chromium.
for(const [layout,viewport] of [['desktop',{width:1366,height:900}],['phone',{width:412,height:915,isMobile:true,hasTouch:true}]]) test(`stale file context preserves the rendered preview (${layout})`,async()=>{
 const root=await realpath(process.env.CODI_GCODE_BUNDLE||'');
 const require=createRequire(resolve(process.env.PUPPETEER_CORE_PATH||'.','package.json'));
 const puppeteer=require('puppeteer-core');
 const catalog=JSON.parse(await readFile(resolve(root,'apps.json'),'utf8'));
 const app=catalog.apps.find(item=>item.id==='gcode-preview');assert.ok(app);
 const path='/'+app.path.replace(/^assets\/desktop\//,'');
 const server=createServer(async(req,res)=>{try{
  if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html','Content-Security-Policy':"default-src 'self'; script-src 'self'; worker-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'"});res.end('<!doctype html><html><body></body></html>');return}
  const file=await realpath(resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname)));if(!file.startsWith(root+sep))throw Error('outside bundle');
  res.writeHead(200,{'Content-Type':extname(file)==='.mjs'?'text/javascript':'application/octet-stream'});res.end(await readFile(file));
 }catch{res.writeHead(404);res.end()}});
 await new Promise(done=>server.listen(0,'127.0.0.1',done));let browser;
 try{
  browser=await puppeteer.launch({executablePath:process.env.CODI_CHROMIUM,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader'],headless:true});
  const page=await browser.newPage();await page.setViewport(viewport);const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.evaluate(async path=>{
   const NativeWorker=window.Worker;window.Worker=class{
    constructor(...args){this.worker=new NativeWorker(...args);this.worker.onmessage=e=>{if(window.holdParse)window.releaseParse=()=>this.onmessage(e);else this.onmessage(e)};this.worker.onerror=e=>this.onerror?.(e);this.worker.onmessageerror=e=>this.onmessageerror?.(e)}
    postMessage(...args){this.worker.postMessage(...args)} terminate(){this.worker.terminate()}
   };
   const {mount}=await import(path);window.contextValid=true;
   const data='G21\nG90\nG0 X0 Y0 Z0.2\nG1 X10 Y10 E1\n';
   const c={path:p=>p,valid:()=>window.contextValid,files:{read:async()=>({data:new TextEncoder().encode(data),version:'v1',status:'clean'}),stat:async()=>({version:'v1',status:'clean'}),subscribe:()=>()=>{}}};
   const make=(tag,cls,text)=>{const e=document.createElement(tag);e.className=cls;if(text)e.textContent=text;return e};
   const host={w:{},desktop:{launch(){}},signal:new AbortController().signal,storage:{signedInSubject:()=> 'user:a',mirrorFileContext:async()=>c,pickFile:async()=>'/test.gcode'},ui:{make,appInput:(label,value)=>{const e=document.createElement('input');e.setAttribute('aria-label',label);e.value=value;return e},textButton:(label,callback)=>{const e=document.createElement('button');e.textContent=label;e.setAttribute('aria-label',label);e.addEventListener('click',callback);return e}}};
   window.testHost=host;window.app=mount(host);document.body.append(app.element);
  },path);
  await page.click('[aria-label="Try example"]');await page.waitForFunction(()=>document.querySelector('.gcode-app .app-status').textContent.includes('Example loaded'),{timeout:20000});
  await page.evaluate(()=>{window.previousCanvas=document.querySelector('.gcode-stage canvas');window.holdParse=true});
  await page.click('[aria-label="Open from My files"]');await page.waitForFunction(()=>typeof window.releaseParse==='function',{timeout:20000});
  await page.evaluate(()=>{window.contextValid=false;window.releaseParse()});
  await page.waitForFunction(()=>document.querySelector('.gcode-app .app-status').textContent.includes('File session changed'),{timeout:20000});
  assert.equal(await page.evaluate(()=>document.querySelector('.gcode-stage canvas')===window.previousCanvas),true);
  assert.equal(await page.evaluate(()=>window.testHost.w.launchContext),null);
  await page.evaluate(()=>{window.contextValid=true;window.holdParse=false});await page.click('[aria-label="Open from My files"]');
  await page.waitForFunction(()=>document.querySelector('.gcode-app .app-status').textContent.includes('/test.gcode loaded'),{timeout:20000});
  assert.equal(await page.evaluate(()=>document.querySelector('.gcode-stage canvas')!==window.previousCanvas),true);
  assert.equal(await page.evaluate(()=>window.testHost.w.launchContext.path),'/test.gcode');
  await page.evaluate(()=>window.app.dispose());assert.deepEqual(errors,[]);
 }finally{if(browser)await browser.close();await new Promise(done=>server.close(done))}
});
