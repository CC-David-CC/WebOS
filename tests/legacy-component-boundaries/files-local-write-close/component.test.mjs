// Nonvisual, source-extracted Files callback controls. No browser/UI/storage proof.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import {createHash} from 'node:crypto';
import {createDocumentOperations,createDocumentOperationCoordinator} from '../../active-system/assets/desktop/document-operations.mjs';
import {moveSelection} from '../../apps/system/files/move-selection.mjs';
const source=await readFile(process.env.CODI_FILES_SOURCE||new URL('../../apps/system/files/index.mjs',import.meta.url),'utf8');
const body=source.replace(/^import .*;\n/gm,'').replace('export function mount(host)','function mount(host)');
const mutations=new Set(['write','mkdir','move','copyFile','copyTree','importTree','remove','resolve']);
const rows=[];
const defer=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve};};
const settle=async test=>{for(let i=0;i<100;i++){if(test())return;await new Promise(r=>setTimeout(r,1));}throw Error('Fixture did not settle');};
function fixture({guest=false,entries=[],invalidate=false,hold=null,prompt='new',confirm=true,mutateFailure=null,missingPhaseMethod=false,abortAfterMutation=false}={}){
 const controller=new AbortController(),coordinator=createDocumentOperationCoordinator();
 const operations=createDocumentOperations({signal:controller.signal,coordinator});
 const states=[],calls=[],phases=[],refs=[];let stateIndex=0;
 const listing=entries.map(x=>({path:x.id,name:x.name,version:x.version||'v1',directory:!!x.isDir,status:x.conflict?'conflict':'synced'}));
 const checkPhase=async(method,args)=>{const phase=operations.state.phase;calls.push({method,args,phase});assert.equal(phase,'local-write',method+' must own local phase');if(hold?.method===method)await hold.gate.promise;if(mutateFailure?.method===method)throw Error('controlled storage refusal');if(abortAfterMutation)controller.abort('controlled lifetime invalidation after first receipt');return{version:'v2',status:'local'};};
 const files={list:async()=>({entries:listing}),status:async()=>({}),subscribe:()=>()=>{},sync:async()=>calls.push({method:'sync',phase:operations.state.phase}),stat:async path=>{const f=listing.find(x=>x.path===path);if(!f)throw Error('File not found.');return f;},read:async path=>{if(hold?.method==='read')await hold.gate.promise;const f=listing.find(x=>x.path===path);return{data:new Uint8Array([65]),version:f?.version||'v1',status:f?.status||'synced'};}};
 for(const method of mutations)files[method]=(...args)=>checkPhase(method,args);
 const context={files,storage:guest?'guest':'mirror',owner:'owned-fixture',valid:()=>!controller.signal.aborted,path:p=>'/'+p.split('/').filter(Boolean).join('/'),name:n=>{if(!n||n.includes('/'))throw Error('Invalid name');return n;}};
 const account={...context,storage:'mirror'};
 const operationFacade=missingPhaseMethod?{...operations,begin(kind){const token=operations.begin(kind);return token&&{...token,enterLocalWrite:undefined};}}:operations;
 const host={documentOperations:operationFacade,signal:controller.signal,desktop:{},storage:{mirrorFileContext:async()=>account,guestFileContext:async()=>context,pickFolder:async()=>'/dest',openMirrorDocument(){},openMirrorEditor(){}},ui:{prompt:async()=>{if(hold?.method==='prompt')await hold.gate.promise;return typeof prompt==='function'?prompt():prompt;},confirm:async()=>typeof confirm==='function'?confirm():confirm},tools:{loadZip:async()=>({createZip:async()=>{if(hold?.method==='zip')await hold.gate.promise;return new Uint8Array([1]);},readZip:async()=>[{name:'dir/a.txt',data:new Uint8Array([1])}]})}};
 const actions=new Proxy({},{get:(_,id)=>({id})});
 function h(type,props,...children){const node={type,props:props||{},children:children.flat(Infinity)};if(props?.ref){props.ref.current={click(){},isConnected:true,addEventListener(){},removeEventListener(){}};}return node;}
 const sandbox={React:{createElement:h,Fragment:'fragment'},useCallback:f=>f,useMemo:f=>f(),useEffect(){},useRef:v=>{const x={current:v};refs.push(x);return x;},useState:v=>{const i=stateIndex++,value=i===1?(guest?'linux':'account'):i===2?context:i===4?listing:i===7?{}:v;states[i]=value;return[value,n=>states[i]=typeof n==='function'?n(states[i]):n];},defineFileAction:x=>x,ChonkyActions:actions,ChonkyIconName:{},CustomVisibilityState:{},FullFileBrowser:'browser',ChonkyIconFA:{},fileSyncMessage:()=>'',moveSelection,readDownloadSnapshot:async()=>{if(hold?.method==='download')await hold.gate.promise;return new Blob(['x']);},Blob,URL,AbortController,Uint8Array,setTimeout,clearTimeout,innerWidth:1000,innerHeight:800,document:{createElement:()=>({click(){},remove(){}}),body:{append(){}}},window:{},KeyboardEvent:class{}};
 vm.createContext(sandbox);vm.runInContext(body+'\nthis.renderFiles=FilesView;',sandbox,{filename:'Files-source-component.mjs'});
 const tree=sandbox.renderFiles({host}),nodes=[];function visit(n){if(!n||typeof n!=='object')return;nodes.push(n);for(const c of n.children||[])visit(c);}visit(tree);
 const action=nodes.find(n=>n.type==='browser').props.onFileAction;
 const menu=nodes.find(n=>n.props.className==='codi-files-menu');
 const button=label=>menu.children.find(n=>n.children[0]===label).props.onClick();
 const upload=async names=>{button('Upload');const input=nodes.find(n=>n.type==='input'&&n.props.type==='file');input.props.onChange({currentTarget:{files:names.map(name=>({name,size:1,arrayBuffer:async()=>new ArrayBuffer(1)})),isConnected:false}});await settle(()=>!operations.state.busy);};
 const selected=entries.map(x=>({...x,version:x.version||'v1'}));
 const invoke=(id,payload={})=>action({id,payload,state:{selectedFilesForAction:selected,selectedFiles:selected}});
 const conflict=label=>{const box=nodes.find(n=>n.props.className==='codi-file-conflicts');let target;function find(n){if(!n||typeof n!=='object')return;if(n.type==='button'&&n.children[0]===label)target=n;for(const c of n.children||[])find(c);}find(box);assert.ok(target,label);return target.props.onClick();};
 const unlisten=operations.subscribe(state=>{phases.push(state.phase);if(invalidate&&state.phase==='local-write')controller.abort('controlled reentrant invalidation');});
 return{operations,controller,coordinator,states,calls,phases,invoke,upload,button,conflict,close(){unlisten();operations.dispose();}};
}
const file={id:'/a.txt',name:'a.txt'},folder={id:'/folder',name:'folder',isDir:true},zip={id:'/a.zip',name:'a.zip'};
async function test(name,options,run,expected){const f=fixture(options);try{await run(f);await settle(()=>f.operations.state.phase===null);const dispatched=f.calls.filter(x=>mutations.has(x.method));assert.deepEqual(dispatched.map(x=>x.method),expected);for(const call of dispatched)assert.equal(call.phase,'local-write',name+': '+call.method);assert.equal(f.operations.state.phase,null);rows.push({name,pass:true,mutations:expected});}finally{f.close();}}
await test('account upload',{},f=>f.upload(['new.txt']),['write']);
await test('temporary guest upload',{guest:true},f=>f.upload(['new.txt']),['write']);
await test('new directory',{},f=>f.button('New folder'),['mkdir']);
await test('new file',{},f=>f.button('New file'),['write']);
await test('temporary guest copy to account',{guest:true,entries:[file]},f=>f.invoke('codi_copy_to_account'),['write']);
await test('move picker',{entries:[file]},f=>f.invoke('codi_move_to'),['move']);
await test('multi copy',{entries:[file,{id:'/b.txt',name:'b.txt'}]},f=>f.invoke('codi_copy_to'),['copyFile','copyFile']);
await test('directory copy',{entries:[folder]},f=>f.invoke('codi_copy_to'),['copyTree']);
await test('single copy',{entries:[file]},f=>f.invoke('codi_copy_to'),['copyFile']);
await test('rename',{entries:[file]},f=>f.invoke('codi_rename_file'),['move']);
await test('archive final publication',{entries:[file],prompt:'out.zip'},f=>f.invoke('codi_archive_files'),['write']);
await test('temporary guest extraction',{guest:true,entries:[zip]},f=>f.invoke('codi_extract_zip'),['mkdir','mkdir','write']);
await test('account extraction',{entries:[zip]},f=>f.invoke('codi_extract_zip'),['importTree']);
await test('drag move',{entries:[file]},f=>f.invoke('MoveFiles',{files:[file],destination:{id:'/dest',isDir:true}}),['move']);
await test('delete',{entries:[file]},f=>f.invoke('codi_delete_selected'),['remove']);
await test('save conflicting device copy',{entries:[{...file,conflict:true}]},f=>f.conflict('Save device copy…'),['write']);
await test('resolve conflict',{entries:[{...file,conflict:true}]},f=>f.conflict('Use server copy'),['resolve']);
// The two extraction mkdir calls and both move callbacks cover all18 source sites.
for(const name of ['New file','New folder'])await test('reentrant invalidation '+name,{invalidate:true},f=>f.button(name),[]);
await test('missing required token method refuses',{missingPhaseMethod:true},f=>f.button('New file'),[]);
await test('skipped upload never writes',{entries:[file],confirm:false},f=>f.upload(['a.txt']),[]);
await test('same-folder drag no-op never enters',{entries:[file]},f=>f.invoke('MoveFiles',{files:[file],destination:{id:'/',isDir:true}}),[]);
await test('storage refusal releases phase',{mutateFailure:{method:'write'}},f=>f.button('New file'),['write']);
await test('lifetime invalidation prevents later multi-copy dispatch',{entries:[file,{id:'/b.txt',name:'b.txt'}],abortAfterMutation:true},f=>f.invoke('codi_copy_to'),['copyFile']);
await test('lifetime invalidation prevents later delete dispatch',{entries:[file,{id:'/b.txt',name:'b.txt'}],abortAfterMutation:true},f=>f.invoke('codi_delete_selected'),['remove']);
await test('temporary guest extraction stops after invalidation',{guest:true,entries:[zip],abortAfterMutation:true},f=>f.invoke('codi_extract_zip'),['mkdir']);
{
 const gate=defer(),f=fixture({hold:{method:'write',gate}});const pending=f.button('New file');await settle(()=>f.calls.length>0);assert.equal(f.operations.state.phase,'local-write');assert.equal(f.operations.state.busy,true);gate.resolve();await pending;await settle(()=>f.operations.state.phase===null);assert.equal(f.operations.state.phase,null);rows.push({name:'owned mutation held through receipt',pass:true});f.close();
}
{
 const gate=defer(),f=fixture({hold:{method:'prompt',gate}});const pending=f.button('New file');assert.equal(f.operations.state.phase,'prepare');f.controller.abort();gate.resolve();await pending;assert.equal(f.calls.length,0);rows.push({name:'cancelled prompt cannot dispatch',pass:true});f.close();
}
{
 let confirmations=0;const f=fixture({entries:[file,{id:'/b.txt',name:'b.txt'}],confirm:()=>{confirmations++;assert.equal(f.operations.state.phase,confirmations===1?'prepare':'local-write');return true;}});await f.upload(['a.txt','b.txt']);assert.equal(confirmations,2);assert.equal(f.calls.length,2);rows.push({name:'batch retains first-write phase through later prompt',pass:true});f.close();
}
{
 const gate=defer(),f=fixture({entries:[file],prompt:'out.zip',hold:{method:'zip',gate}});const pending=f.invoke('codi_archive_files');await new Promise(r=>setTimeout(r,1));assert.equal(f.operations.state.phase,'prepare');f.controller.abort();gate.resolve();await pending;assert.equal(f.calls.length,0);rows.push({name:'archive preparation remains cancellable',pass:true});f.close();
}
{
 const gate=defer(),f=fixture({entries:[file],hold:{method:'download',gate}});const pending=f.invoke('codi_download');await new Promise(r=>setTimeout(r,1));assert.equal(f.operations.state.phase,'prepare');f.controller.abort();gate.resolve();await pending;assert.equal(f.calls.length,0);rows.push({name:'download preparation remains cancellable',pass:true});f.close();
}
{
 const f=fixture({entries:[file]}),peer=createDocumentOperations({coordinator:f.coordinator});const token=peer.begin('peer-save');assert.equal(token.claimDocument('mirror:/a.txt'),true);await f.invoke('codi_rename_file');assert.deepEqual(f.calls,[]);assert.equal(f.operations.state.phase,null);assert.equal(peer.state.phase,'prepare');token.finish();peer.dispose();rows.push({name:'peer contention does not grant a local mutation phase',pass:true});f.close();
}
console.log(JSON.stringify({scope:'source-extracted nonvisual Files callbacks + actual DocumentOperations; synthetic storage; no shared-host Close/UI/durable-storage claim',sourceSHA256:createHash('sha256').update(source).digest('hex'),rows},null,2));
