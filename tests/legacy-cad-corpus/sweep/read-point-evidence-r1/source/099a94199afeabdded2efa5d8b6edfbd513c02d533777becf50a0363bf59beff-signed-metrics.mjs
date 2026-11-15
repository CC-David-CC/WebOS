// Signed metric-only adapter. Frozen full native-point oracle stays untouched.
import assert from 'node:assert/strict';
import {deriveSweepExpectation,checkSavedSweepIntent,SWEEP_TOLERANCE} from './oracle.mjs';
import {canonical} from '../strict-join/oracle.mjs';
export const AUTHORED=['version','unit','engine','engineRevision','featureId','faceId','regionId','pathFaceId','pathCurves','transport','bodyPolicy'];
export function fromSaved({native,authored,discovery,profileInspection,pathInspection}){
 assert.equal(native.format,'codi-jsketcher-project');assert.equal(native.version,2);assert.equal(native.unit,'millimeter');
 const history=native.project.model.history,sweeps=history.filter(x=>x.type==='WORKER_SELECTED_PROFILE_SWEEP_V1');assert.equal(sweeps.length,1);assert.equal(history.length,3);assert.equal(history.filter(x=>x.type==='PLANE').length,2);checkSavedSweepIntent(sweeps[0].params,authored);
 const sketches=native.project.sketches;assert.equal(sketches.length,2);const profile=sketches.filter(x=>x.id===authored.faceId),path=sketches.filter(x=>x.id===authored.pathFaceId);assert.equal(profile.length,1);assert.equal(path.length,1);assert.notEqual(profile[0].id,path[0].id);
 assert.equal(discovery.faceId,authored.faceId);assert.equal(discovery.pathFaceId,authored.pathFaceId);const regions=discovery.regions.filter(x=>x.regionId===authored.regionId);assert.equal(regions.length,1);assert.equal(regions[0].support,'supported');
 for(const[data,inspection]of[[profile[0].data,profileInspection],[path[0].data,pathInspection]])assert.equal(canonical(data.metadata.boundaryFrame),canonical(inspection.boundaryFrame),'Saved and public source frames differ.');
 const input={unit:'millimeter',featureId:authored.featureId,engineRevision:authored.engineRevision,transport:authored.transport,profile:{faceId:authored.faceId,digest:discovery.sourceDigest,frame:profileInspection.boundaryFrame,sketch:profile[0].data,region:{regionId:authored.regionId,...regions[0].descriptor}},path:{faceId:authored.pathFaceId,digest:discovery.pathDigest,frame:pathInspection.boundaryFrame,sketch:path[0].data,refs:authored.pathCurves}};
 return{input,expected:deriveSweepExpectation(input)};
}
export function checkMetrics(observation,expected){
 assert.equal(observation.unit,'millimeter');assert.equal(observation.featureId,expected.featureId);assert.equal(observation.engineRevision,expected.engineRevision);assert(typeof observation.bodyId==='string'&&observation.bodyId);
 const m=observation.metrics;assert.equal('sha256:'+m.runtime.jsSha256+':'+m.runtime.wasmSha256,expected.engineRevision);assert.equal(m.nativeValidity.valid,true);assert.equal(m.solidCount,1);assert.equal(m.resultKind,'single-solid');assert(Number.isFinite(m.nativeVolume)&&m.nativeVolume>0);assert(Math.abs(m.nativeVolume-expected.volumeMM3)<=SWEEP_TOLERANCE.volumeMM3,'Native volume differs from independent saved source.');
 for(const k of['min','max']){assert(Array.isArray(m.nativeBounds[k])&&m.nativeBounds[k].length===3);m.nativeBounds[k].forEach((n,i)=>assert(Number.isFinite(n)&&Math.abs(n-expected.boundsMM[k][i])<=SWEEP_TOLERANCE.boundsMM,'Native bounds differ from independent saved source.'));}
 for(let i=0;i<3;i++)assert(m.nativeBounds.min[i]<=m.nativeBounds.max[i]);
 return{scope:'signed saved-source native volume/bounds only',volumeMM3:m.nativeVolume,boundsMM:m.nativeBounds,nativePointClassification:{status:'unavailable',reason:'NO_PUBLIC_NATIVE_POINT_QUERY'},fullNativePointOracleInvoked:false};
}
export function observation(info,binding){assert.equal(info.ready,true,info.reason);assert.equal(info.bodies.length,1);assert.equal(info.outputs.length,1);const b=info.bodies[0],o=info.outputs[0];assert.equal(b.featureId,binding.featureId);assert.equal(b.id,binding.bodyId);assert.equal(o.featureId,b.featureId);assert.equal(o.outputId,b.id);assert.equal(b.engine,'occ');assert.equal(b.selections.status,'unavailable');return{unit:'millimeter',revision:info.revision,featureId:b.featureId,bodyId:b.id,engineRevision:binding.engineRevision,metrics:b.metrics};}
