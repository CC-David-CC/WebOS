import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createCommandRegistry} from '../active-system/assets/desktop/command-registry.mjs';
import {createRectangleController} from '../apps/system/jsketcher/rectangle-commands.mjs';
function fixture(){
 const s={subject:'alice',session:{},open:true,calls:0,revision:'r1'},controller=new AbortController();
 const registry=createCommandRegistry({currentSubject:()=>s.subject,currentSession:()=>s.session});
 const craft={inspectRectangleCreation:()=>({ready:true,revision:s.revision,unit:'millimeter'}),async createRectangleSketch(args,options){if(!options.valid()||options.signal.aborted)throw Error('closed');if(args.revision!==s.revision)throw Error('stale');s.calls++;return {persistence:'volatile-workspace'};}};
 const host={session:()=>s.session,signal:controller.signal,commands:registry.scope({windowId:'one',appId:'jsketcher',owner:'alice',isOpen:()=>s.open})};
 const rect=createRectangleController(host,()=>({craft,valid:()=>s.open&&s.subject==='alice'})),dispose=rect.register();
 const exec=(command,args)=>registry.execute({windowId:'one',command,args});return {s,host,rect,registry,controller,craft,dispose,exec};
}
const args=revision=>({revision,unit:'millimeter',origin:[0,0],width:100,height:50,depth:0});
test('scoped discovery, revision and shared core operation',async()=>{const f=fixture();assert.deepEqual(f.registry.list().map(x=>x.id),['inspect-rectangle-creation','create-rectangle-sketch']);const a=await f.exec('inspect-rectangle-creation',{});assert.equal((await f.exec('create-rectangle-sketch',args(a.revision))).persistence,'volatile-workspace');f.s.revision='r2';await assert.rejects(f.exec('create-rectangle-sketch',args(a.revision)),/stale/);assert.equal(f.s.calls,1);f.dispose();assert.equal(f.registry.list().length,0);});
test('invalid arguments and wrong accounts do not invoke core',async()=>{const f=fixture();await assert.rejects(f.exec('create-rectangle-sketch',{...args('r1'),extra:1}));f.s.subject='bob';assert.equal(f.registry.list().length,0);await assert.rejects(f.exec('create-rectangle-sketch',args('r1')));assert.equal(f.s.calls,0);});
test('core receives a synchronous lifetime guard while held',async()=>{const f=fixture();let release,entered;const ready=new Promise(r=>entered=r),hold=new Promise(r=>release=r);f.craft.createRectangleSketch=async(_,options)=>{entered();await hold;if(!options.valid()||options.signal.aborted)throw Error('closed');f.s.calls++;};const pending=f.exec('create-rectangle-sketch',args('r1'));await ready;f.s.session={};release();await assert.rejects(pending);assert.equal(f.s.calls,0);});
test('older runtime is unavailable, rather than faking the operation',()=>{const f=fixture();delete f.craft.createRectangleSketch;assert.throws(()=>f.rect.inspect(),/unavailable/);});
