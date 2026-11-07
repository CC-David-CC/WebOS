// Boundary metadata/lifetime controls only; delegates return no native model.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {registerSourcePlaneDepthCommands} from '../../../apps/system/jsketcher/source-plane-depth-commands.mjs';
function fixture(){
 const handlers=new Map(),controller=new AbortController(),state={session:{},generation:0,targets:0,calls:[]},craft={inspectSourcePlanes:()=>({transportOnly:true}),editSourcePlaneDepth:async(input,options)=>{state.calls.push({input,options});return{transportOnly:true}}},host={signal:controller.signal,session:()=>state.session,commands:{register(spec,run){handlers.set(spec.id,{spec,run});return()=>handlers.delete(spec.id);}}},target=()=>{state.targets++;const generation=state.generation;return{craft,valid:()=>generation===state.generation}},stop=registerSourcePlaneDepthCommands(host,target);
 return{handlers,controller,state,craft,host,target,stop,run:(id,args={})=>handlers.get(id).run(args)};
}
const intent=()=>({revision:'actual-current-revision',index:1,featureId:2,faceId:'inspected-opaque-face',depth:40});
test('exact signed scalar intent detaches/freezes before Craft and carries host lifetime',async()=>{
 const f=fixture();try{for(const depth of [-1e8,-7,-0,0,40,1e8]){const request={...intent(),depth};await f.run('edit-source-plane-depth',request);const call=f.state.calls.at(-1);request.faceId='changed';request.depth=12;assert.equal(call.input.faceId,'inspected-opaque-face');assert(Object.is(call.input.depth,depth));assert(Object.isFrozen(call.input));assert(Object.isFrozen(call.options));assert.equal(call.options.signal,f.controller.signal);assert.equal(call.options.valid(),true);}assert.deepEqual([...f.handlers.keys()],['inspect-source-planes','edit-source-plane-depth']);const schema=f.handlers.get('edit-source-plane-depth').spec.parameters;assert.deepEqual(schema.required,['revision','index','featureId','faceId','depth']);assert.equal(schema.additionalProperties,false);assert.deepEqual(schema.properties.depth,{type:'number',minimum:-1e8,maximum:1e8});}finally{f.stop()}
});
test('foreign-realm own-data record is captured without a realm prototype restriction',async()=>{const f=fixture();try{await f.run('edit-source-plane-depth',vm.runInNewContext('('+JSON.stringify(intent())+')'));assert.equal(f.state.calls.length,1);}finally{f.stop()}});
test('unknown/missing/symbol/nonenumerable/accessor/inherited fields refuse before target without getter calls',async()=>{
 let invoked=0;const accessor=intent();Object.defineProperty(accessor,'depth',{enumerable:true,get(){invoked++;return 40}});const hidden=intent();Object.defineProperty(hidden,'depth',{value:40,enumerable:false});const inherited=Object.create({revision:'hidden'});Object.assign(inherited,{index:1,featureId:2,faceId:'f',depth:40});
 for(const request of [{...intent(),orientation:'XY'},Object.fromEntries(Object.entries(intent()).filter(([key])=>key!=='faceId')),{...intent(),[Symbol('extra')]:1},accessor,hidden,inherited,[],null]){const f=fixture();try{await assert.rejects(f.run('edit-source-plane-depth',request));assert.equal(f.state.targets,0);assert.equal(f.state.calls.length,0);}finally{f.stop()}}assert.equal(invoked,0);
});
test('invalid numeric/string identities and signed-depth limits refuse before target',async()=>{
 for(const patch of [{revision:''},{revision:'x'.repeat(257)},{index:-1},{index:256},{index:1.5},{featureId:0},{featureId:'2'},{featureId:Number.MAX_SAFE_INTEGER+1},{faceId:''},{faceId:'x'.repeat(257)},...['40',null,true,NaN,Infinity,-Infinity,1e8+1,-1e8-1].map(depth=>({depth}))]){const f=fixture();try{await assert.rejects(f.run('edit-source-plane-depth',{...intent(),...patch}));assert.equal(f.state.targets,0);assert.equal(f.state.calls.length,0);}finally{f.stop()}}
});
test('inspection is exact no-args and rechecks session/window after synchronous delegate',()=>{
 const f=fixture();try{assert.deepEqual(f.run('inspect-source-planes'),{transportOnly:true});assert.throws(()=>f.run('inspect-source-planes',{revision:'extra'}));f.craft.inspectSourcePlanes=()=>{f.state.session={};return{transportOnly:true}};assert.throws(()=>f.run('inspect-source-planes'),/window or account changed/);}finally{f.stop()}
});
test('unavailable/aborted owner refuses before delegate; pending replacement cannot report stale success',async()=>{
 for(const change of [f=>f.controller.abort(),f=>f.state.session=null,f=>f.craft.editSourcePlaneDepth=null]){const f=fixture();try{change(f);await assert.rejects(f.run('edit-source-plane-depth',intent()));assert.equal(f.state.calls.length,0);}finally{f.stop()}}
 const f=fixture();let finish;f.craft.editSourcePlaneDepth=()=>new Promise(resolve=>finish=resolve);try{const pending=f.run('edit-source-plane-depth',intent());f.state.generation++;finish({transportOnly:true});await assert.rejects(pending,{name:'AbortError'});}finally{f.stop()}
});
test('actual host abort settles a held delegate and late fulfillment is inert',async()=>{
 const f=fixture();let finish,settled=0;f.craft.editSourcePlaneDepth=()=>new Promise(resolve=>finish=resolve);try{const pending=f.run('edit-source-plane-depth',intent()).finally(()=>settled++);f.controller.abort();await assert.rejects(pending,{name:'AbortError'});finish({transportOnly:true});await Promise.resolve();assert.equal(settled,1);}finally{f.stop()}
});
test('ordinary refusal and committed failure retain their original receipts',async()=>{
 for(const committed of [false,true]){const f=fixture(),failure=Object.assign(Error('Controlled refusal; no native geometry executed'),{code:committed?'COMMITTED_TEST_ONLY':'NOT_RUN',committed});f.craft.editSourcePlaneDepth=async()=>{throw failure};try{await assert.rejects(f.run('edit-source-plane-depth',intent()),error=>error===failure);}finally{f.stop()}}
});
test('partial registration cleanup and repeated disposal remove only owned commands',()=>{
 const f=fixture();f.stop();f.stop();assert.equal(f.handlers.size,0);const removed=[];let count=0;assert.throws(()=>registerSourcePlaneDepthCommands({...f.host,commands:{register(spec){if(++count===2)throw Error('Registration fixture failure');return()=>removed.push(spec.id)}}},f.target));assert.deepEqual(removed,['inspect-source-planes']);
});
