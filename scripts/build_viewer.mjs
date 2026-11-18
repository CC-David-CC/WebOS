/** Assemble the existing viewer and public account apps; never builds a replacement shell. */
import {build} from 'esbuild';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,readdir,lstat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const flags=Object.fromEntries(process.argv.slice(2).reduce((pairs,item,index,all)=>index%2?pairs:[...pairs,[item,all[index+1]]],[]));
if(!flags['--output']||!flags['--wordcraft-site']||Object.keys(flags).some(k=>!['--output','--wordcraft-site','--pdfcraft-site','--gridcraft-site','--deckcraft-site'].includes(k)))throw Error('Use --output NEW_EXTERNAL_DIRECTORY --wordcraft-site VERIFIED_ENGINE_SITE [--pdfcraft-site VERIFIED_ENGINE_SITE] [--gridcraft-site VERIFIED_ENGINE_SITE] [--deckcraft-site VERIFIED_ENGINE_SITE]');
const output=path.resolve(flags['--output']),wordcraft=path.resolve(flags['--wordcraft-site']);
if(output===root||output.startsWith(root+path.sep)||root.startsWith(output+path.sep))throw Error('Output must be outside source');
for(let p=output;path.dirname(p)!==p;p=path.dirname(p)){try{if((await lstat(p)).isSymbolicLink())throw Error('Direct output paths required');}catch(e){if(e.code!=='ENOENT')throw e;}}
try{await lstat(output);throw Error('Refusing existing output');}catch(e){if(e.code!=='ENOENT')throw e;}
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const safe=name=>typeof name==='string'&&!path.isAbsolute(name)&&!name.split('/').some(p=>!p||p==='.'||p==='..');
const sourceInputs=new Map();
async function put(name,bytes){if(!safe(name))throw Error('Unsafe output');const target=path.join(output,name);await mkdir(path.dirname(target),{recursive:true});await writeFile(target,bytes);}
async function copySource(relative,name){const parts=relative.split('/'),owner=parts.slice(0,2).join('/');execFileSync('git',['--no-optional-locks','-C',path.join(root,owner),'ls-files','--error-unmatch','--',parts.slice(2).join('/')],{stdio:'pipe'});const bytes=await readFile(path.join(root,relative));sourceInputs.set(relative,hash(bytes));await put(name,bytes);}
async function tree(relative,prefix){for(const item of await readdir(path.join(root,relative),{withFileTypes:true})){if(item.isSymbolicLink())throw Error('Symlinked source input');const name=[prefix,item.name].filter(Boolean).join('/');if(item.isDirectory())await tree(relative+'/'+item.name,name);else if(item.isFile())await copySource(relative+'/'+item.name,name);}}
const engine=JSON.parse(await readFile(path.join(wordcraft,'component-build.json'),'utf8'));
if(engine.schema!=='webos-component-build/1'||engine.component!=='wordcraft'||!Array.isArray(engine.files)||!engine.files.length)throw Error('WordCraft build receipt required');
execFileSync('git',['-C',path.join(root,'apps/wordcraft'),'merge-base','--is-ancestor',engine.sourceCommit,'HEAD']);
let pdfcraft=null,pdfEngine=null;
if(flags['--pdfcraft-site']){
  pdfcraft=path.resolve(flags['--pdfcraft-site']);pdfEngine=JSON.parse(await readFile(path.join(pdfcraft,'component-build.json'),'utf8'));
  if(pdfEngine.schema!=='webos-component-build/1'||pdfEngine.component!=='pdfcraft'||!Array.isArray(pdfEngine.files)||!pdfEngine.files.length)throw Error('PdfCraft build receipt required');
  execFileSync('git',['-C',path.join(root,'apps/pdfcraft'),'merge-base','--is-ancestor',pdfEngine.sourceCommit,'HEAD']);
}
const additionalEngines=[];
for(const [id,name] of [['gridcraft','GridCraft'],['deckcraft','DeckCraft']])if(flags['--'+id+'-site']){
  const site=path.resolve(flags['--'+id+'-site']),receiptBytes=await readFile(path.join(site,'component-build.json'));
  const receipt=JSON.parse(receiptBytes);
  if(receipt.schema!=='webos-component-build/1'||receipt.component!==id||!Array.isArray(receipt.files)||!receipt.files.length)throw Error(id+' build receipt required');
  const selected=execFileSync('git',['-C',path.join(root,'apps',id),'rev-parse','HEAD'],{encoding:'utf8'}).trim();
  if(receipt.sourceCommit!==selected)throw Error(id+' native build must match the selected source exactly');
  additionalEngines.push({id,name,site,receipt,receiptBytes});
}
// The engine is a separately identified, previously built input. Its receipt is
// never relabeled as a fresh compilation of today's bridge/native source.
await mkdir(output);
await tree('platform/desktop/active-system','');
await copySource('apps/terminal/active-system/terminal.js','terminal.js');
for(const item of await readdir(path.join(root,'platform/runtime/active-system/assets/desktop'),{withFileTypes:true})){if(item.isFile()&&item.name.endsWith('.mjs'))await copySource('platform/runtime/active-system/assets/desktop/'+item.name,'assets/desktop/'+item.name);}
await copySource('platform/runtime/active-system/network/strict-json.mjs','network/strict-json.mjs');
await tree('platform/storage/src/webos_storage/vendor/js-sha256','assets/desktop/vendor/js-sha256');
const common={absWorkingDir:root,bundle:true,platform:'browser',format:'esm',target:'es2022',minify:false,legalComments:'eof',metafile:true,write:false,
  nodePaths:[path.join(root,'node_modules')],loader:{'.woff':'file','.woff2':'file','.ttf':'file','.svg':'file','.png':'file'}};
function recordInputs(meta){for(const name of Object.keys(meta.inputs)){if(name.startsWith('<'))continue;const absolute=path.resolve(root,name);if(!absolute.startsWith(root+path.sep))throw Error('Build dependency outside assembly');}}
async function emitBuild(options,destination){const result=await build({...common,...options});recordInputs(result.metafile);for(const input of Object.keys(result.metafile.inputs)){if(input.startsWith('<'))continue;sourceInputs.set(input,hash(await readFile(path.resolve(root,input))));}const files=[];for(const file of result.outputFiles){const name=path.relative(options.outdir,file.path).split(path.sep).join('/');files.push({name,bytes:file.contents});}await destination(files);}
const servicesSource = additionalEngines.length ? {
  stdin: {
    contents: [
      "export * from './assembly/viewer/account-services.mjs';",
      "import {createOfficeRecovery} from './assembly/viewer/office-recovery.mjs';",
      ...additionalEngines.map(({id,name})=>`import * as ${id} from '@webos/${id}/recovery';export const restore${id[0].toUpperCase()+id.slice(1)}Recovery=createOfficeRecovery('${id}','${name}',${id}).restore;`)
    ].join('\n'),
    resolveDir: root, sourcefile: '<account-services>', loader: 'js',
  },
} : {entryPoints:{'account-services':'assembly/viewer/account-services.mjs'}};
await emitBuild({...servicesSource,outdir:path.join(output,'.virtual-services'),outExtension:{'.js':'.mjs'}},async files=>{
  for(const file of files)await put('assets/desktop/'+file.name.replace(/^stdin[.]/,'account-services.'),file.bytes);
});
const apps=[];
for(const id of ['calculator','files','text','wordcraft',...(pdfEngine?['pdfcraft']:[]),...additionalEngines.map(engine=>engine.id),'help']){
  const office=additionalEngines.find(engine=>engine.id===id);
  const recovery=office
    ? `import * as drafts from '@webos/${id}/recovery';import {createOfficeRecovery} from './assembly/viewer/office-recovery.mjs';const officeRecovery=createOfficeRecovery('${id}','${office.name}',drafts);`
    : 'const officeRecovery=null;';
  const delegation=id==='deckcraft'?',delegatedCommands':'';
  const contents=id==='help'?"export {mount} from './apps/help/apps/system/help/index.mjs';":
    `import {mount as appMount${delegation}} from '@webos/${id}';import {mountAccountApp} from './assembly/viewer/account-app.mjs';${recovery}export function mount(host){return mountAccountApp(appMount,host,${JSON.stringify(id)},officeRecovery${delegation});}`;
  await emitBuild({stdin:{contents,resolveDir:root,sourcefile:'<viewer-'+id+'>',loader:'js'},outdir:path.join(output,'.virtual-'+id),outExtension:{'.js':'.mjs'}},async files=>{
    // esbuild calls a stdin entry "stdin"; the loader's stable entry is index.
    for(const f of files)f.name=f.name.replace(/^stdin[.]/,'index.');
    const inventory=Object.fromEntries(files.map(f=>[f.name,{bytes:f.bytes.length,sha256:hash(f.bytes)}]).sort(([a],[b])=>a.localeCompare(b)));
    const bundleSHA256=hash(JSON.stringify(inventory)),prefix='assets/desktop/apps/'+id+'/'+bundleSHA256;
    for(const f of files)await put(prefix+'/'+f.name,f.bytes);
    const entry=inventory['index.mjs'];if(!entry)throw Error('Missing app entry');
    apps.push({id,kind:'browser',path:prefix+'/index.mjs',sha256:entry.sha256,bytes:entry.bytes,bundleSHA256,files:inventory,styles:Object.keys(inventory).filter(n=>n.endsWith('.css'))});
  });
}
await put('assets/desktop/apps.json',JSON.stringify({version:'codi-public-apps/2',hostAPI:2,apps}));
await put('viewer-profile.json',JSON.stringify({version:'webos-existing-viewer/1',apps:apps.map(a=>a.id),guest:false,speech:false,offlineCache:false}));
await put('assets/desktop/cache-manifest.json',JSON.stringify({version:'webos-viewer-cache-disabled/1',id:hash(Buffer.concat([await readFile(path.join(output,'bootstrap.js')),await readFile(path.join(output,'viewer-profile.json')),await readFile(path.join(output,'assets/desktop/apps.json'))]))}));
let engineBytes=0;
for(const file of engine.files){if(!safe(file.path)||!Number.isSafeInteger(file.bytes)||file.bytes<0)throw Error('Invalid engine path/size');const bytes=await readFile(path.join(wordcraft,file.path));if(bytes.length!==file.bytes||hash(bytes)!==file.sha256)throw Error('Engine input hash mismatch');await put('wordcraft/'+file.path,bytes);engineBytes+=bytes.length;}
await put('wordcraft/component-build.json',JSON.stringify(engine,null,2)+'\n');
let pdfEngineBytes=0;
if(pdfEngine){
  for(const file of pdfEngine.files){if(!safe(file.path)||!Number.isSafeInteger(file.bytes)||file.bytes<0)throw Error('Invalid PdfCraft engine path/size');const bytes=await readFile(path.join(pdfcraft,file.path));if(bytes.length!==file.bytes||hash(bytes)!==file.sha256)throw Error('PdfCraft engine input hash mismatch');await put('pdfcraft/'+file.path,bytes);pdfEngineBytes+=bytes.length;}
  await put('pdfcraft/component-build.json',JSON.stringify(pdfEngine,null,2)+'\n');
}
const additionalReceipts={};
for(const {id,site,receipt,receiptBytes} of additionalEngines){
  let total=0;const seen=new Set();
  for(const file of receipt.files){
    if(!safe(file.path)||seen.has(file.path)||file.path==='component-build.json'||!Number.isSafeInteger(file.bytes)||file.bytes<0)throw Error('Invalid '+id+' engine path/size');
    seen.add(file.path);const bytes=await readFile(path.join(site,file.path));
    if(bytes.length!==file.bytes||hash(bytes)!==file.sha256)throw Error(id+' engine input hash mismatch');
    await put(id+'/'+file.path,bytes);total+=bytes.length;
  }
  await put(id+'/component-build.json',receiptBytes);
  additionalReceipts[id+'Engine']={sourceCommit:receipt.sourceCommit,bytes:total,receiptSHA256:hash(receiptBytes)};
}
// No backend/package/credential state is included in public output.
const receipt={schema:'webos-existing-viewer-build/1',engine:{sourceCommit:engine.sourceCommit,bytes:engineBytes,receiptSHA256:hash(await readFile(path.join(wordcraft,'component-build.json')))},
  ...(pdfEngine?{pdfcraftEngine:{sourceCommit:pdfEngine.sourceCommit,bytes:pdfEngineBytes,receiptSHA256:hash(await readFile(path.join(pdfcraft,'component-build.json')))}}:{}),
  ...additionalReceipts,sourceInputs:[...sourceInputs].map(([path,sha256])=>({path,sha256})),apps:apps.map(a=>a.id),qualification:'Source-assembled candidate. Real viewer/browser/account acceptance remains separate; WordCraft engine is a verified prebuilt input.'};
await put('viewer-build.json',JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({output,apps:receipt.apps,sourceInputs:sourceInputs.size,engineBytes,engineSourceCommit:engine.sourceCommit,guest:false,sourceAssembled:true}));
