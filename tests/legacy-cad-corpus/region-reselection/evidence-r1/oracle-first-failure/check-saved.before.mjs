// Separate raw saved-file checker. Does not parse opaque region identities.
import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';
const root=path.resolve(process.argv[2]),r=JSON.parse(fs.readFileSync(path.join(root,'receipt.json'))),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),near=(a,b)=>assert(Number.isFinite(a)&&Math.abs(a-b)<1e-6),results=[];
for(const [label,caseName,objects,volume,min,max]of[
 ['disjoint','disjoint-and-mixed-history',8,2700,[40,0,0],[70,10,9]],
 ['nested','nested-circle-regions',3,625*Math.PI,[-15,-15,0],[15,15,5]],
 ['compatible-child','compatible-world-space-boolean-child',8,750,[40,5,0],[70,10,5]],
 ['incompatible-child','incompatible-source-bound-edge-child',8,1000-5*(1-Math.PI/4),[0,0,0],[20,10,5]]
]){
 const row=r.rows.find(x=>x.case===caseName&&x.label==='Saved native intent and fresh signed Open');assert(row,label+' fresh Open evidence absent');const bytes=fs.readFileSync(path.join(root,label+'.jsketcher.json')),n=JSON.parse(bytes),p=n.project,binding=r.cases.find(c=>c.name===caseName).binding;assert.equal(sha(bytes),row.sha256);assert.equal(n.format,'codi-jsketcher-project');assert.equal(n.version,2);assert.equal(n.unit,'millimeter');assert.equal(p.sketches.length,1);assert.equal(p.sketches[0].id,binding.faceId);assert.equal(p.sketches[0].data.objects.length,objects);
 const history=p.model.history,profiles=history.filter(x=>x.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2');assert.equal(profiles.length,1);const intent=profiles[0].params;assert.equal(intent.featureId,binding.featureId);assert.equal(intent.faceId,binding.faceId);assert.equal(intent.regionId,row.intent.regionId);assert.equal(intent.engineRevision,binding.engineRevision);assert.equal(intent.depth,max[2]);assert.equal(intent.bodyPolicy,'separate');assert.equal(p.model.counters.featureId,binding.counter);assert.equal(p.model.expressions,'');
 if(label==='nested'){const circles=p.sketches[0].data.objects;assert(circles.every(o=>o.type==='Circle'&&o.data.c.x===0&&o.data.c.y===0));assert.deepEqual(circles.map(o=>o.data.r).sort((a,b)=>a-b),[5,10,15]);}
 else{const byId=new Map(p.sketches[0].data.objects.map(o=>[o.id,o]));for(const[idset,lo,hi]of[[binding.a,0,20],[binding.b,40,70]]){assert.equal(idset.length,4);for(const id of idset){const o=byId.get(id);assert.equal(o.type,'Segment');for(const v of[o.data.a,o.data.b])assert([lo,hi].includes(v.x)&&[0,10].includes(v.y));}}}
 const m=row.after.measurement;near(m.nativeVolume,volume);for(let i=0;i<3;i++){near(m.nativeBounds.min[i],min[i]);near(m.nativeBounds.max[i],max[i]);}
 if(label==='compatible-child'){const cut=history.find(x=>x.type==='WORKER_SOLID_BOOLEAN_V1');assert.equal(cut.params.kind,'subtract');assert.equal(cut.params.a,binding.outputId);assert.equal(cut.params.engineRevision,binding.engineRevision);}
 if(label==='incompatible-child'){const edge=history.find(x=>x.type==='WORKER_SOLID_EDGE_TREATMENT_V1');assert.equal(edge.params.kind,'fillet');assert.equal(edge.params.size,1);assert.equal(edge.params.target,binding.outputId);assert.equal(edge.params.edgeIds.length,1);}
 results.push({label,sha256:sha(bytes),historyLength:history.length,featureId:intent.featureId,volume,min,max});
}
console.log(JSON.stringify({status:'PASS',scope:'Actual saved intent and independent analytic formula/readback checks; no public-ID parsing or model writes',results},null,2));
