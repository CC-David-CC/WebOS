// Acceptance checks only. No production geometry or feature authoring lives here.
import assert from 'node:assert/strict';
import {canonical} from '../strict-join/oracle.mjs';
import {checkBinding,observation,sameReadOnly} from '../loft/circle-signed-check.mjs';
import {checkCircleLoftMetrics} from '../loft/circle-oracle.mjs';
export {canonical,observation,sameReadOnly,checkCircleLoftMetrics};
export function nativeFromAccepted(accepted){return{project:{model:{history:accepted.native.history,counters:accepted.native.counters},sketches:accepted.native.sketches.map(row=>({id:row.id,data:JSON.parse(row.source)}))}};}
export function checkPlaneSaved(native,binding){
 const expected=checkBinding(native,binding);assert.equal(binding.planes.length,2);assert.equal(new Set(binding.planes.map(row=>row.featureId)).size,2);assert.equal(new Set(binding.planes.map(row=>row.faceId)).size,2);
 for(let i=0;i<2;i++){
  const row=binding.planes[i];assert(Number.isSafeInteger(row.index)&&row.index>=0);assert.equal(row.faceId,binding.sections[i].faceId);assert.equal(row.orientation,'XY');const op=native.project.model.history[row.index];assert.equal(op.type,'PLANE');assert.deepEqual(Object.keys(op.params).sort(),['featureId','orientation','datum','depth'].sort());assert.equal(Number(op.params.featureId),row.featureId);assert.equal(op.params.orientation,row.orientation);assert.equal(op.params.datum,null);assert.equal(op.params.depth,binding.depths[i]);assert.equal(row.depth,binding.depths[i]);assert.equal(expected.sections[i].z,op.params.depth,'Derived source witness differs from authoritative saved PLANE.depth');
 }
 return expected;
}
export function withoutFrame(text){const value=JSON.parse(text);delete value.metadata.boundaryFrame;return value;}
export function checkPlaneRows(info,binding){
 assert.equal(info.ready,true,info.reason);assert.equal(info.unit,'millimeter');assert.equal(info.depthLimit,1e8);assert.equal(info.scope,'independent-principal-plane-depth');
 for(let i=0;i<2;i++){const plane=binding.planes[i],found=info.features.filter(row=>row.index===plane.index&&row.featureId===plane.featureId&&row.faceId===plane.faceId);assert.equal(found.length,1);assert.equal(found[0].canEdit,true,found[0].reason);assert.equal(found[0].orientation,plane.orientation);assert.equal(found[0].depth,binding.depths[i]);}
}
export async function snapshot(h,binding){
 return{accepted:await h.capture(binding.sections[0].faceId),custody:await h.frame.evaluate(()=>{const c=globalThis.__CAD_APP,p=c.projectService,s=c.storageService;return{documentGeneration:p.documentGeneration,evaluationEpoch:c.craftService.evaluationEpoch,unit:c.projectManager.unit,manufacturing:structuredClone(c.projectManager.getManufacturingMetadata()),sourceVersions:c.sketchStorageService.getAllSketches().map(row=>({id:row.id,key:p.sketchStorageKey(row.id),version:s.versionOf(p.sketchStorageKey(row.id))})).sort((a,b)=>a.id.localeCompare(b.id))};}),ownership:await h.ownership()};
}
function settled(state){assert.equal(state.ownership.processing,false);assert.equal(state.ownership.resources.cleanupFailed,false);assert.equal(state.ownership.resources.candidates,0);}
export function preservedAccepted(before,after){
 settled(before);settled(after);const normalize=value=>{const copy=structuredClone(value);delete copy.accepted.solids.revision;delete copy.accepted.journal.revision;delete copy.custody.evaluationEpoch;return copy};assert.equal(canonical(normalize(after)),canonical(normalize(before)),'Rejected candidate changed accepted source/history/counters/journal/body/source versions or resource ownership.');
}
export function depthTransition(before,after,binding,sourceIndex){
 settled(before);settled(after);const row=binding.planes[sourceIndex],a=before.accepted.native,b=after.accepted.native,history=structuredClone(a.history);history[row.index].params.depth=binding.depths[sourceIndex];assert.equal(canonical(b.history),canonical(history),'Plane edit changed additional authored history');assert.equal(canonical(a.counters),canonical(b.counters));assert.equal(canonical(before.ownership.counters),canonical(after.ownership.counters));for(const key of ['expressions','presentation'])assert.equal(canonical(a[key]),canonical(b[key]));assert.equal(a.sketches.length,b.sketches.length);
 for(const prior of a.sketches){const found=b.sketches.filter(next=>next.id===prior.id);assert.equal(found.length,1);if(prior.id!==row.faceId)assert.equal(found[0].source,prior.source,'Unrelated source bytes changed');else{assert.equal(canonical(withoutFrame(found[0].source)),canonical(withoutFrame(prior.source)),'Plane edit changed local source geometry/IDs/constraints or other metadata');const frame=JSON.parse(found[0].source).metadata.boundaryFrame,oldFrame=JSON.parse(prior.source).metadata.boundaryFrame;assert.deepEqual(frame.origin,[0,0,binding.depths[sourceIndex]]);for(const basis of ['x','y','z'])assert.deepEqual(frame[basis],oldFrame[basis]);}}
 checkCircleLoftMetrics(observation(after,binding).metrics,checkPlaneSaved(nativeFromAccepted(after.accepted),binding));assert.equal(after.accepted.solids.bodies[0].id,before.accepted.solids.bodies[0].id);assert.equal(after.accepted.solids.bodies[0].featureId,before.accepted.solids.bodies[0].featureId);assert.equal(canonical(after.accepted.solids.bodies[0].metrics.runtime),canonical(before.accepted.solids.bodies[0].metrics.runtime));
}
export function checkDisplay(display,expected){
 assert.equal(display.quality,'detached-float32-display-copy');assert(Number.isSafeInteger(display.triangleCount)&&display.triangleCount>0&&display.triangleCount<=100000);assert.equal(display.positions.length,display.triangleCount*9);const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];for(let i=0;i<display.positions.length;i++){const value=display.positions[i],axis=i%3;assert(Number.isFinite(value));min[axis]=Math.min(min[axis],value);max[axis]=Math.max(max[axis],value);assert(value>=expected.boundsMM.min[axis]-1e-4&&value<=expected.boundsMM.max[axis]+1e-4,'Display vertex outside independent native fixture envelope');}
 for(let axis=0;axis<3;axis++){const tolerance=axis===2?1e-4:0.05;assert(Math.abs(min[axis]-expected.boundsMM.min[axis])<=tolerance);assert(Math.abs(max[axis]-expected.boundsMM.max[axis])<=tolerance);}return{min,max,quality:display.quality,triangles:display.triangleCount};
}
