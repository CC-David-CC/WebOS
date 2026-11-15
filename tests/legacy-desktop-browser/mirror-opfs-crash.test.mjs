import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const profile=await mkdtemp(join(tmpdir(),'codi-content-crash-'));
const http=spawn('python3',['-m','http.server','19924','--bind','127.0.0.1'],{stdio:'ignore'});
const opts={executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']};
let browser;
try{
 await new Promise(r=>setTimeout(r,300));browser=await puppeteer.launch(opts);let page=await browser.newPage();await page.goto('http://127.0.0.1:19924/');
 await page.evaluate(async()=>{
 const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
 const scope='crash-test',server={async list(){throw Error('offline')}},legacy=new MirroredFiles({scope,server,retryMs:0});
 const row=await legacy.write('/note','original');legacy.close();
 const real=new VerifiedContent(scope),content={async capture(blob){const ref=await real.capture(blob);window.candidateClosed=true;await new Promise(()=>{});return ref},read:ref=>real.read(ref)};
 const mirror=new MirroredFiles({scope,server,content,retryMs:0});mirror.migrateContent('/note',row.version).catch(()=>{});
 });
 await page.waitForFunction('window.candidateClosed === true',{timeout:30000});
 const exit=new Promise(r=>browser.process().once('exit',r));browser.process().kill('SIGKILL');await exit;browser=null;
 browser=await puppeteer.launch(opts);page=await browser.newPage();await page.goto('http://127.0.0.1:19924/');
 const result=await page.evaluate(async()=>{const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');const scope='crash-test',server={async list(){throw Error('offline')}},content=new VerifiedContent(scope),mirror=new MirroredFiles({scope,server,content,retryMs:0});const row=await mirror.read('/note'),text=new TextDecoder().decode(row.data),status=row.status;mirror.close();content.close();return {text,status}});
 assert.deepEqual(result,{text:'original',status:'pending'});
 await page.evaluate(async()=>{const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');const scope='crash-test',server={async list(){throw Error('offline')}},content=new VerifiedContent(scope),mirror=new MirroredFiles({scope,server,content,retryMs:0});const row=await mirror.read('/note');await mirror.write('/note','published',row.version);mirror.close();content.close()});
 const exit2=new Promise(r=>browser.process().once('exit',r));browser.process().kill('SIGKILL');await exit2;browser=null;
 browser=await puppeteer.launch(opts);page=await browser.newPage();await page.goto('http://127.0.0.1:19924/');
 const after=await page.evaluate(async()=>{const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');const scope='crash-test',server={async list(){throw Error('offline')}},content=new VerifiedContent(scope),mirror=new MirroredFiles({scope,server,content,retryMs:0});const row=await mirror.read('/note'),out={text:new TextDecoder().decode(row.data),status:row.status};mirror.close();content.close();return out});
 assert.deepEqual(after,{text:'published',status:'pending'});
 console.log('PASS browser SIGKILL before and after mirror publication retains correct pending file');
}finally{await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true})}
