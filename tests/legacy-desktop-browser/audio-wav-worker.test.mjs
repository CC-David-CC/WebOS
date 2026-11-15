import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
import {readFile} from 'node:fs/promises';
const catalog=JSON.parse(await readFile(process.env.CODI_AUDIO_CATALOG||'active-system/.build/simplified-apps/apps.json','utf8'));
const entry=catalog.apps.find(a=>a.id==='audio-editor').path;
const workerURL='/'+entry.replace(/index\.mjs$/,'workers/wav.mjs');
const browser=await puppeteer.connect({browserURL:process.env.CODI_BROWSER_URL||'http://127.0.0.1:19255'}),context=await browser.createBrowserContext(),page=await context.newPage();
try {
 await page.goto(process.env.CODI_TEST_URL||'http://127.0.0.1:18256/');
 const precision=await page.evaluate(async workerURL=>{async function encode(format,arrays){const worker=new Worker(workerURL,{type:'module'});try{return await new Promise((resolve,reject)=>{worker.onerror=()=>reject(Error('Worker failed'));worker.onmessage=async({data})=>{if(data.type==='error')return resolve({error:data.message});if(data.type==='ready'){const parts=arrays.map(x=>new Float32Array(x));worker.postMessage({type:'chunk',offset:0,parts},parts.map(p=>p.buffer));return}const b=new Uint8Array(await data.blob.arrayBuffer());resolve([...b])};worker.postMessage({type:'start',length:arrays[0].length,numberOfChannels:arrays.length,sampleRate:32000,format})})}finally{worker.terminate()}}return {pcm24:await encode('pcm24',[[-1,0,1]]),stereo:await encode('pcm24',[[-1,.5],[1,-.5]]),float:await encode('float32',[[-1.25,0,.75,1.25]]),invalid:await encode('float32',[[NaN]])}},workerURL);
 const a=Uint8Array.from(precision.pcm24),av=new DataView(a.buffer);assert.equal(av.getUint16(20,true),1);assert.equal(av.getUint16(34,true),24);assert.equal(av.getUint32(24,true),32000);assert.equal(av.getUint32(40,true),9);assert.equal(a.length,54,'odd PCM data is padded');assert.deepEqual([...a.slice(44,53)],[0,0,128,0,0,0,255,255,127]);assert.equal(a[53],0);
 const stereo=Uint8Array.from(precision.stereo);assert.equal(new DataView(stereo.buffer).getUint16(22,true),2);assert.deepEqual([...stereo.slice(44,56)],[0,0,128,255,255,127,255,255,63,0,0,192],'24-bit samples are interleaved by frame');
 const f=Uint8Array.from(precision.float),fv=new DataView(f.buffer);assert.equal(fv.getUint16(20,true),3);assert.equal(fv.getUint16(34,true),32);assert.equal(String.fromCharCode(...f.slice(36,40)),'fact');assert.equal(fv.getUint32(44,true),4);assert.equal(String.fromCharCode(...f.slice(48,52)),'data');assert.deepEqual([0,1,2,3].map(i=>fv.getFloat32(56+4*i,true)),[-1.25,0,.75,1.25]);assert.match(precision.invalid.error,/non-finite/);
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
 console.log('PASS 16-bit, 24-bit, float, stereo, clipping, padding and 128 MiB worker boundary');
}finally{await context.close();await browser.disconnect()}
