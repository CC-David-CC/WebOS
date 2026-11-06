import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {cmd,frame} from '../numeric-expressions/helpers.mjs';
export {harness,cmd,launch,frame,sync,save,reopen} from '../numeric-expressions/helpers.mjs';
export {append,plane} from '../signed-distance/helpers.mjs';
export function requiredPins(){
 assert.equal(new URL(process.env.CODI_TEST_URL).port,process.env.CODI_TEST_PORT||'20406','Fresh isolated signed fixture required');
 assert.match(process.env.CODI_SOURCE||'',/^[a-f0-9]{40}$/);
 assert.match(process.env.CODI_EXPECTED_SELECTED_WORKER_SHA||'',/^[a-f0-9]{64}$/);
 for(const name of['APP','SKETCH','PROJECT','SEMANTIC'])assert.match(process.env['CODI_EXPECTED_'+name+'_SHA']||'',/^[a-f0-9]{64}$/);
}
export async function verifyRuntime(p){
 const origin=new URL((await frame(p)).url()),cookies=await p.cookies(origin.href);
 async function read(url){const r=await fetch(url,{headers:{cookie:cookies.map(c=>c.name+'='+c.value).join('; ')}});assert.equal(r.status,200);return Buffer.from(await r.arrayBuffer());}
 const sha=b=>createHash('sha256').update(b).digest('hex'),url=new URL('static/index.bundle.js',origin),app=await read(url),assets={app:{url:url.href,sha256:sha(app)}};
 assert.equal(assets.app.sha256,process.env.CODI_EXPECTED_APP_SHA);
 for(const [name,stem] of[['SKETCH','sketch-solver'],['PROJECT','project-validator'],['SEMANTIC','prism-semantic']]){
  const refs=[...new Set(app.toString().match(new RegExp(stem+'\\.[a-f0-9]+\\.js','g')))];assert.equal(refs.length,1);
  const u=new URL('static/'+refs[0],origin),bytes=await read(u);assets[name.toLowerCase()]={url:u.href,sha256:sha(bytes)};assert.equal(sha(bytes),process.env['CODI_EXPECTED_'+name+'_SHA']);
 }
 for(const [name,want] of[
  ['selected-profile-worker.js',process.env.CODI_EXPECTED_SELECTED_WORKER_SHA],
  ['selected-profile-occ-portable.js','cbd49d63d0900f50dda7fc53518d5f06183e85b1dea720522cc2994b0876adc9'],
  ['a81af0b78dd585124f3f.wasm','a81af0b78dd585124f3f2d05d09b4a387b276bd1f655f0234002a6ab4646a637'],
  ['oci-verified-worker.js','6189a58b58667c4bca68c67e1593f8656d04ad0875162b301659392a82fd96e4'],
  ['occ-portable.js','a84b31900e58e61a1d7e3f8d04978408455764ad149923359e7fba19d3d07884'],
  ['manifold-verified-worker.js','35876bd7cd773b5eb243fde935599afb670314c192ba77ec11036dcb12aa79e4'],
  ['07d763a05f35cd257501.wasm','07d763a05f35cd257501d339d9087df63c65bcaeb51a4f4f80832e333892e12e'],
  ['7bb5f8ee10fcafdab787.wasm','7bb5f8ee10fcafdab78799b1e5dd2cdc7c282ea0bf8e7939c43f3ad34b823e3d']
 ]){
  const u=new URL('static/'+name,origin),r=await fetch(u,{headers:{cookie:cookies.map(c=>c.name+'='+c.value).join('; ')}});assert.equal(r.status,200);const hash=createHash('sha256');let bytes=0;for await(const block of r.body){hash.update(block);bytes+=block.length;}const actual=hash.digest('hex');assert.equal(actual,want);assets[name]={url:u.href,sha256:actual,bytes};
 }return assets;
}
export async function discover(p,faceId,depth=5){
 const info=await cmd(p,'inspect-selected-profiles');assert.equal(info.ready,true,info.reason);assert.ok(info.sourceFaces.some(x=>x.faceId===faceId));
 const result=await cmd(p,'inspect-selected-regions',{revision:info.revision,faceId,depth});assert.equal(result.revision,info.revision);assert.equal(result.engineRevision,info.engineRevision);assert.equal(result.faceId,faceId);return{info,result};
}
export function intent(d,faceId,regionId=d.result.regions[0].regionId){return{revision:d.info.revision,faceId,regionId,unit:'millimeter',engine:'occ',engineRevision:d.info.engineRevision,depth:5,bodyPolicy:'separate'};}
export async function capture(p,faceId){return{
 bodies:(await cmd(p,'inspect-worker-solids')).bodies,
 native:await(await frame(p)).evaluate(id=>{const c=__CAD_APP;return{snapshot:JSON.stringify(c.projectManager.snapshotCurrentProject()),source:c.sketchStorageService.getSketchData(id),history:JSON.stringify(c.craftService.modifications$.value),streams:{models:c.craftService.models$.revision,history:c.craftService.modifications$.revision,expressions:[c.expressionService.script$,c.expressionService.table$,c.expressionService.errors$].map(s=>s.revision)},failure:c.craftService.pipelineFailure$.value};},faceId)
};}
export function disk(state){
 assert.equal(state.bodies.length,1);const b=state.bodies[0],m=b.metrics;
 assert.equal(b.engine,'occ');assert.equal(m.nativeValidity.valid,true);assert.equal(m.solidCount,1);assert.equal(m.resultKind,'single-solid');
 assert.ok(Math.abs(m.nativeVolume-500*Math.PI)<1e-6);
 for(const [key,expected] of[['min',[-9.9995,-10,0]],['max',[10.0005,10,5]]])for(let i=0;i<3;i++)assert.ok(Math.abs(m.nativeBounds[key][i]-expected[i])<1e-7);
 assert.equal(m.runtime.jsSha256,'cbd49d63d0900f50dda7fc53518d5f06183e85b1dea720522cc2994b0876adc9');
 assert.equal(m.runtime.wasmSha256,'a81af0b78dd585124f3f2d05d09b4a387b276bd1f655f0234002a6ab4646a637');
 return{id:b.id,featureId:b.featureId,engine:b.engine,volume:m.nativeVolume,bounds:m.nativeBounds,runtime:m.runtime};
}
