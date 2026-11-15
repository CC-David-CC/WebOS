// Independent replay of own normally saved native files and actual receipt.
import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
import {savedIntent,volume,near,canonical} from './oracle.mjs';
const dir=process.argv[2],r=JSON.parse(fs.readFileSync(path.join(dir,'receipt.json'))),sha=b=>crypto.createHash('sha256').update(b).digest('hex');assert.equal(r.status,'PASS');
const binding=r.rows.find(x=>x.binding)?.binding;assert(binding);const result={status:'PASS',scope:'Own public-command native Save exports plus independently calculated expected volumes; no imported authoring seed',files:[]};
for(const [label,chamfer,measurement]of [['edge-chain',1,r.rows.find(x=>x.resized)?.resized],['edge-chain-reedited',1.5,r.rows.find(x=>x.reedited)?.reedited]]){
 const raw=fs.readFileSync(path.join(dir,label+'.jsketcher.json')),native=JSON.parse(raw),proof=savedIntent(native,binding,{width:150,height:30,depth:25,fillet:4,chamfer});assert.equal(proof.history.length,4);assert.equal(native.project.sketches.length,1);
 const record=r.rows.find(x=>x.label===label+' normal native Save and server sync');assert(record);assert.equal(sha(raw),record.sha256);assert.equal(raw.length,record.bytes);
 for(const t of proof.history.filter(x=>x.type==='WORKER_SOLID_EDGE_TREATMENT_V1')){assert.equal(t.params.edgeIds.length,2);for(const id of t.params.edgeIds){assert(id.startsWith('worker-prism-selection:1:'));const d=JSON.parse(id.slice('worker-prism-selection:1:'.length));assert.equal(d[0],binding.profileFeatureId);assert.equal(d[1],binding.regionId);assert.equal(d[2],'edge');assert.equal(d[3],'connector');assert.equal(d[4].length,2);assert(d[4][0]<d[4][1]);assert(d[4].every(c=>binding.curveIds.includes(c)));}}
 const nativeExpected=volume(150,30,25,4,chamfer);near(measurement.nativeVolume,nativeExpected,1e-6);result.files.push({name:label+'.jsketcher.json',sha256:sha(raw),bytes:raw.length,sourceSegments:4,sourceConstraints:11,historyOperations:4,fillet:4,chamfer,depth:25,expectedVolume:nativeExpected,actualReplayedNativeVolume:measurement.nativeVolume,symbolicEdgeBindingsPreserved:true});
}
assert.equal(canonical(r.rows.find(x=>x.binding).binding),canonical(binding));fs.writeFileSync(path.join(dir,'saved-oracle.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
