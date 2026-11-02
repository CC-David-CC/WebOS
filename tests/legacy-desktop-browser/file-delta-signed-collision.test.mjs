import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const base=new URL(process.env.CODI_TEST_URL||'http://127.0.0.1:19873/');assert.ok(['127.0.0.1','localhost'].includes(base.hostname));
const browser=await puppeteer.connect({browserURL:'http://127.0.0.1:19255'}),context=await browser.createBrowserContext();
try{
 const page=await context.newPage();await page.goto(base.href);await page.waitForSelector('.login-toggle');await page.click('.login-toggle');await page.type('[aria-label=Username]','collision'+Date.now().toString().slice(-8));await page.type('[aria-label=Password]','test1234');await page.type('[aria-label="Confirm password"]','test1234');await page.click('.login-form button[type=submit]');await page.waitForFunction(()=>window.desktopLab?.session?.kind==='registered',{timeout:30000});
 const result=await page.evaluate(async()=>{
  const server=(await serverFileContext()).files,base=new Uint8Array(65536).fill(100);const initial=await server.write('collision.bin',base,null);
  const original=server.request.bind(server);let used='';
  server.request=async(op,...args)=>{if(op==='delta-signatures')return {version:'codi-file-delta/1',size:65536,block:65536,sha256:initial.sha256,chunks:[[787416541,'f'.repeat(64)]]};if(op==='replace'||op==='replace-delta')used=op;return original(op,...args)};
  const data=new Uint8Array(1024*1024);for(let i=0;i<data.length;i++)data[i]=[101,98,101,100][i%4];const written=await server.write('collision.bin',data,initial.sha256);const read=await server.read('collision.bin');
  if(used!=='replace'||written.sha256!==read.sha256||read.data.length!==data.length||read.data.some((x,i)=>x!==data[i]))throw Error('Collision fallback did not commit verified full replacement');return {used,bytes:read.data.length};
 });assert.equal(result.used,'replace');console.log('PASS signed account collision fallback:',JSON.stringify(result));
}finally{await context.close();await browser.disconnect()}
