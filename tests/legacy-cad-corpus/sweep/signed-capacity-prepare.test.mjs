// Actual retained source arithmetic and refusal controls only; no fake history,
// 32-model doubles, browser authoring, native evaluation or query replies.
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {sourceExpectation,savedCapacity} from './signed-capacity-measure.mjs';
const base=new URL('./signed-evidence-r3/',import.meta.url),receipt=JSON.parse(fs.readFileSync(new URL('receipt.json',base))),disk=receipt.saved.find(s=>s.label==='straight-disk-baseline'),native=JSON.parse(fs.readFileSync(new URL(disk.savedFile,base)));
test('actual previously saved circle/line source gives40π and five genuine analytic probes',()=>{const e=sourceExpectation(disk.input);assert(Math.abs(e.volumeMM3-40*Math.PI)<=1e-12);assert.deepEqual(e.boundsMM,{min:[-2,-2,0],max:[2,2,10]});assert.equal(e.probes.length,5);assert.deepEqual(new Set(e.probes.map(p=>p.classification)),new Set(['inside','outside','boundary']));});
test('one actual saved sweep cannot masquerade as qualified32capacity history',()=>{assert.throws(()=>savedCapacity(native,disk.binding,[{featureId:disk.binding.featureId,bodyId:disk.binding.bodyId}]));});
