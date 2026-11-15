// Host settlement/metadata fixtures only; no Native geometry or real files.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {fixture,extracted,sha} from '../native-save-outcomes/fixture.mjs';
import {inspectedProjectIsDirty} from '../../../apps/system/jsketcher/inspect-state.mjs';
const drawing=()=>({version:1,unit:'millimeter',drawingId:'synthetic-drawing',title:'Metadata only, not native geometry',target:{featureId:2,operationType:'WORKER_THROUGH_HOLES_V1',engine:'occ',engineRevision:'sha256:'+'a'.repeat(64)+':'+'b'.repeat(64),output:'complete-native-result'},datum:{featureId:1,faceId:'synthetic-face',regionId:'opaque synthetic region'},sheet:{width:297,height:210,scale:{numerator:1,denominator:2}},views:[{viewId:'top',basis:'top',paperOrigin:[10,10],visibility:'visible-and-hidden'}],dimensions:[]});
const project=()=>({model:{history:[],expressions:'',assembly:[],counters:{featureId:0}},sketches:[]});
const envelope=(withDrawing=true)=>({format:'codi-jsketcher-project',version:withDrawing?3:2,unit:'millimeter',project:project(),...(withDrawing?{drawings:[drawing()]}:{})});
const start=extracted.indexOf(' function supportedEnvelope(value)'),end=extracted.indexOf('\n function snapshot(',start),scope={};vm.createContext(scope);vm.runInContext(extracted.slice(start,end),scope);const supported=scope.supportedEnvelope;
test('actual host admission retains v3 identity and exact drawing-free v2',()=>{for(const drawing of [false,true]){const value=envelope(drawing);assert.equal(supported(value),value);}});
test('actual host rejects mismatched versions and absent/null/multiple drawing containers',()=>{
 for(const change of [v=>delete v.drawings,v=>v.drawings=null,v=>v.drawings=[],v=>v.drawings.push(drawing()),v=>v.version=2,v=>v.version=4,v=>v.drawings[0].unit='inch',v=>v.drawings[0].version=2]){const value=envelope();change(value);assert.throws(()=>supported(value));}
});
test('readonly dirty serializer includes complete definition and optional material/display metadata',()=>{
 const value={...envelope(false),version:3,manufacturing:{version:1,unit:'millimeter',synthetic:'not native proof'},presentation:{version:1,lengthUnit:'inch'},drawings:[drawing()]};const baseline=JSON.stringify(value),getM=()=>value.manufacturing,getP=()=>value.presentation;
 assert.equal(inspectedProjectIsDirty(value.project,baseline,getM,'millimeter',getP,()=>value.drawings[0]),false);
 const changed=structuredClone(value.drawings[0]);changed.title='new paper title';assert.equal(inspectedProjectIsDirty(value.project,baseline,getM,'millimeter',getP,()=>changed),true);
 assert.equal(inspectedProjectIsDirty(value.project,baseline,getM,'millimeter',getP,()=>null),true);
 assert.throws(()=>inspectedProjectIsDirty(value.project,baseline,getM,'millimeter',getP));
 assert.throws(()=>inspectedProjectIsDirty(value.project,baseline,getM,'millimeter',getP,()=>undefined));
});
test('readonly v2 inspection stays exact and newly present drawing is dirty',()=>{
 const value=envelope(false),baseline=JSON.stringify(value);assert.equal(inspectedProjectIsDirty(value.project,baseline,null,'millimeter'),false);assert.equal(inspectedProjectIsDirty(value.project,baseline,null,'millimeter',null,()=>drawing()),true);
});
for(const material of [false,true])test('actual native Save host function/public adapter preserves complete v3 bytes '+(material?'with material/display':'ordinary'),async()=>{
 const f=fixture();try{const value=envelope();if(material){value.manufacturing={version:1,unit:'millimeter',synthetic:'not Native proof'};value.presentation={version:1,lengthUnit:'inch'};}
  const manager=f.scope.active.contentWindow.__CAD_APP.projectManager;manager.snapshotCurrentProject=()=>value;manager.prepareHostSave=async()=>({envelope:value,isCurrent:()=>true});
  const result=await f.run(true);assert.equal(result.kind,'fulfilled');assert.equal(result.value.persistence,'browser');const observed=f.observe(result);assert.equal(observed.events.writes,1);assert.equal(observed.storage[0].sha256,sha(JSON.stringify(value)));assert.equal(f.scope.baseline,JSON.stringify(value));assert.equal(observed.association.dirty,false);assert.equal(observed.coordinator.kind,null);
 }finally{await f.close();}
});
test('malformed v3 manager receipt refuses before storage/association publication',async()=>{const f=fixture();try{const value=envelope();delete value.drawings;f.scope.active.contentWindow.__CAD_APP.projectManager.prepareHostSave=async()=>({envelope:value,isCurrent:()=>true});const result=await f.run(true),observed=f.observe(result);assert.equal(result.kind,'rejected');assert.equal(observed.events.writes,0);assert.equal(observed.association.path,null);assert.equal(observed.coordinator.kind,null);}finally{await f.close();}});
