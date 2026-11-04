import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {spawn} from 'node:child_process';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const profile=await mkdtemp(join(tmpdir(),'codi-content-browser-'));
const http=spawn('python3',['-m','http.server','19923','--bind','127.0.0.1'],{stdio:'ignore'});
let browser;
try{
 await new Promise(r=>setTimeout(r,300));
 browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:profile,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage(); await page.goto('http://127.0.0.1:19923/');
 const result=await page.evaluate(async()=>{
  const {MirroredFiles}=await import('/active-system/storage/browser/mirror.mjs');
  const {VerifiedContent}=await import('/active-system/storage/browser/verified-content.mjs');
  const scope='browser-'+crypto.randomUUID(), server={async list(){throw Error('offline')}};
  const legacy=new MirroredFiles({scope,server,retryMs:0}), old=await legacy.write('/note','before');legacy.close();
  const store=new VerifiedContent(scope), m=new MirroredFiles({scope,server,content:store,retryMs:0});
  await m.migrateContent('/note',old.version);
  const migrated=await(await m.readBlob('/note')).data.text();
  const saved=await m.write('/note',new Blob(['after']),old.version);
  m.close();store.close();
  const reopenedStore=new VerifiedContent(scope),reopened=new MirroredFiles({scope,server,content:reopenedStore,retryMs:0});
  const after=await(await reopened.readBlob('/note')).data.text();
  const copied=await reopened.copyFile('/note','/copy',saved.version);
  const copy=await(await reopened.readBlob('/copy')).data.text();
  await reopened.remove('/copy',copied.version);reopened.close();reopenedStore.close();
  return {migrated,after,copy};
 });
 assert.deepEqual(result,{migrated:'before',after:'after',copy:'after'});
 console.log('PASS real Chromium OPFS mirror migration, save, reopen and copy');
}finally{
 await browser?.close();http.kill('SIGTERM');await rm(profile,{recursive:true,force:true});
}
