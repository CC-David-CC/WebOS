// Independent arithmetic/data oracles; no CAD product imports or writers.
import assert from 'node:assert/strict';
export {canonical,connectors,sourceSides,noNativeIdentity} from '../edge-treatments/oracle.mjs';
import {canonical,noNativeIdentity} from '../edge-treatments/oracle.mjs';
export const revision='sha256:dd666902fe926d69cc3c8843f5568c2a3e569f38ff49291baa2f248165b5ea99:8d5e537e0d7f9e12b8ae0eaf239c0be1080934ed12a24bf6e7f849c9135ed5a2';
export const near=(a,b,t=1e-6)=>assert(Number.isFinite(a)&&Math.abs(a-b)<=t,`${a} != ${b}`);
export const centers=[[50,25],[8,8],[92,8],[92,42],[8,42]],radii=[5,2,2,2,2];
export const volume=(holes,fillet=0,chamfer=0)=>100000-radii.slice(0,holes).reduce((s,r)=>s+r*r,0)*Math.PI*20-2*20*fillet*fillet*(1-Math.PI/4)-20*chamfer*chamfer;
export function geometry(info,{holes=0,fillet=0,chamfer=0,binding}){
 assert.equal(info.bodies.length,1);assert.equal(info.outputs.length,1);const body=info.bodies[0],out=info.outputs[0],m=body.metrics;assert.equal(body.id,out.outputId);assert.equal(body.engine,'occ');assert.equal(m.resultKind,'single-solid');assert.equal(m.solidCount,1);assert(m.nativeValidity.valid);near(m.nativeVolume,volume(holes,fillet,chamfer));
 for(const [k,vs]of Object.entries({min:[0,0,0],max:[100,50,20]}))vs.forEach((v,i)=>near(m.nativeBounds[k][i],v));
 assert.equal(m.runtime.jsSha256,revision.split(':')[1]);assert.equal(m.runtime.wasmSha256,revision.split(':')[2]);assert.equal(m.runtime.mountEngine,'occ-boolean-history-v1-component');
 const treated=(fillet?2:0)+(chamfer?2:0);assert.equal(m.nativeTopology.counts.faces,6+holes+treated);assert.equal(m.nativeTopology.counts.edges,12+3*holes+3*treated);assert.equal(m.nativeTopology.counts.vertices,8+2*holes+2*treated);
 assert.equal(canonical(body.selections),canonical(out.selections));const s=body.selections;assert.equal(s.status,'available');assert.equal(s.plan.version,2);assert.equal(s.plan.featureId,body.featureId);assert.equal(s.plan.scope,'authored-source');assert(!Object.hasOwn(s.plan,'regionId'));
 const contexts=[{kind:'sketch-profile',featureId:binding.base.featureId,regionId:binding.base.regionId},...binding.tools.slice(0,holes).map(t=>({kind:'sketch-profile',featureId:t.featureId,regionId:t.regionId}))].sort((a,b)=>a.featureId-b.featureId);assert.equal(canonical(s.plan.sourceContexts),canonical(contexts));
 for(const e of [...s.plan.edges,...s.plan.faces])assert(contexts.some(c=>c.featureId===e.originFeatureId));
 return{bodyId:body.id,featureId:body.featureId,nativeVolume:m.nativeVolume,nativeBounds:m.nativeBounds,nativeTopology:m.nativeTopology,selections:s,runtime:m.runtime};
}
export function savedIntent(native,binding,{fillet=3,chamfer=1}={}){
 assert.equal(native.format,'codi-jsketcher-project');assert.equal(native.version,2);assert.equal(native.unit,'millimeter');const history=native.project.model.history;
 const profiles=history.filter(x=>x.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2');assert.equal(profiles.length,6);
 for(const p of [binding.base,...binding.tools]){const found=profiles.find(x=>x.params.featureId===p.featureId);assert(found);assert.equal(found.params.faceId,p.faceId);assert.equal(found.params.regionId,p.regionId);assert.equal(found.params.depth,p===binding.base?20:22);assert.equal(found.params.engineRevision,revision);assert.equal(found.params.bodyPolicy,'separate');noNativeIdentity(found.params);}
 const booleans=history.filter(x=>x.type==='WORKER_SOLID_BOOLEAN_V1');assert.equal(booleans.length,5);let previous=binding.base;
 for(const [i,b]of booleans.entries()){const tool=binding.tools[i];assert.deepEqual(Object.keys(b.params).sort(),['version','unit','engine','engineRevision','featureId','kind','a','b'].sort());assert.equal(b.params.version,1);assert.equal(b.params.unit,'millimeter');assert.equal(b.params.engine,'occ');assert.equal(b.params.engineRevision,revision);assert.equal(b.params.kind,'subtract');assert.equal(b.params.a,previous.outputId);assert.equal(b.params.b,tool.outputId);assert.equal(b.params.featureId,binding.cuts[i].featureId);noNativeIdentity(b.params);previous=binding.cuts[i];}
 const treatments=history.filter(x=>x.type==='WORKER_SOLID_EDGE_TREATMENT_V1');assert.equal(treatments.length,2);
 for(const [i,t]of treatments.entries()){const expected=i?binding.chamfer:binding.fillet,producer=i?binding.fillet:binding.cuts.at(-1);assert.deepEqual(Object.keys(t.params).sort(),['version','unit','engine','engineRevision','featureId','target','producerFeatureId','kind','edgeIds','size'].sort());assert.equal(t.params.version,1);assert.equal(t.params.unit,'millimeter');assert.equal(t.params.engine,'occ');assert.equal(t.params.engineRevision,revision);assert.equal(t.params.featureId,expected.featureId);assert.equal(t.params.producerFeatureId,producer.featureId);assert.equal(t.params.target,producer.outputId);assert.equal(t.params.kind,i?'chamfer-equal':'fillet');assert.equal(t.params.size,i?chamfer:fillet);assert.equal(canonical(t.params.edgeIds),canonical(expected.edgeIds));noNativeIdentity(t.params);}
 const sketches=native.project.sketches;assert.equal(sketches.length,6);
 const rectangle=sketches.find(s=>s.id===binding.base.faceId);assert(rectangle);assert.equal(rectangle.data.objects.length,4);assert(rectangle.data.objects.every(x=>x.type==='Segment'));assert.equal(rectangle.data.stages[0].constraints.length,11);
 const corners=[[0,0],[100,0],[100,50],[0,50]],seen=new Set();for(const s of rectangle.data.objects){assert(binding.base.curveIds.includes(binding.base.faceId+'/'+s.id));const a=s.data.a,b=s.data.b,i=corners.findIndex(p=>Math.abs(a.x-p[0])<1e-8&&Math.abs(a.y-p[1])<1e-8);assert(i>=0&&!seen.has(i));seen.add(i);near(b.x,corners[(i+1)%4][0]);near(b.y,corners[(i+1)%4][1]);}
 for(const [i,tool]of binding.tools.entries()){const sketch=sketches.find(s=>s.id===tool.faceId);assert(sketch);assert.equal(sketch.data.objects.length,1);const circle=sketch.data.objects[0];assert.equal(circle.type,'Circle');assert.equal(circle.id,tool.circleId);near(circle.data.c.x,centers[i][0]);near(circle.data.c.y,centers[i][1]);near(circle.data.r,radii[i]);assert.equal(sketch.data.stages[0].constraints.length,0);}
 return{profiles:profiles.length,booleans:booleans.length,treatments:treatments.length,sourceSketches:sketches.length};
}
