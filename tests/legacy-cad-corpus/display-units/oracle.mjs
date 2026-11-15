// Detached numerical/structural observations only. No CAD imports or writers.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const canonical=value=>{if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';return JSON.stringify(value);};
export const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const near=(a,b,t)=>assert(Number.isFinite(a)&&Math.abs(a-b)<=t,`${a} != ${b} +/- ${t}`);
export function geometry(solids,depth){
 assert.equal(solids.bodies.length,1);assert.equal(solids.outputs.length,1);const b=solids.bodies[0],o=solids.outputs[0],m=b.metrics;
 assert.equal(b.id,o.outputId);assert.equal(b.featureId,o.featureId);assert.equal(b.engine,'occ');assert.equal(m.nativeValidity.valid,true);assert.equal(m.solidCount,1);assert.equal(m.resultKind,'single-solid');
 near(m.nativeVolume,25.4*50.8*depth,1e-6);for(const [k,a]of Object.entries({min:[0,0,0],max:[25.4,50.8,depth]}))a.forEach((v,i)=>near(m.nativeBounds[k][i],v,1e-7));
 assert.equal(m.nativeTopology.counts.faces,6);assert.equal(m.nativeTopology.counts.edges,12);assert.equal(m.nativeTopology.counts.vertices,8);assert.equal(canonical(b.selections),canonical(o.selections));
 return{bodyId:b.id,featureId:b.featureId,nativeVolume:m.nativeVolume,nativeBounds:m.nativeBounds,nativeTopology:m.nativeTopology,selections:b.selections,runtime:m.runtime};
}
export function modelState(state,{acrossOpen=false}={}){
 const s=structuredClone(state);delete s.units;delete s.document;delete s.native.presentation;delete s.native.worker;delete s.solids.revision;delete s.journal.revision;
 if(acrossOpen){delete s.native.materialRevision;delete s.journal;delete s.mesh;}
 return s;
}
export function sameModel(before,after,options){assert.equal(canonical(modelState(after,options)),canonical(modelState(before,options)),'Presentation changed canonical source/history/IDs/counters/journal/native result/mesh');}
export function noWorkerDispatch(before,after){assert.equal(canonical(after.native.worker),canonical(before.native.worker),'Presentation dispatched or allocated a Worker');}
export function savedModel(native,binding,depth,unit){
 assert.equal(native.format,'codi-jsketcher-project');assert.equal(native.version,2);assert.equal(native.unit,'millimeter');
 if(unit==='inch')assert.deepEqual(native.presentation,{version:1,lengthUnit:'inch'});else assert(!Object.hasOwn(native,'presentation'));
 const history=native.project.model.history,profile=history.filter(o=>o.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2');assert.equal(profile.length,1);assert.equal(profile[0].params.featureId,binding.profile.featureId);assert.equal(profile[0].params.faceId,binding.faceId);assert.equal(profile[0].params.regionId,binding.regionId);assert.equal(profile[0].params.depth,depth);assert.equal(profile[0].params.unit,'millimeter');
 const sketches=native.project.sketches;assert.equal(sketches.length,1);assert.equal(sketches[0].id,binding.faceId);assert.equal(sketches[0].data.objects.length,4);assert(sketches[0].data.objects.every(o=>o.type==='Segment'));
 const corners=[[0,0],[25.4,0],[25.4,50.8],[0,50.8]],seen=new Set();for(const o of sketches[0].data.objects){const {a,b}=o.data,i=corners.findIndex(p=>Math.abs(p[0]-a.x)<1e-8&&Math.abs(p[1]-a.y)<1e-8);assert(i>=0&&!seen.has(i));seen.add(i);near(b.x,corners[(i+1)%4][0],1e-8);near(b.y,corners[(i+1)%4][1],1e-8);}
 return{sourceSketches:1,profileFeatures:1,canonicalWidth:25.4,canonicalHeight:50.8,canonicalDepth:depth,presentation:unit};
}
