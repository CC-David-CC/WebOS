// Recorded genuine historical saved-source/point observations exercise these
// acceptance checks. This is not a new native execution or depth-edit success.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {checkPlaneSaved,withoutFrame,preservedAccepted} from './checks.mjs';
import {checkCircleLoftMetrics} from '../loft/circle-oracle.mjs';
import {sha} from '../loft/circle-signed-check.mjs';
const dir=new URL('../loft/circle-signed-evidence-r3/',import.meta.url),receipt=JSON.parse(fs.readFileSync(new URL('receipt.json',dir))),saved=receipt.saved.find(row=>row.label==='phase0-baseline'),bytes=fs.readFileSync(new URL(saved.savedFile,dir)),native=JSON.parse(bytes);assert.equal(sha(bytes),saved.sha256);
function binding(){const value=structuredClone(saved.binding);value.planes=value.sections.map((section,i)=>{const rows=receipt.rows.filter(row=>row.case==='phase0'&&row.plane?.faceId===section.faceId);assert.equal(rows.length,1);const created=rows[0].plane,index=native.project.model.history.findIndex(row=>row.type==='PLANE'&&Number(row.params.featureId)===created.featureId);assert(index>=0);return{index,featureId:created.featureId,faceId:created.faceId,orientation:'XY',depth:value.depths[i]}});return value;}
test('actual retained public creation IDs and saved PLANE params corroborate historical circle analytic truth',()=>{const expected=checkPlaneSaved(native,binding());assert(Math.abs(expected.volumeMM3-280*Math.PI)<1e-10);assert.deepEqual(expected.boundsMM,{min:[-4,-4,0],max:[4,4,30]});checkCircleLoftMetrics(saved.before.metrics,expected);});
test('wrong plane feature/index/face/depth and source witness cannot masquerade as a saved placement edit',()=>{
 for(const mutate of [b=>b.planes[1].featureId+=100,b=>b.planes[1].index=0,b=>b.planes[1].faceId=b.planes[0].faceId,b=>b.planes[1].depth=40]){const b=binding();mutate(b);assert.throws(()=>checkPlaneSaved(native,b));}
 for(const change of ['params-only','frame-only','both-wrong-identity']){const n=structuredClone(native),b=binding();if(change==='params-only')n.project.model.history[1].params.depth=40;if(change==='frame-only')n.project.sketches.find(row=>row.id===b.sections[1].faceId).data.metadata.boundaryFrame.origin[2]=40;if(change==='both-wrong-identity'){b.depths[1]=40;b.planes[1].depth=40;n.project.model.history[1].params.depth=40;n.project.model.history[1].params.featureId='777';n.project.sketches.find(row=>row.id===b.sections[1].faceId).data.metadata.boundaryFrame.origin[2]=40;}assert.throws(()=>checkPlaneSaved(n,b));}
});
test('metadata-only comparison retains actual local source IDs/coordinates/constraints and other metadata',()=>{
 const source=JSON.stringify(native.project.sketches[1].data),copy=JSON.parse(source);copy.metadata.boundaryFrame.origin[2]=40;assert.deepEqual(withoutFrame(JSON.stringify(copy)),withoutFrame(source));copy.objects[0].data.r+=1;assert.notDeepEqual(withoutFrame(JSON.stringify(copy)),withoutFrame(source));
});
test('recorded real query preservation passes and changed accepted source/counters/journal/resources refuses',()=>{
 const actual=receipt.pointQueries.find(row=>row.label==='phase0-baseline-before-open');assert(actual);preservedAccepted(actual.before,actual.after);for(const mutate of [s=>s.accepted.native.counters.featureId++,s=>s.accepted.native.sketches[0].source+=' ',s=>s.accepted.journal.canUndo=!s.accepted.journal.canUndo,s=>s.ownership.resources.candidates=1]){const changed=structuredClone(actual.after);mutate(changed);assert.throws(()=>preservedAccepted(actual.before,changed));}
});
