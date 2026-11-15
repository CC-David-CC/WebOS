// Mock host/window/account protocol only; no geometry, Worker, browser,
// authoring/replay/publication or file persistence qualification.
import test from 'node:test';import assert from 'node:assert/strict';import{getEventListeners}from'node:events';import{runInNewContext}from'node:vm';
import{registerThroughHoleCommands}from'../../../apps/system/jsketcher/through-hole-commands.mjs';
const build='sha256:'+'a'.repeat(64)+':'+'b'.repeat(64);
const center=()=>({revision:'r',version:1,unit:'millimeter',engine:'occ',engineRevision:build,bodyId:'owned-body',sourceFeatureId:10,kind:'centered-through',diameter:10});
const corners=()=>({...center(),kind:'four-corner-through',diameter:4,offsetX:8,offsetY:9}),editCenter=()=>({revision:'h',index:1,featureId:20,diameter:12}),editCorners=()=>({...editCenter(),featureId:21,diameter:5,offsetX:10,offsetY:11});
function fixture(){
 const handlers=new Map(),controller=new AbortController(),state={session:{},version:0,valid:true,throws:false,targets:0,calls:[]},craft={};
 for(const method of['inspectWorkerThroughHoles','inspectWorkerThroughHoleHistory'])craft[method]=function(){state.calls.push({method,args:arguments.length});return{revision:'r',scope:method};};
 for(const method of['createWorkerThroughHole','editWorkerThroughHole'])craft[method]=async(args,options)=>{state.calls.push({method,args,options});return args;};
 const host={signal:controller.signal,session:()=>state.session,commands:{register(def,run){handlers.set(def.id,{def,run});return()=>handlers.delete(def.id);}}};
 const context=()=>{state.targets++;const version=state.version;return{craft,valid:()=>{if(state.throws)throw Error('Destroyed realm');return state.valid&&state.version===version;}};};
 const stop=registerThroughHoleCommands(host,context);return{handlers,controller,state,craft,host,context,stop,run:(id,args)=>handlers.get(id).run(args)};
}
test('four command descriptors use required common fields and optional paired offsets without native/source-face inputs',()=>{
 const f=fixture();assert.deepEqual([...f.handlers.keys()],['inspect-through-holes','create-through-hole','inspect-through-hole-history','edit-through-hole']);const c=f.handlers.get('create-through-hole').def.parameters,e=f.handlers.get('edit-through-hole').def.parameters;
 assert.deepEqual(c.required,Object.keys(center()));assert.equal(c.additionalProperties,false);assert.deepEqual(c.properties.engine.enum,['occ']);assert.deepEqual(c.properties.kind.enum,['centered-through','four-corner-through']);assert(c.properties.offsetX&&c.properties.offsetY);assert(!Object.hasOwn(c.properties,'handle'));assert(!Object.hasOwn(c.properties,'sourceFaceId'));assert.deepEqual(e.required,Object.keys(editCenter()));assert(!Object.hasOwn(e.properties,'kind'));assert(!Object.hasOwn(e.properties,'sourceFeatureId'));
 for(const [id,method]of[['inspect-through-holes','inspectWorkerThroughHoles'],['inspect-through-hole-history','inspectWorkerThroughHoleHistory']]){assert.equal(f.run(id,{}).scope,method);assert.deepEqual(f.state.calls.at(-1),{method,args:0});}f.stop();f.stop();assert.equal(f.handlers.size,0);
});
test('center/corner create/edit delegate exact detached frozen primitives and captured lifetime',async()=>{
 const f=fixture();for(const [id,method,input]of[['create-through-hole','createWorkerThroughHole',center()],['create-through-hole','createWorkerThroughHole',corners()],['edit-through-hole','editWorkerThroughHole',editCenter()],['edit-through-hole','editWorkerThroughHole',editCorners()]]){const expected=structuredClone(input),pending=f.run(id,input);input.revision='changed';input.diameter=999;assert.deepEqual(await pending,expected);const call=f.state.calls.at(-1);assert.equal(call.method,method);assert.notEqual(call.args,input);assert(Object.isFrozen(call.args));assert(Object.isFrozen(call.options));assert.equal(call.options.signal,f.controller.signal);assert.equal(call.options.valid(),true);assert.equal(getEventListeners(f.controller.signal,'abort').length,0);}f.stop();
});
test('center forbids offsets; corner requires both; edit admits only both-or-neither and delegates actual kind validation',async()=>{
 const f=fixture();for(const args of[{...center(),offsetX:8,offsetY:9},{...center(),kind:'four-corner-through'},{...corners(),offsetY:undefined},{...center(),offsetX:8}])await assert.rejects(f.run('create-through-hole',args));
 for(const args of[{...editCenter(),offsetX:8},{...editCorners(),offsetY:undefined},{...editCenter(),kind:'centered-through'},{...editCenter(),sourceFeatureId:10}])await assert.rejects(f.run('edit-through-hole',args));assert.equal(f.state.calls.length,0);
 const refused=Object.assign(Error('Offsets do not match actual feature kind'),{code:'INVALID_FEATURE'});f.craft.editWorkerThroughHole=async args=>{assert.deepEqual(args,editCorners());throw refused;};await assert.rejects(f.run('edit-through-hole',editCorners()),e=>e===refused);f.stop();
});
test('getters, hidden/symbol/extra/native identity fields refuse before target without evaluation',async()=>{
 const f=fixture();let gets=0;for(const field of['kind','diameter','sourceFeatureId']){const input=center();Object.defineProperty(input,field,{enumerable:true,get(){gets++;return 10;}});await assert.rejects(f.run('create-through-hole',input));}
 const hidden=center();Object.defineProperty(hidden,'diameter',{enumerable:false,value:10});for(const input of[hidden,{...center(),[Symbol('x')]:1},{...center(),handle:'native'},{...center(),sourceHandle:'native'},{...center(),sourceFaceId:'face'},{...center(),producerFeatureId:10},{...center(),featureId:20},{...center(),target:'other'}])await assert.rejects(f.run('create-through-hole',input));
 const edit=editCorners();Object.defineProperty(edit,'offsetY',{enumerable:true,get(){gets++;return 11;}});await assert.rejects(f.run('edit-through-hole',edit));assert.throws(()=>f.run('inspect-through-holes',{extra:1}));assert.throws(()=>f.run('inspect-through-hole-history',[]));assert.equal(gets,0);assert.equal(f.state.targets,0);assert.equal(f.state.calls.length,0);f.stop();
});
test('plain cross-realm/null-prototype input accepted; classes/custom prototypes/arrays refused',async()=>{
 const f=fixture();assert.deepEqual(await f.run('edit-through-hole',runInNewContext('({revision:"h",index:1,featureId:20,diameter:12})')),editCenter());assert.deepEqual(await f.run('create-through-hole',Object.assign(Object.create(null),corners())),corners());const before=f.state.calls.length;
 for(const input of[null,undefined,[],new class{constructor(){Object.assign(this,center());}}(),Object.assign(Object.create({inherited:true}),center())])await assert.rejects(f.run('create-through-hole',input));assert.equal(f.state.calls.length,before);f.stop();
});
test('numeric/identity/build bounds reject without coercion and preserve alternate-build core refusal',async()=>{
 const f=fixture();let coerced=0;for(const change of[{revision:''},{revision:'r'.repeat(257)},{version:'1'},{unit:'inch'},{engine:'auto'},{engine:'manifold'},{engineRevision:build+'\n'},{engineRevision:build.toUpperCase()},{bodyId:''},{bodyId:'b'.repeat(1025)},{sourceFeatureId:0},{sourceFeatureId:1.5},{sourceFeatureId:Number.MAX_SAFE_INTEGER+1},{sourceFeatureId:'10'},{kind:'corners'},{diameter:0},{diameter:-1},{diameter:NaN},{diameter:Infinity},{diameter:1e6+1},{diameter:'4'},{diameter:{valueOf(){coerced++;return 4;}}}])await assert.rejects(f.run('create-through-hole',{...center(),...change}));
 for(const change of[{index:-1},{index:256},{index:1.5},{featureId:0},{featureId:Number.MAX_SAFE_INTEGER+1},{diameter:0},{offsetX:0},{offsetY:'11'}])await assert.rejects(f.run('edit-through-hole',{...editCorners(),...change}));assert.equal(coerced,0);assert.equal(f.state.calls.length,0);
 for(const diameter of[Number.MIN_VALUE,1e6])assert.equal((await f.run('edit-through-hole',{...editCenter(),diameter})).diameter,diameter);
 const alternate='sha256:'+'1'.repeat(64)+':'+'2'.repeat(64),error=Object.assign(Error('Exact build unavailable'),{code:'ENGINE_REVISION_MISMATCH'});f.craft.createWorkerThroughHole=async args=>{assert.equal(args.engineRevision,alternate);throw error;};await assert.rejects(f.run('create-through-hole',{...center(),engineRevision:alternate}),e=>e===error);f.stop();
});
test('published schema arrays cannot change private admission',async()=>{
 const f=fixture();for(const [id,args]of[['create-through-hole',center()],['edit-through-hole',editCenter()]]){f.handlers.get(id).def.parameters.required.push('handle');assert.deepEqual(await f.run(id,args),args);await assert.rejects(f.run(id,{...args,handle:'forbidden'}));}assert.equal(f.state.calls.length,2);f.stop();
});
test('unavailable account/window/realm/signal/method refuses without core fallback',async()=>{
 for(const mode of['account','window','realm','signal','method']){const f=fixture();if(mode==='account')f.state.session=null;if(mode==='window')f.state.valid=false;if(mode==='realm')f.state.throws=true;if(mode==='signal')f.controller.abort();if(mode==='method')delete f.craft.createWorkerThroughHole;await assert.rejects(f.run('create-through-hole',center()),/unavailable/);assert.equal(f.state.calls.length,0);f.stop();}
});
test('pending create/edit cancel on account/window/realm/signal loss; late success is inert and listeners clear',async()=>{
 for(const [id,method,args]of[['create-through-hole','createWorkerThroughHole',corners()],['edit-through-hole','editWorkerThroughHole',editCorners()]])for(const mode of['account','window','realm','signal']){
  const f=fixture();let release,scope;f.craft[method]=(_args,options)=>{scope=options;return new Promise(resolve=>release=resolve);};const pending=f.run(id,args);if(mode==='account')f.state.session={};if(mode==='window')f.state.version++;if(mode==='realm')f.state.throws=true;if(mode==='signal')f.controller.abort();
  await assert.rejects(pending,{name:'AbortError'});assert.equal(scope.valid(),false);assert.equal(getEventListeners(f.controller.signal,'abort').length,0);release({late:true});await new Promise(r=>setTimeout(r,0));await assert.rejects(pending,{name:'AbortError'});f.stop();
 }
});
test('synchronous inspection and accepted asynchronous reply recheck captured ownership',async()=>{
 const f=fixture();f.craft.inspectWorkerThroughHoles=()=>{f.state.session={};return{mustNotEscape:true};};assert.throws(()=>f.run('inspect-through-holes',{}),/window or account changed/);
 f.craft.editWorkerThroughHole=async()=>{f.state.valid=false;return{mustNotEscape:true};};await assert.rejects(f.run('edit-through-hole',editCenter()),{name:'AbortError'});assert.equal(getEventListeners(f.controller.signal,'abort').length,0);f.stop();
});
test('exact core refusal/committed errors propagate; already-lost lifetime remains explicit unknown outcome',async()=>{
 const f=fixture();for(const committed of[false,true]){const error=Object.assign(Error('Core refused'),{code:'REFUSED',committed});f.craft.createWorkerThroughHole=async()=>{throw error;};await assert.rejects(f.run('create-through-hole',center()),e=>e===error);}
 let rejectCore;const committed=Object.assign(Error('Accepted command superseded'),{name:'AbortError',committed:true});f.craft.editWorkerThroughHole=()=>new Promise((_resolve,reject)=>rejectCore=reject);const pending=f.run('edit-through-hole',editCenter());f.state.valid=false;rejectCore(committed);await assert.rejects(pending,e=>e===committed);assert.equal(getEventListeners(f.controller.signal,'abort').length,0);f.stop();
 const g=fixture();g.craft.editWorkerThroughHole=async()=>{g.state.valid=false;throw committed;};await assert.rejects(g.run('edit-through-hole',editCenter()),e=>e.name==='AbortError'&&/outcome is unavailable/.test(e.message)&&!Object.hasOwn(e,'committed'));assert.equal(getEventListeners(g.controller.signal,'abort').length,0);g.stop();
});
test('partial registration cleans up reverse order and normal disposal is idempotent',()=>{
 const f=fixture();f.stop();const removed=[];let count=0;assert.throws(()=>registerThroughHoleCommands({...f.host,commands:{register(def){if(++count===4)throw Error('registration failed');return()=>removed.push(def.id);}}},f.context),/registration failed/);assert.deepEqual(removed,['inspect-through-hole-history','create-through-hole','inspect-through-holes']);f.stop();assert.equal(f.handlers.size,0);
});
