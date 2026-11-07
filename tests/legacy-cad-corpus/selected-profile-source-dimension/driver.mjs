// Complete signed workflow source; execute only on the parent's composed pins.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {harness} from '../sweep/signed-harness.mjs';
const need=k=>{assert(process.env[k],k+' required');return process.env[k];};
const pins=JSON.parse(fs.readFileSync(need('CODI_SIGNED_PINS'))),build=need('CODI_SOURCE_REGION_ENGINE_REVISION'),out=path.resolve(need('CODI_EVIDENCE'));
assert.equal(pins.source,need('CODI_EXPECT_SOURCE'));assert.equal(pins.desktop,need('CODI_EXPECT_DESKTOP'));assert.match(build,/^sha256:[a-f0-9]{64}:[a-f0-9]{64}$/);
for(const k of ['CODI_TEST_URL','CODI_TEST_CDP'])assert(['127.0.0.1','localhost'].includes(new URL(need(k)).hostname));
assert(!fs.existsSync(out),'Fresh evidence directory required');fs.mkdirSync(out,{recursive:true});
const canonical=v=>JSON.stringify(function order(x){return Array.isArray(x)?x.map(order):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,order(x[k])])):x;}(v));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const files=['test/agent-cad-corpus/selected-profile-source-dimension/driver.mjs','test/agent-cad-corpus/selected-profile-source-dimension/README.md','test/agent-cad-corpus/sweep/signed-harness.mjs','test/agent-cad-corpus/strict-join/oracle.mjs','apps/system/jsketcher/selected-profile-source-dimension-commands.mjs'].map(f=>path.join(root,f));
const hashes=()=>Object.fromEntries(files.map(f=>[path.relative(root,f),sha(fs.readFileSync(f))]));
const receipt={status:'RUNNING',scope:'Atomic literal source-dimension and explicit region repair; compatible Boolean and incompatible unchanged source consumer; shared UndoRedo; native Save/Open/reedit. Bounded E04/E05.',pins,engineRevision:build,sourceHashes:hashes(),tolerances:{volumeAbsMm3:1e-6,boundsAbsMm:1e-6},sourceSeeds:false,rows:[],saved:[]};
const flush=()=>fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
const record=(label,data={})=>{receipt.rows.push(structuredClone({label,...data}));flush();console.log(label);};
const one=(rows,label)=>{assert.equal(rows.length,1,'One '+label+' required');return rows[0];};
const near=(a,b)=>assert(Number.isFinite(a)&&Math.abs(a-b)<=1e-6,`${a} differs from ${b}`),ids=values=>values.slice().sort();
const browser=await createRequire(import.meta.url)(need('PUPPETEER_CORE_PATH')).connect({browserURL:need('CODI_TEST_CDP'),protocolTimeout:300000});
let h,binding;
async function runtime(){const assets=await h.pinFiles(Object.keys(pins.files));for(const row of assets)assert.equal(row.sha256,pins.files[row.name],row.name);const outer=await h.pinOuter({bundle:pins.outer.bundleSHA256});assert.equal(outer.sha256,pins.outer.sha256);record('Exact served inner outer and native pins',{assets,outer});}
async function state(){return{capture:await h.capture(binding.faceId),host:await h.command('inspect'),ownership:await h.ownership()};}
function accepted(s){const r=structuredClone(s);delete r.capture.solids.revision;delete r.capture.journal.revision;delete r.host.revision;return r;}
const tokens=s=>({solids:s.capture.solids.revision,journal:s.capture.journal.revision,host:s.host.revision});
async function refusal(label,command,args,code,{replayed=false}={}){
 const before=await state();let failure;try{await h.command(command,args);}catch(e){failure={name:e.name,code:e.code,message:e.message,committed:e.committed===true,possiblyCommitted:e.possiblyCommitted===true};}
 record(label+' raw outcome',{failure:failure??null,expectedCode:code,before});assert(failure,'Required refusal succeeded');assert.equal(failure.code,code);assert.equal(failure.name,'Error');assert.equal(failure.committed,false);assert.equal(failure.possiblyCommitted,false);
 const after=await state();assert.equal(canonical(replayed?accepted(after):after),canonical(replayed?accepted(before):before),'Refusal changed accepted source/history/model/counters/journal/material/document/baseline');
 record(label+' preservation',{before,after,inspectionTokenComparison:{before:tokens(before),after:tokens(after),policy:replayed?'Only three opaque inspection revisions may advance on evaluated refusal; every accepted field stays exact':'Every same-window field and revision stays exact'}});
}
function descriptor(row,outer,holes){return canonical(ids(row.descriptor.outerCurveIds))===canonical(ids(outer))&&canonical(row.descriptor.holeCurveIds.map(ids).sort((a,b)=>canonical(a).localeCompare(canonical(b))))===canonical(holes.map(ids).sort((a,b)=>canonical(a).localeCompare(canonical(b))));}
const sourceInfo=()=>h.inspect(binding.faceId);
const widthTarget=info=>one(info.dimensionTargets.filter(t=>t.typeId==='SegmentLength'&&t.canEdit&&t.unit==='millimeter'&&t.objects.length===1&&t.objects[0]===binding.bottomId),'actual width dimension');
async function ordinaryWidth(width){const info=await sourceInfo();return h.command('edit-closed-sketch-dimension',{revision:info.revision,faceId:binding.faceId,constraintId:widthTarget(info).constraintId,value:width});}
async function request(width){const history=await h.command('inspect-selected-profile-history'),sources=await h.command('inspect-closed-sketches'),info=await sourceInfo(),f=one(history.features.filter(f=>f.featureId===binding.profile.featureId),'same extrusion');return{revision:history.revision,sourceRevision:sources.revision,index:f.index,featureId:f.featureId,constraintId:widthTarget(info).constraintId,value:width};}
async function proposal(width){const args=await request(width),before=await state(),p=await h.command('inspect-selected-profile-source-dimension-regions',args);assert.equal(canonical(await state()),canonical(before),'Read-only proposal changed accepted state');assert.equal(p.revision,args.revision);assert.equal(p.sourceRevision,args.sourceRevision);assert.equal(p.featureId,args.featureId);assert.equal(p.proposalCustody,'recomputed-from-current-source');assert.match(p.candidateSourceDigest,/^[a-f0-9]{64}$/);return{args,p};}
const commitArgs=p=>({...p.args,regionId:one(p.p.regions.filter(r=>r.support==='supported'&&descriptor(r,binding.outerIds,[binding.innerIds])),'explicit proposed outer-with-hole region').regionId,candidateSourceDigest:p.p.candidateSourceDigest});
async function depth(value){const history=await h.command('inspect-selected-profile-history'),f=one(history.features.filter(f=>f.featureId===binding.profile.featureId),'same extrusion');return h.command('edit-selected-profile-depth',{revision:history.revision,index:f.index,featureId:f.featureId,depth:value});}
function source(capture,width){
 const native=JSON.parse(capture.native.source);assert.equal(native.objects.length,8);assert.deepEqual(native.objects.map(o=>o.id).sort(),ids([...binding.outerIds,...binding.innerIds]));
 const outer=native.objects.filter(o=>binding.outerIds.includes(o.id)),positions=outer.flatMap(o=>[o.data.a,o.data.b]),corners=[[0,0],[width,0],[width,50],[0,50]],counts=new Map();
 for(const p of positions){const c=one(corners.filter(([x,y])=>Math.abs(x-p.x)<=1e-6&&Math.abs(y-p.y)<=1e-6),'analytic outer corner'),key=canonical(c);counts.set(key,(counts.get(key)||0)+1);}assert.equal(counts.size,4);assert([...counts.values()].every(n=>n===2));
 for(const original of binding.innerObjects)assert.deepEqual(one(native.objects.filter(o=>o.id===original.id),'unrelated inner Segment'),original,'Unrelated loop geometry or intent changed');
 assert.deepEqual(native.metadata.boundaryFrame,binding.frame);return native;
}
async function measured(width,d=20,{lowerCut=false,second=false}={}){
 const capture=await h.capture(binding.faceId);source(capture,width);const producer=binding.child||binding.profile,body=one(capture.solids.bodies.filter(b=>b.id===producer.outputId),'same current output'),m=body.metrics;
 assert.equal(body.featureId,producer.featureId);assert.equal(m.resultKind,'single-solid');assert.equal(m.solidCount,1);assert.equal(m.nativeValidity.valid,true);assert.equal('sha256:'+m.runtime.jsSha256+':'+m.runtime.wasmSha256,build);
 const outerArea=width*(lowerCut?25:50),holeArea=width>140?30*(lowerCut?15:30):0;near(m.nativeVolume,(outerArea-holeArea)*d);for(let i=0;i<3;i++){near(m.nativeBounds.min[i],[0,lowerCut?25:0,0][i]);near(m.nativeBounds.max[i],[width,50,d][i]);}
 assert.equal(capture.solids.bodies.length,second?2:1);if(second){const other=one(capture.solids.bodies.filter(b=>b.id===binding.second.outputId),'unchanged second output');assert.equal(other.featureId,binding.second.featureId);near(other.metrics.nativeVolume,100*50*10);}
 assert.deepEqual(capture.native.counters,binding.counters);const owner=await h.ownership();assert.equal(owner.processing,false);for(const key of ['candidates','accepted','mounts'])assert.equal(owner.resources[key],0);assert.equal(owner.resources.cleanupFailed,false);return capture;
}
async function createProfile(depthMm){const inspect=await h.command('inspect-selected-profiles',{engineRevision:build});assert.equal(inspect.ready,true,inspect.reason);assert.equal(inspect.engineRevision,build);const regions=await h.command('inspect-selected-regions',{revision:inspect.revision,faceId:binding.faceId,depth:depthMm,engineRevision:build}),row=one(regions.regions.filter(r=>r.support==='supported'&&descriptor(r,binding.outerIds,[])),'initial actual outer rectangle region');return h.command('create-selected-extrusion',{revision:inspect.revision,faceId:binding.faceId,regionId:row.regionId,unit:'millimeter',engine:'occ',engineRevision:build,depth:depthMm,bodyPolicy:'separate'});}
async function setup(label,kind){
 const dir=path.join(out,label);fs.mkdirSync(dir);h=await harness(browser,need('CODI_TEST_URL'),dir,record);await h.login();const list=await h.launch();for(const command of ['inspect-selected-profile-source-dimension-regions','edit-selected-profile-source-dimension-region','append-sketch-primitive','edit-closed-sketch-dimension','travel-authored-edit','save','open-project'])assert(list.some(c=>c.id===command),command);await runtime();
 const r=await h.command('inspect-rectangle-creation'),created=await h.command('create-rectangle-sketch',{revision:r.revision,unit:'millimeter',origin:[0,0],width:100,height:50,depth:0});binding={faceId:created.faceId};
 const info=await sourceInfo(),outer=info.objects.filter(o=>o.type==='Segment');assert.equal(outer.length,4);const bottom=one(outer.filter(o=>{const points=info.points.filter(p=>p.parentId===o.id);return points.length===2&&points.every(p=>p.y===0)&&points.some(p=>p.x===0)&&points.some(p=>p.x===100);}), 'initial bottom Segment');Object.assign(binding,{outerIds:outer.map(o=>o.id),bottomId:bottom.id,frame:info.boundaryFrame,innerIds:[]});
 const vertices=[[110,10],[140,10],[140,40],[110,40]];for(let i=0;i<4;i++){const [x,y]=vertices[i],[bx,by]=vertices[(i+1)%4],current=await h.command('inspect-closed-sketches'),added=await h.command('append-sketch-primitive',{revision:current.revision,faceId:binding.faceId,kind:'Segment',role:null,stage:0,data:{a:{x,y},b:{x:bx,y:by}}});assert.equal(typeof added.id,'string');binding.innerIds.push(added.id);}
 const captured=await h.capture(binding.faceId),raw=JSON.parse(captured.native.source);binding.innerObjects=raw.objects.filter(o=>binding.innerIds.includes(o.id));assert.equal(binding.innerObjects.length,4);binding.profile=await createProfile(20);assert.equal(binding.profile.engineRevision,build);
 if(kind==='compatible'){
  const i=await h.command('inspect-worker-solids'),box=await h.command('create-worker-solid-box',{revision:i.revision,version:1,unit:'millimeter',engine:'occ',engineRevision:build,origin:[-1,-1,-1],dimensions:[202,26,22]}),j=await h.command('inspect-worker-solids');binding.child=await h.command('create-worker-solid-boolean',{revision:j.revision,version:1,unit:'millimeter',engine:'occ',kind:'subtract',a:binding.profile.outputId,b:box.outputId});
 }else if(kind==='incompatible')binding.second=await createProfile(10);
 binding.counters=(await h.ownership()).counters;record(label+' genuine public setup',{kind,binding,capture:await measured(100,20,{lowerCut:kind==='compatible',second:kind==='incompatible'})});return{dir};
}
async function persist(label,width,d=20,options={},existingFile=null){
 const before=await measured(width,d,options),file=existingFile||'/Source-region-'+label+'-'+h.username+'.jsketcher.json',saved=await h.save(file,label);
 assert.equal(saved.native.format,'codi-jsketcher-project');assert.equal(saved.native.version,2);assert.equal(saved.native.unit,'millimeter');assert.deepEqual(saved.native.project.model.history,before.native.history);assert.deepEqual(saved.native.project.model.counters,before.native.counters);
 assert.deepEqual(one(saved.native.project.sketches.filter(s=>s.id===binding.faceId),'saved actual source').data,JSON.parse(before.native.source));
 const feature=one(saved.native.project.model.history.filter(e=>e.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2'&&e.params.featureId===binding.profile.featureId),'same saved extrusion');assert.equal(feature.params.faceId,binding.faceId);assert.equal(feature.params.engineRevision,build);assert.equal(feature.params.depth,d);assert.equal(Object.keys(feature.params).length,9);
 receipt.saved.push({label,file,savedFile:path.relative(out,path.join(out,label.startsWith('compatible')?'compatible':'primary',label+'.jsketcher.json')),sha256:saved.sha256,bytes:saved.bytes.length,width,depth:d,binding:structuredClone(binding)});flush();
 await h.freshOpen(file);await runtime();const opened=await measured(width,d,options);assert.deepEqual(opened.native.history,before.native.history);assert.equal(opened.native.source,before.native.source);assert.deepEqual(opened.native.counters,before.native.counters);assert.equal(opened.journal.canUndo,false);assert.equal(opened.journal.canRedo,false);record(label+' native Save sync fresh signed Open',{file,sha256:saved.sha256,before,opened});return file;
}
try{
 await setup('primary','primary');const original=await measured(100),initialHost=await h.command('inspect'),width=await sourceInfo();
 await refusal('Ordinary dimension edit cannot silently reselect changed region','edit-closed-sketch-dimension',{revision:width.revision,faceId:binding.faceId,constraintId:widthTarget(width).constraintId,value:150},'STALE_REGION',{replayed:true});
 await refusal('Unchanged width uses the ordinary region command','inspect-selected-profile-source-dimension-regions',await request(100),'UNCHANGED_DIMENSION');
 await refusal('Touching boundaries stay explicitly unsupported','inspect-selected-profile-source-dimension-regions',await request(110),'UNSUPPORTED_REGION_TOPOLOGY');
 let p=await proposal(150),args=commitArgs(p);assert.equal(p.p.regions.filter(r=>r.support==='supported').length,2,'Both bounded nested regions must be explicit choices');
 await refusal('Wrong proposed source digest','edit-selected-profile-source-dimension-region',{...args,candidateSourceDigest:args.candidateSourceDigest==='0'.repeat(64)?'1'.repeat(64):'0'.repeat(64)},'STALE_PROPOSAL');
 await refusal('Unknown opaque proposed region','edit-selected-profile-source-dimension-region',{...args,regionId:'unknown-current-proposal-region'},'STALE_REGION');
 await depth(25);await measured(100,25);await refusal('Proposal stale after a genuine depth edit','edit-selected-profile-source-dimension-region',args,'STALE_HISTORY');await h.travel('undo');await measured(100);
 p=await proposal(150);args=commitArgs(p);const edited=await h.command('edit-selected-profile-source-dimension-region',args);assert.equal(edited.changed,true);assert.equal(edited.authoredUndo,true);assert.equal(edited.featureId,binding.profile.featureId);assert.equal(edited.regionId,args.regionId);
 const repaired=await measured(150),expectedHistory=structuredClone(original.native.history),selected=one(expectedHistory.filter(e=>e.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2'&&e.params.featureId===binding.profile.featureId),'same original selected feature');selected.params.regionId=args.regionId;assert.deepEqual(repaired.native.history,expectedHistory);assert.equal(repaired.journal.undoTarget.kind,'selected-profile-source-dimension');assert.equal((await h.command('inspect')).documentToken,initialHost.documentToken);
 record('One atomic source dimension and explicit region publication',{proposal:p.p,request:args,edited,original,repaired,analytic:{originalVolume:100000,repairedVolume:132000,outerArea:7500,holeArea:900}});
 await depth(25);await measured(150,25);await h.travel('undo');await measured(150);assert.equal((await h.command('inspect-authored-edits')).undoTarget.kind,'selected-profile-source-dimension');
 await h.travel('undo');const undone=await measured(100);assert.equal(undone.native.source,original.native.source);assert.deepEqual(undone.native.history,original.native.history);
 await h.travel('redo');await measured(150);await h.travel('redo');await measured(150,25);await h.travel('undo');await measured(150);record('Interleaved depth and source-region normal UndoRedo',{capture:await h.capture(binding.faceId)});
 const file=await persist('primary-repaired',150);const reopened=await h.capture(binding.faceId);await ordinaryWidth(160);const reedited=await measured(160);assert.deepEqual(reedited.native.history,reopened.native.history);assert.deepEqual(reedited.native.counters,reopened.native.counters);
 await h.travel('undo');assert.equal((await measured(150)).native.source,reopened.native.source);await h.travel('redo');await measured(160);await persist('primary-reedited',160,20,{},file);await h.retire();h=null;
 await setup('compatible','compatible');const childOriginal=await measured(100,20,{lowerCut:true}),childIntent=one(childOriginal.native.history.filter(e=>e.type==='WORKER_SOLID_BOOLEAN_V1'&&e.params.featureId===binding.child.featureId),'actual Boolean child'),cp=await proposal(150),ca=commitArgs(cp);
 await h.command('edit-selected-profile-source-dimension-region',ca);const childAfter=await measured(150,20,{lowerCut:true});assert.deepEqual(one(childAfter.native.history.filter(e=>e.type==='WORKER_SOLID_BOOLEAN_V1'&&e.params.featureId===binding.child.featureId),'same unchanged child'),childIntent);
 await h.travel('undo');assert.equal((await measured(100,20,{lowerCut:true})).native.source,childOriginal.native.source);await h.travel('redo');await measured(150,20,{lowerCut:true});await persist('compatible-repaired',150,20,{lowerCut:true});record('Unchanged compatible world-space Boolean child survives complete parent replay',{binding,childIntent,analytic:{beforeVolume:50000,afterVolume:66000}});await h.retire();h=null;
 await setup('incompatible','incompatible');const incompatibleBefore=await measured(100,20,{second:true}),ip=await proposal(150),ia=commitArgs(ip);
 await refusal('Other unchanged source-region consumer refuses instead of retargeting','edit-selected-profile-source-dimension-region',ia,'STALE_REGION',{replayed:true});const incompatibleAfter=await measured(100,20,{second:true});assert.deepEqual(incompatibleAfter.native.history,incompatibleBefore.native.history);assert.equal(incompatibleAfter.native.source,incompatibleBefore.native.source);record('Incompatible second extrusion preserves both original intents and native outputs',{binding,before:incompatibleBefore,after:incompatibleAfter});
 receipt.status='PASS';
}catch(error){receipt.status='FAIL';receipt.error={name:error.name,code:error.code??null,message:error.message,stack:error.stack};process.exitCode=1;console.error(error.stack);}
finally{
 try{if(h)await h.retire();record('Owned contexts retired after settled operations and writes',{sharedBrowserRetained:true});}catch(error){receipt.status='FAIL';receipt.cleanupError={name:error.name,message:error.message};process.exitCode=1;}
 receipt.sourceHashesAfter=hashes();if(canonical(receipt.sourceHashesAfter)!==canonical(receipt.sourceHashes)){receipt.status='FAIL';receipt.sourceChanged=true;process.exitCode=1;}flush();await browser.disconnect();
}
