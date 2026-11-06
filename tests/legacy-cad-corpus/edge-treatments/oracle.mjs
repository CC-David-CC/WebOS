// Independent arithmetic/data checks only. No CAD imports or private writers.
import assert from 'node:assert/strict';
const sorted=v=>Array.isArray(v)?v.map(sorted):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])])):v;
export const canonical=v=>JSON.stringify(sorted(v));
export const revision='sha256:b3d91cbb02f90ba56732039283d787b92eda97c51091fafbd933ecf4db30dd97:28e8e2c2752cef100a98e24ec487f7d90021edb98fb060fdd1160fe63501bbe2';
export const near=(a,b,t=1e-7)=>assert(Number.isFinite(a)&&Math.abs(a-b)<=t,`${a} != ${b}`);
export const volume=(w,h,d,r,c)=>w*h*d-2*d*r*r*(1-Math.PI/4)-d*c*c;
export function geometry(info,w,h,d,r=0,c=0){
 assert.equal(info.bodies.length,1);assert.equal(info.outputs.length,1);const body=info.bodies[0],output=info.outputs[0];assert.equal(body.id,output.outputId);const m=body.metrics;
 assert.equal(body.engine,'occ');assert.equal(m.nativeValidity.valid,true);assert.equal(m.solidCount,1);assert.equal(m.resultKind,'single-solid');near(m.nativeVolume,volume(w,h,d,r,c),1e-6);
 for(const [key,values]of Object.entries({min:[0,0,0],max:[w,h,d]}))values.forEach((n,i)=>near(m.nativeBounds[key][i],n));
 assert.equal(m.runtime.jsSha256,revision.split(':')[1]);assert.equal(m.runtime.wasmSha256,revision.split(':')[2]);assert.equal(m.runtime.mountEngine,'occ-mechanical-profile-v1-component');
 const treated=(r?2:0)+(c?2:0);assert.equal(m.nativeTopology.counts.faces,6+treated);assert.equal(m.nativeTopology.counts.edges,12+3*treated);assert.equal(m.nativeTopology.counts.vertices,8+2*treated);
 assert.equal(canonical(body.selections),canonical(output.selections));return{bodyId:body.id,featureId:body.featureId,nativeVolume:m.nativeVolume,nativeBounds:m.nativeBounds,nativeTopology:m.nativeTopology,runtime:m.runtime};
}
export function connectors(selection,pairs){
 assert.equal(selection.status,'available');const p=selection.plan;assert.equal(p.scope,'authored-source');
 const found=p.edges.filter(e=>e.role==='connector'&&pairs.some(pair=>canonical(e.incidentCurveIds)===canonical(pair.slice().sort())));assert.equal(found.length,pairs.length);assert(found.every(e=>e.geometry==='line'));return found.map(e=>e.id);
}
export function sourceSides(inspect,faceId,width,height){
 const rows=inspect.objects.filter(o=>o.type==='Segment');assert.equal(rows.length,4);const points=new Map(inspect.points.map(p=>[p.id,p])),sides={};
 for(const row of rows){const a=points.get(row.id+':A'),b=points.get(row.id+':B');assert(a&&b);let side;
  if(Math.abs(a.y)<1e-8&&Math.abs(b.y)<1e-8)side='bottom';else if(Math.abs(a.x-width)<1e-8&&Math.abs(b.x-width)<1e-8)side='right';else if(Math.abs(a.y-height)<1e-8&&Math.abs(b.y-height)<1e-8)side='top';else if(Math.abs(a.x)<1e-8&&Math.abs(b.x)<1e-8)side='left';assert(side&&!sides[side]);sides[side]=faceId+'/'+row.id;
 }
 assert.deepEqual(Object.keys(sides).sort(),['bottom','left','right','top']);return sides;
}
export function noNativeIdentity(value){
 if(Array.isArray(value)){value.forEach(noNativeIdentity);return;}if(!value||typeof value!=='object')return;
 for(const [key,item]of Object.entries(value)){assert(!['nativeIndex','nativeSlot','nativePointer','ptr','handle','token','edgeIndex','edgeIndices'].includes(key),'Native identity leaked into authored intent: '+key);noNativeIdentity(item);}
}
export function savedIntent(native,binding,expected){
 assert.equal(native.format,'codi-jsketcher-project');assert.equal(native.version,2);assert.equal(native.unit,'millimeter');const history=native.project.model.history,profile=history.find(x=>x.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2');assert(profile);
 assert.equal(profile.params.engineRevision,revision);assert.equal(profile.params.featureId,binding.profileFeatureId);assert.equal(profile.params.faceId,binding.faceId);assert.equal(profile.params.regionId,binding.regionId);assert.equal(profile.params.depth,expected.depth);
 const treatments=history.filter(x=>x.type==='WORKER_SOLID_EDGE_TREATMENT_V1');assert.equal(treatments.length,2);for(const [i,t]of treatments.entries()){
  assert.deepEqual(Object.keys(t.params).sort(),['version','unit','engine','engineRevision','featureId','target','producerFeatureId','kind','edgeIds','size'].sort());assert.equal(t.params.version,1);assert.equal(t.params.unit,'millimeter');assert.equal(t.params.engine,'occ');assert.equal(t.params.engineRevision,revision);assert.equal(t.params.featureId,i?binding.chamferFeatureId:binding.filletFeatureId);assert.equal(t.params.producerFeatureId,i?binding.filletFeatureId:binding.profileFeatureId);assert.equal(t.params.target,i?binding.filletBodyId:binding.profileBodyId);assert.equal(t.params.kind,i?'chamfer-equal':'fillet');assert.equal(t.params.size,i?expected.chamfer:expected.fillet);assert.equal(canonical(t.params.edgeIds),canonical(i?binding.chamferEdges:binding.filletEdges));noNativeIdentity(t.params);
 }
 const source=native.project.sketches.find(s=>s.id===binding.faceId);assert(source);const segments=source.data.objects.filter(o=>o.type==='Segment');assert.equal(segments.length,4);assert.equal(source.data.stages[0].constraints.length,11);
 const corners=[[0,0],[expected.width,0],[expected.width,expected.height],[0,expected.height]],seen=new Set();for(const s of segments){assert(binding.curveIds.includes(binding.faceId+'/'+s.id));const a=s.data.a,b=s.data.b;const i=corners.findIndex(p=>Math.abs(a.x-p[0])<1e-8&&Math.abs(a.y-p[1])<1e-8);assert(i>=0);assert(!seen.has(i));seen.add(i);const q=corners[(i+1)%4];near(b.x,q[0],1e-8);near(b.y,q[1],1e-8);}return{history,source:source.data};
}
