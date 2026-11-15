// Real Chromium exercise of the public staging allowlist, under a strict CSP.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createServer} from 'node:http';
import {mkdtemp,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import puppeteer from 'puppeteer-core';

const root=fileURLToPath(new URL('../',import.meta.url));
const temporary=await mkdtemp(join(tmpdir(),'codi-staged-storage-'));
const publicRoot=join(temporary,'public'),requests=new Set();
let browser;
execFileSync('python3',['-c',
  'import pathlib,sys;sys.path.insert(0,sys.argv[1]);from origin_service.public_storage import stage_browser_storage;out=pathlib.Path(sys.argv[2]);out.mkdir();stage_browser_storage(pathlib.Path(sys.argv[1]),out)',
  join(root,'active-system'),publicRoot]);
const server=createServer(async(request,response)=>{
  const path=new URL(request.url,'http://localhost').pathname;
  response.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; worker-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'");
  if(path==='/'){response.setHeader('Content-Type','text/html');response.end('<!doctype html><title>Staged storage</title>');return;}
  const target=resolve(publicRoot,'.'+path);
  if(!target.startsWith(publicRoot+'/')){response.writeHead(404);response.end();return;}
  try{const data=await readFile(target);requests.add(path);response.setHeader('Content-Type',path.endsWith('.mjs')?'text/javascript':'text/plain');response.end(data);}
  catch{response.writeHead(404);response.end();}
});
try{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  browser=await puppeteer.launch({executablePath:process.env.CHROME,userDataDir:join(temporary,'profile'),headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage(),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/');
  const result=await page.evaluate(async()=>{
    const {createAccountFileMirror}=await import('/storage/browser/account-context.mjs');
    const owner='staged-'+crypto.randomUUID(),server={async list(){throw Error('offline')}};
    const options={issuer:location.origin,owner,server,valid:()=>true,storage:{version:'codi-browser-file-content/1',backend:'opfs',databaseVersion:2}};
    let unsupported=false,invalidated=false;
    try{createAccountFileMirror({...options,storage:{...options.storage,databaseVersion:99}});}catch{unsupported=true;}
    try{createAccountFileMirror({...options,valid:()=>false});}catch{invalidated=true;}
    if(!unsupported||!invalidated)throw Error('Invalid storage/session configuration was accepted');
    const files=createAccountFileMirror(options);
    const saved=await files.write('/note','saved through the staged worker');
    files.close();
    const restored=createAccountFileMirror(options);
    try{
      const read=await restored.readBounded('/note',128);
      return {text:new TextDecoder().decode(read.data),version:read.version,savedVersion:saved.version,status:read.status};
    }finally{restored.close();}
  });
  assert.equal(result.text,'saved through the staged worker');
  assert.equal(result.version,result.savedVersion);
  assert.equal(result.status,'pending');
  assert.deepEqual(errors,[]);
  for(const name of ['account-context.mjs','mirror.mjs','verified-content.mjs','opfs/store.mjs','opfs/worker.mjs','opfs/core.mjs','opfs/shared.mjs']){
    assert.ok(requests.has('/storage/browser/'+name),'staged runtime requested '+name);
  }
  console.log('PASS staged mirror imports, strict-CSP worker capture and reopen');
}finally{
  await browser?.close();
  await new Promise(resolve=>server.close(resolve));
  await rm(temporary,{recursive:true,force:true});
}
