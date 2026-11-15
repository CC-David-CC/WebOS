import assert from 'node:assert/strict';import puppeteer from 'puppeteer-core';import {spawn} from 'node:child_process';import {mkdtemp,rm} from 'node:fs/promises';import {tmpdir} from 'node:os';import {join} from 'node:path';
const profile=await mkdtemp(join(tmpdir(),'codi-gc-crash-')),http=spawn('python3',['-m','http.server','19933','--bind','127.0.0.1'],{stdio:'ignore'});let browser;
const opts={executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']};
try{await new Promise(r=>setTimeout(r,250));browser=await puppeteer.launch(opts);let page=await browser.newPage();await page.goto('http://127.0.0.1:19933/');
 await page.evaluate(async()=>{const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs'),scope='gc-crash',server={async list(){throw Error('offline')}},m=new MirroredFiles({scope,server,content:new VerifiedContent(scope),retryMs:0});let row=await m.write('/x','old');await m.write('/x','current',row.version);
 const orig=FileSystemDirectoryHandle.prototype.removeEntry;FileSystemDirectoryHandle.prototype.removeEntry=async function(...args){await orig.apply(this,args);window.afterUnlink=true;await new Promise(()=>{})};
 window.collect=(async()=>{let cursor=null;do{const r=await m.collectGarbage({cursor,limit:16});cursor=r.next}while(cursor)})().catch(()=>{});
 });
 await page.waitForFunction('window.afterUnlink===true',{timeout:15000,polling:50});
 const exited=new Promise(r=>browser.process().once('exit',r));browser.process().kill('SIGKILL');await exited;browser=null;
 browser=await puppeteer.launch(opts);page=await browser.newPage();await page.goto('http://127.0.0.1:19933/');
 const result=await page.evaluate(async()=>{const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs'),{VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs'),scope='gc-crash',server={async list(){throw Error('offline')}},m=new MirroredFiles({scope,server,content:new VerifiedContent(scope),retryMs:0});let cursor=null,removed=0;do{const r=await m.collectGarbage({cursor,limit:16});removed+=r.removed;cursor=r.next}while(cursor);const text=new TextDecoder().decode((await m.read('/x')).data);m.close();return {removed,text}});
 assert.deepEqual(result,{removed:1,text:'current'});console.log('PASS interrupted post-unlink collection resumes idempotently and preserves current data');
}finally{await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true})}
