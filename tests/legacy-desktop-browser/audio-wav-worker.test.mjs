import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {readFile} from 'node:fs/promises';
const catalog=JSON.parse(await readFile(process.env.CODI_AUDIO_CATALOG||'active-system/.build/simplified-apps/apps.json','utf8'));
const entry=catalog.apps.find(a=>a.id==='audio-editor').path;
const workerURL='/'+entry.replace(/index\.mjs$/,'workers/wav.mjs');
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage();
try {
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18256/');
 const result=await page.evaluate(async ({workerURL,length})=>{
  const worker=new Worker(workerURL,{type:'module'});let offset=0,ticks=0;const timer=setInterval(()=>ticks++,10);
  try{return await new Promise((resolve,reject)=>{
   worker.onerror=()=>reject(Error('Worker failed to load'));
   worker.onmessage=async({data:m})=>{try{
    if(m.type==='error')throw Error(m.message);
    if(m.type==='ready'){const end=Math.min(offset+262144,length),part=new Float32Array(end-offset);part.fill(.5);worker.postMessage({type:'chunk',offset,parts:[part]},[part.buffer]);offset=end;return;}
    const bytes=new Uint8Array(await m.blob.slice(0,48).arrayBuffer()),view=new DataView(bytes.buffer);resolve({size:m.blob.size,magic:String.fromCharCode(...bytes.slice(0,4)),channels:view.getUint16(22,true),sample:view.getInt16(44,true),ticks});
   }catch(e){reject(e)}};
   worker.postMessage({type:'start',length,numberOfChannels:1,sampleRate:48000});
  });}finally{clearInterval(timer);worker.terminate()}
 },{workerURL,length:(128*1024*1024-44)/2});
 assert.equal(result.size,128*1024*1024);assert.equal(result.magic,'RIFF');assert.equal(result.channels,1);assert.equal(result.sample,16383);assert.ok(result.ticks>0,'UI thread remains responsive');
 const rejected=await page.evaluate(workerURL=>new Promise((resolve,reject)=>{const worker=new Worker(workerURL,{type:'module'});worker.onerror=()=>reject(Error('Worker failed'));worker.onmessage=({data})=>{worker.terminate();resolve(data)};worker.postMessage({type:'start',length:128*1024*1024,numberOfChannels:1,sampleRate:48000})}),workerURL);
 assert.equal(rejected.type,'error');assert.match(rejected.message,/128 MiB/);
 console.log('PASS 128 MiB WAV conversion off-thread, sample values and 128 MiB boundary rejection');
}finally{await context.close();await browser.disconnect()}
