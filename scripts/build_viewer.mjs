/** Assemble the existing viewer and public account apps; never builds a replacement shell. */
import {build} from 'esbuild';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,readdir,lstat,mkdtemp,rm} from 'node:fs/promises';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {assembleAcad} from './assemble_acad.mjs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {execFileSync} from 'node:child_process';
import {buildLinuxX11} from './build_linux_x11.mjs';
import {buildTerminal} from './build_terminal.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const flags=Object.fromEntries(process.argv.slice(2).reduce((pairs,item,index,all)=>index%2?pairs:[...pairs,[item,all[index+1]]],[]));
const graphicsEngines = [
  {id:'vectorcraft', name:'VectorCraft', extension:'.vectorcraft', forceWebGL:true},
  {id:'figcraft', name:'FigCraft', extension:'.figcraft'},
  {id:'anicraft', name:'AniCraft', extension:'.anicraft', deviceImport:true},
  {id:'lightcraft', name:'LightCraft', extension:'.lightcraft'},
  {id:'designcraft', name:'DesignCraft', extension:'.designcraft'},
  {id:'soundcraft', name:'SoundCraft', extension:'.scraftz'},
  {id:'filmcraft', name:'FilmCraft', extension:'.fcproj'},
  {id:'effectcraft', name:'EffectCraft', extension:'.ecproj'},
  {id:'cadcraft', name:'CADCraft', extension:'.dxf'},
  {id:'texturecraft', name:'TextureCraft', extension:'.tcraft'},
  {id:'solidcraft', name:'SolidCraft', extension:'.sc', legacyExtensions:['.solidcraft','.solvecraft']},
  {id:'pcbcraft', name:'PCBCraft', extension:'.pc'},
  {id:'fieldcraft', name:'FieldCraft', extension:'.fieldcraft'},
  {id:'sketchcraft', name:'SketchCraft', extension:'.sketchcraft', externalModule:true},
  {id:'materialcraft', name:'MaterialCraft', extension:'.mcraft'},
].flatMap(engine => {
  const release = flags['--'+engine.id+'-site'];
  const review = flags['--test-'+engine.id+'-site'];
  if(release && review) throw Error(`Choose one ${engine.name} build input`);
  return release || review ? [{...engine,site:release??review,review:!!review}] : [];
});
const knownFlags = ['--clothcraft-site','--paintcraft-site','--paint-rs-site','--learning-games','--notebook-site','--notecraft-site','--i-success-site','--acad-site','--speech-inputs','--output','--wordcraft-site','--pdfcraft-site','--gridcraft-site','--deckcraft-site','--terminal','--linux-x11-packages','--linux-x11-chromium-inputs',
  '--photocraft-site','--test-photocraft-site',
  ...['vectorcraft','figcraft','anicraft','lightcraft','designcraft','soundcraft','filmcraft','effectcraft','cadcraft','texturecraft','materialcraft','sketchcraft','solidcraft','pcbcraft','fieldcraft'].flatMap(id=>['--'+id+'-site','--test-'+id+'-site'])];
if(!flags['--output']||!flags['--wordcraft-site']||Object.keys(flags).some(k=>!knownFlags.includes(k))) {
  throw Error('Use --output NEW_EXTERNAL_DIRECTORY --wordcraft-site VERIFIED_ENGINE_SITE with optional supported component site flags');
}
if(flags['--photocraft-site']&&flags['--test-photocraft-site'])throw Error('Choose a single PhotoCraft build input');
if(flags['--terminal']!==undefined&&!['enabled','account-home'].includes(flags['--terminal']))throw Error('Use --terminal enabled or --terminal account-home to package Terminal');
const terminalEnabled=flags['--terminal']!==undefined;
const accountGuestHome=flags['--terminal']==='account-home';
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
const officeEngines = [...additionalEngines];
const photoTest = flags['--test-photocraft-site'];
const photoSite = flags['--photocraft-site'] ?? photoTest;
if(photoSite){
  const site=path.resolve(photoSite);
  const receiptBytes=await readFile(path.join(site,'component-build.json'));
  const receipt=JSON.parse(receiptBytes);
  const id='photocraft', component=path.join(root,'apps',id);
  const commit=value=>typeof value==='string'&&/^[0-9a-f]{40}$/.test(value);
  if(receipt.schema!=='webos-component-build/1'||receipt.component!==id||!commit(receipt.sourceCommit)||
      !Array.isArray(receipt.files)||!receipt.files.some(file=>file.path==='index.html'))throw Error('Verified PhotoCraft package required');
  const git=(...args)=>execFileSync('git',['--no-optional-locks','-C',component,...args],{encoding:'utf8'}).trim();
  if(git('rev-parse',receipt.sourceCommit+'^{tree}')!==receipt.sourceTree)throw Error('PhotoCraft native source tree mismatch');
  if(!photoTest && (receipt.sourceCommit!==git('rev-parse','HEAD') || receipt.packagingSourceCommit)){
    throw Error('The PhotoCraft release requires a directly built package from its selected source');
  }
  if(receipt.packagingSourceCommit){
    if(!commit(receipt.packagingSourceCommit)||receipt.compiledInputsUnchanged!==true||
        git('diff','--name-only',receipt.sourceCommit,receipt.packagingSourceCommit)!=='packaging/web/package.sh'){
      throw Error('PhotoCraft repack must preserve compiled source inputs');
    }
  }
  additionalEngines.push({id,site,receipt,receiptBytes});
}
for(const graphics of graphicsEngines) {
  const {id} = graphics;
  const site = path.resolve(graphics.site);
  const receiptBytes = await readFile(path.join(site,'component-build.json'));
  const receipt = JSON.parse(receiptBytes);
  const component = path.join(root,'apps',id);
  const git = (...args) => execFileSync('git',['--no-optional-locks','-C',component,...args],{encoding:'utf8'}).trim();
  const oid = value => typeof value === 'string' && /^[0-9a-f]{40}$/.test(value);
  if(receipt.schema!=='webos-component-build/1'||receipt.component!==id||!oid(receipt.sourceTree)||
      !Array.isArray(receipt.files)||!receipt.files.some(file=>file.path==='index.html')) {
    throw Error(`Verified ${id} package required`);
  }
  if(!graphics.review && (receipt.localReview || receipt.packagingSourceCommit || receipt.sourceCommit !== git('rev-parse','HEAD'))) {
    throw Error(`${id} release requires a direct build from its selected component commit`);
  }
  if(graphics.review && receipt.localReview === true && receipt.sourceCommit === null) {
    if(!oid(receipt.baseCommit)||git('rev-parse','HEAD')!==receipt.baseCommit||git('cat-file','-t',receipt.sourceTree)!=='tree') {
      throw Error(`${id} local review tree and selected base are required`);
    }
  } else if(!oid(receipt.sourceCommit)||git('rev-parse',receipt.sourceCommit+'^{tree}')!==receipt.sourceTree) {
    throw Error(`${id} native build source tree mismatch`);
  }
  additionalEngines.push({...graphics,site,receipt,receiptBytes});
}
// The engine is a separately identified, previously built input. Its receipt is
// never relabeled as a fresh compilation of today's bridge/native source.
await mkdir(output);
await tree('platform/desktop/active-system','');
await copySource('apps/terminal/active-system/terminal.js','terminal.js');
for(const item of await readdir(path.join(root,'platform/runtime/active-system/assets/desktop'),{withFileTypes:true})){if(item.isFile()&&item.name.endsWith('.mjs'))await copySource('platform/runtime/active-system/assets/desktop/'+item.name,'assets/desktop/'+item.name);}
await copySource('apps/linux/assets/desktop/guest-network.mjs','assets/desktop/guest-network.mjs');
await copySource('platform/runtime/active-system/network/strict-json.mjs','network/strict-json.mjs');
await tree('platform/storage/src/webos_storage/vendor/js-sha256','assets/desktop/vendor/js-sha256');
const storageBrowser = 'platform/storage/active-system/storage/browser';
for (const file of ['temporary-files.mjs', 'account-context.mjs', 'mirror.mjs', 'verified-content.mjs',
  ...(accountGuestHome ? ['account-home.mjs'] : [])]) {
  await copySource(storageBrowser+'/'+file, 'storage/browser/'+file);
}
await tree(storageBrowser+'/opfs', 'storage/browser/opfs');
const common={absWorkingDir:root,bundle:true,platform:'browser',format:'esm',target:'es2022',minify:false,legalComments:'eof',metafile:true,write:false,
  nodePaths:[path.join(root,'node_modules')],loader:{'.woff':'file','.woff2':'file','.ttf':'file','.svg':'file','.png':'file'}};
async function emitBuild(options, destination) {
  const result = await build({...common, ...options});
  for (const [input, metadata] of Object.entries(result.metafile.inputs)) {
    if (input.startsWith('<')) continue;
    // esbuild creates empty virtual modules for dependencies disabled by a browser mapping.
    if (input.startsWith('(disabled):') && metadata.bytes === 0) continue;
    const absolute = path.resolve(root, input);
    if (!absolute.startsWith(root + path.sep)) throw Error('Build dependency outside assembly');
    sourceInputs.set(input, hash(await readFile(absolute)));
  }
  const files = result.outputFiles.map(file => ({
    name: path.relative(options.outdir, file.path).split(path.sep).join('/'),
    bytes: file.contents,
  }));
  await destination(files);
}
const servicesSource = officeEngines.length || photoSite || graphicsEngines.length ? {
  stdin: {
    contents: [
      "export * from './assembly/viewer/account-services.mjs';",
      "import {createOfficeRecovery} from './assembly/viewer/office-recovery.mjs';",
      ...officeEngines.map(({id,name})=>`import * as ${id} from '@webos/${id}/recovery';export const restore${id[0].toUpperCase()+id.slice(1)}Recovery=createOfficeRecovery('${id}','${name}',${id}).restore;`),
      ...(photoSite ? ["import {photoRecovery} from './assembly/viewer/photocraft-app.mjs';export const restorePhotocraftRecovery=photoRecovery.restore;"] : []),
      ...(graphicsEngines.length ? ["import {createCraftRecovery} from './assembly/viewer/craft-account-recovery.mjs';"] : []),
      ...graphicsEngines.map(({id,name,extension,legacyExtensions})=>`export const restore${name[0]+id.slice(1)}Recovery=createCraftRecovery(${JSON.stringify({app:id,name,extension,legacyExtensions})}).restore;`),
    ].join('\n'),
    resolveDir: root, sourcefile: '<account-services>', loader: 'js',
  },
} : {entryPoints:{'account-services':'assembly/viewer/account-services.mjs'}};
await emitBuild({...servicesSource,outdir:path.join(output,'.virtual-services'),outExtension:{'.js':'.mjs'}},async files=>{
  for(const file of files)await put('assets/desktop/'+file.name.replace(/^stdin[.]/,'account-services.'),file.bytes);
});
const apps=[];
for(const id of ['calculator','files','text','wordcraft',...(pdfEngine?['pdfcraft']:[]),...additionalEngines.map(engine=>engine.id),'help']){
  if (id === 'calculator') {
    const graphing = 'apps/calculator/graphing';
    const files = [];
    const outdir = path.join(output,'.virtual-calculator');
    for (const [name,format] of [['index','esm'],['engine-worker','iife']]) {
      await emitBuild({entryPoints:{[name]:graphing+'/src/'+name+'.mjs'}, format, outdir,
        outExtension:{'.js':'.mjs'}, loader:{'.css':'text'}, minify:true}, async built => files.push(...built));
    }
    const notices = ['THIRD_PARTY_NOTICES.txt', ...(await readdir(path.join(root,graphing,'licenses'))).sort().map(name => 'licenses/'+name)];
    for (const name of notices) {
      const source = graphing+'/'+name;
      execFileSync('git',['-C',path.join(root,'apps/calculator'),'ls-files','--error-unmatch','--','graphing/'+name],{stdio:'pipe'});
      const bytes = await readFile(path.join(root,source));
      sourceInputs.set(source,hash(bytes));
      files.push({name,bytes});
    }
    await registerFiles(id,files);
    continue;
  }
  const office=officeEngines.find(engine=>engine.id===id);
  const recovery=office
    ? `import * as drafts from '@webos/${id}/recovery';import {createOfficeRecovery} from './assembly/viewer/office-recovery.mjs';const officeRecovery=createOfficeRecovery('${id}','${office.name}',drafts);`
    : 'const officeRecovery=null;';
  const delegation=id==='deckcraft'?',delegatedCommands':'';
  const graphics = graphicsEngines.find(app => app.id===id);
  const graphicsProject = graphics && JSON.stringify({
    app:id,name:graphics.name,extension:graphics.extension,forceWebGL:graphics.forceWebGL,deviceImport:graphics.deviceImport
  });
  const contents=id==='help'?"export {mount} from './apps/help/apps/system/help/index.mjs';":
    id==='photocraft'?"export {mount} from './assembly/viewer/photocraft-app.mjs';":
    id==='lightcraft'?"export {mount} from './assembly/viewer/lightcraft-app.mjs';":
    id==='designcraft'?"export {mount} from './assembly/viewer/designcraft-app.mjs';":
    id==='soundcraft'?"export {mount} from './assembly/viewer/soundcraft-app.mjs';":
    id==='filmcraft'?"export {mount} from './assembly/viewer/filmcraft-app.mjs';":
    id==='effectcraft'?"export {mount} from './assembly/viewer/effectcraft-app.mjs';":
    id==='cadcraft'?"export {mount} from './assembly/viewer/cadcraft-app.mjs';":
    id==='solidcraft'?"export {mount} from './assembly/viewer/solidcraft-app.mjs';":
    id==='pcbcraft'||id==='fieldcraft'?`export {mount} from './assembly/viewer/${id}-app.mjs';`:
    id==='sketchcraft'?"export {mount} from './assembly/viewer/sketchcraft-app.mjs';":
    id==='materialcraft'?"export {mount} from './assembly/viewer/materialcraft-app.mjs';":
    id==='texturecraft'?"export {mount} from './assembly/viewer/texturecraft-app.mjs';":
    graphics?`import {mountCraftAccount} from './assembly/viewer/craft-account-app.mjs';import {createCraftRecovery} from './assembly/viewer/craft-account-recovery.mjs';const project=${graphicsProject};const recovery=createCraftRecovery(project);export function mount(host){return mountCraftAccount(host,{...project,recovery,reviewWindowClose:true});}`:
    `import {mount as appMount${delegation}} from '@webos/${id}';import {mountAccountApp} from './assembly/viewer/account-app.mjs';${recovery}export function mount(host){return mountAccountApp(appMount,host,${JSON.stringify(id)},officeRecovery${delegation});}`;
  await emitBuild({stdin:{contents,resolveDir:root,sourcefile:'<viewer-'+id+'>',loader:'js'},outdir:path.join(output,'.virtual-'+id),outExtension:{'.js':'.mjs'}},async files=>{
    // esbuild calls a stdin entry "stdin"; the loader's stable entry is index.
    for(const f of files)f.name=f.name.replace(/^stdin[.]/,'index.');
    await registerFiles(id,files,files.filter(f=>f.name.endsWith('.css')).map(f=>f.name));
  });
}
async function registerFiles(id,files,styles=[]){
    const inventory=Object.fromEntries(files.map(f=>[f.name,{bytes:f.bytes.length,sha256:hash(f.bytes)}]).sort(([a],[b])=>a.localeCompare(b)));
    const bundleSHA256=hash(JSON.stringify(inventory)),prefix='assets/desktop/apps/'+id+'/'+bundleSHA256;
    for(const f of files)await put(prefix+'/'+f.name,f.bytes);
    const entry=inventory['index.mjs'];if(!entry)throw Error('Missing app entry');
    apps.push({id,kind:'browser',path:prefix+'/index.mjs',sha256:entry.sha256,bytes:entry.bytes,bundleSHA256,files:inventory,styles});
}

if (flags['--learning-games'] !== undefined) {
  if (flags['--learning-games'] !== 'enabled') throw Error('Use --learning-games enabled to bundle the seven learning games.');
  const ids = ['fraction-farm','market-math','math-path','pocket-conquest','rule-detective','tile-islands','word-weaver'];
  for (const id of ids) {
    const entry = 'apps/' + id + '/index.mjs';
    const style = 'apps/' + id + '/index.css';
    const css = await readFile(path.join(root, style));
    sourceInputs.set(style, hash(css));
    await emitBuild({entryPoints: {index: entry}, outdir: path.join(output,'.virtual-'+id), outExtension: {'.js':'.mjs'}}, async files => {
      files.push({name: 'index.css', bytes: css});
      await registerFiles(id, files, ['index.css']);
    });
  }
}

// These native mounts own their Shadow DOM styles. Keep the Isobar worker, ES
// modules and tile assets at their original relative URLs in the hashed bundle.
const mapsRoot='apps/isobar';
const mapFiles=execFileSync('git',['-C',path.join(root,mapsRoot),'ls-files','-z','--','app.mjs','js','css','vendor','favicon.svg','LICENSE'],{encoding:'utf8'}).split('\0').filter(Boolean);
const mapBundle=[];
for(const name of mapFiles){
  const relative=mapsRoot+'/'+name, bytes=await readFile(path.join(root,relative));
  sourceInputs.set(relative,hash(bytes));
  mapBundle.push({name:name==='app.mjs'?'index.mjs':name,bytes});
}
await registerFiles('weather-maps',mapBundle);
await copySource('apps/isobar/favicon.svg','assets/desktop/weather-maps.svg');
await copySource('apps/pohoda/app/icon.svg','assets/desktop/weather.svg');
const weatherDist=await mkdtemp(path.join(tmpdir(),'webos-weather-dist-'));
try {
  execFileSync(process.execPath,['scripts/build-webos.mjs','--outdir',weatherDist],{cwd:path.join(root,'apps/pohoda'),stdio:['ignore','inherit','inherit']});
  const inputs=JSON.parse(await readFile(path.join(weatherDist,'build-inputs.json'),'utf8'));
  for(const item of inputs){
    if(!safe(item.path))throw Error('Unsafe Weather build input');
    const relative='apps/pohoda/'+item.path;
    if(hash(await readFile(path.join(root,relative)))!==item.sha256)throw Error('Weather source changed during build');
    sourceInputs.set(relative,item.sha256);
  }
  const files=[{name:'index.mjs',bytes:await readFile(path.join(root,'apps/pohoda/app.mjs'))},
    {name:'LICENSE',bytes:await readFile(path.join(root,'apps/pohoda/LICENSE'))}];
  for(const name of ['pohoda.mjs','pohoda.mjs.LEGAL.txt','THIRD_PARTY_LICENSES.txt']){
    files.push({name:'dist/'+name,bytes:await readFile(path.join(weatherDist,name))});
  }
  await registerFiles('weather',files);
} finally {
  await rm(weatherDist,{recursive:true,force:true});
}
if(terminalEnabled)apps.push(await buildTerminal({root,output,copySource,accountHome:accountGuestHome,
  recordSource:async relative=>sourceInputs.set(relative,hash(await readFile(path.join(root,relative))))}));
if (flags['--acad-site']) {
  const sourceCommit=execFileSync('git',['-C',root,'rev-parse','HEAD:apps/acad'],{encoding:'utf8'}).trim();
  const checkout=path.join(root,'apps/acad');
  const head=execFileSync('git',['-C',checkout,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
  if (head!==sourceCommit) throw Error('ACAD checkout must match the assembly pin');
  const pins='modules/engine/source-occt/pins.mjs';
  const committed=execFileSync('git',['-C',checkout,'show',sourceCommit+':'+pins]);
  if (!committed.equals(await readFile(path.join(checkout,pins)))) throw Error('Modified ACAD engine pins');
  const {sourceEngine}=await import(pathToFileURL(path.join(checkout,pins)));
  apps.push(await assembleAcad({site:flags['--acad-site'],sourceCommit,sourceEngine,put}));
  sourceInputs.set('apps/acad/'+pins,hash(committed));
}
// MathCraft has an independent app checkout and a browser-local Octave runtime.
{
  const id = 'mathcraft', appRoot = 'apps/' + id;
  const manifest = appRoot + '/webos-files.json';
  let inventory;
  try { inventory = await readFile(path.join(root, manifest)); }
  catch (e) { if (e.code !== 'ENOENT') throw e; }
  if (inventory) {
    sourceInputs.set(manifest, hash(inventory));
    const names = JSON.parse(inventory);
    if (!Array.isArray(names) || new Set(names).size !== names.length ||
        !['app.mjs','icon.svg','vendor/octave/octave.wasm'].every(n => names.includes(n)) ||
        names.some(n => typeof n !== 'string' || !safe(n) || n.split('/').some(s => !s || s === '.' || s === '..') ||
          !/^(app[.]mjs|icon[.]svg|(?:src|lab|examples|vendor[/]octave)[/][a-zA-Z0-9._-]+)$/.test(n)))
      throw Error('Invalid MathCraft app inventory');
    const bundle = [];
    for (const name of names) {
      const source = appRoot + '/' + name, bytes = await readFile(path.join(root, source));
      sourceInputs.set(source, hash(bytes));
      bundle.push({name: name === 'app.mjs' ? 'index.mjs' : name, bytes});
      if (name === 'icon.svg') await put('assets/desktop/mathcraft.svg', bytes);
    }
    await registerFiles(id, bundle);
    // The corresponding source is available separately from the startup payload.
    for (const name of ['source-3996ed4.tar.xz', 'PROVENANCE.md','GNU-GPL-3.txt','WASM-wrapper.LICENSE','EMSCRIPTEN.LICENSE','prepare-no-eval.mjs','SHA256SUMS']) {
      const source = appRoot + '/vendor/octave/' + name, bytes = await readFile(path.join(root, source));
      sourceInputs.set(source, hash(bytes));
      await put('assets/legal/mathcraft/' + name, bytes);
    }
  }
}
if (flags['--linux-x11-chromium-inputs'] && !flags['--linux-x11-packages']) {
  throw Error('Chromium inputs require the locked Linux X11 packages');
}
if (flags['--linux-x11-packages']) {
  if (!accountGuestHome) throw Error('The X11 release requires the account-home runtime');
  const files = await buildLinuxX11(root,flags['--linux-x11-packages'],sourceInputs,flags['--linux-x11-chromium-inputs']);
  await registerFiles('linux-x11',files);
  await copySource('apps/linux-x11/docs/debian-sources.json','assets/legal/linux-x11/debian-sources.json');
  if (flags['--linux-x11-chromium-inputs']) {
    await copySource('apps/linux-x11/docs/chromium-source-packages.json','assets/legal/linux-x11/chromium-source-packages.json');
    await copySource('apps/linux-x11/docs/ncurses-copyright.txt','assets/legal/linux-x11/ncurses-copyright.txt');
  }
}
if (flags['--paint-rs-site']) {
  const appRoot = 'apps/paint-rs';
  const checkout = path.join(root, appRoot);
  const site = path.resolve(flags['--paint-rs-site']);
  const git = (cwd, ...args) => execFileSync('git', ['-C', cwd, ...args], {encoding:'utf8'}).trim();
  const receipt = JSON.parse(await readFile(path.join(site, 'component-build.json'), 'utf8'));
  const pin = git(root, 'rev-parse', 'HEAD:' + appRoot);
  if (receipt.schema !== 'webos-component-build/1' || receipt.component !== 'paint-rs' ||
      receipt.sourceCommit !== pin || git(checkout, 'rev-parse', 'HEAD') !== pin ||
      receipt.sourceTree !== git(checkout, 'rev-parse', 'HEAD^{tree}') ||
      receipt.cargoLockSHA256 !== hash(await readFile(path.join(checkout, 'Cargo.lock'))) ||
      !Array.isArray(receipt.files)) {
    throw Error('Invalid Paint.RS build receipt');
  }
  const bundle = [];
  const names = new Set();
  for (const item of receipt.files) {
    const name = item.path;
    if (typeof name !== 'string' || names.has(name) ||
        !name.split('/').every(part => /^[A-Za-z0-9_@+-][A-Za-z0-9_@+.\-]*$/.test(part))) {
      throw Error('Invalid Paint.RS package path');
    }
    names.add(name);
    const bytes = await readFile(path.join(site, name));
    if (bytes.length !== item.bytes || hash(bytes) !== item.sha256) {
      throw Error('Invalid Paint.RS artifact ' + name);
    }
    bundle.push({name:'webos/native/' + name, bytes});
  }
  if (!names.has('index.html') || !names.has('notices/LICENSE') ||
      !names.has('sam_worker_bg.wasm') ||
      ![...names].some(name => /^paintrs-.+_bg[.]wasm[.]gz$/.test(name))) {
    throw Error('Incomplete Paint.RS package');
  }
  const entries = new Map([
    ['app.mjs', 'index.mjs'],
    ['webos/app.css', 'webos/app.css'],
    ['LICENSE', 'LICENSE'],
    ['LICENSE.md', 'LICENSE.md'],
    ['NOTICE.md', 'NOTICE.md'],
  ]);
  for (const [source, name] of entries) {
    const relative = appRoot + '/' + source;
    const bytes = await readFile(path.join(root, relative));
    const committed = execFileSync('git', ['-C', checkout, 'show', 'HEAD:' + source]);
    if (!bytes.equals(committed)) throw Error('Paint.RS input differs from its pin: ' + source);
    sourceInputs.set(relative, hash(bytes));
    bundle.push({name, bytes});
  }
  await registerFiles('paint-rs', bundle);
}
if (flags['--paintcraft-site']) {
  const appRoot = 'apps/paintcraft', checkout = path.join(root,appRoot);
  const site = path.resolve(flags['--paintcraft-site']);
  const git = (cwd,...args) => execFileSync('git',['-C',cwd,...args],{encoding:'utf8'}).trim();
  const receipt = JSON.parse(await readFile(path.join(site,'component-build.json'),'utf8'));
  const pin = git(root,'rev-parse','HEAD:'+appRoot);
  if (receipt.schema !== 'webos-component-build/1' || receipt.component !== 'paintcraft' ||
      receipt.sourceCommit !== pin || git(checkout,'rev-parse','HEAD') !== pin ||
      receipt.sourceTree !== git(checkout,'rev-parse','HEAD^{tree}') ||
      receipt.cargoLockSHA256 !== hash(await readFile(path.join(checkout,'Cargo.lock'))) ||
      receipt.pnpmLockSHA256 !== hash(await readFile(path.join(checkout,'apps/paintcraft-web/pnpm-lock.yaml'))) ||
      !Array.isArray(receipt.files)) throw Error('Invalid PaintCraft build receipt');
  const bundle = [], names = new Set();
  for (const item of receipt.files) {
    const name = item.path;
    if (typeof name !== 'string' || !/^(runtime|legal)\//.test(name) ||
        name.split('/').some(part=>!part || part==='.' || part==='..' || part.includes('\\')) || names.has(name)) {
      throw Error('Invalid PaintCraft package path');
    }
    names.add(name);
    const bytes = await readFile(path.join(site,name));
    if (bytes.length !== item.bytes || hash(bytes) !== item.sha256) throw Error('Invalid PaintCraft artifact '+name);
    bundle.push({name,bytes});
  }
  if (!names.has('runtime/index.html') || !names.has('runtime/fonts/manifest.json') ||
      !names.has('legal/LICENSE') || ![...names].some(n=>n.endsWith('.wasm'))) throw Error('Incomplete PaintCraft package');
  for (const name of ['app.mjs','webos/workspace.css']) {
    const source = appRoot+'/'+name;
    const bytes = await readFile(path.join(root,source));
    if (hash(bytes) !== hash(execFileSync('git',['-C',checkout,'show','HEAD:'+name]))) throw Error('PaintCraft wrapper differs from its pin');
    sourceInputs.set(source,hash(bytes)); bundle.push({name:name==='app.mjs'?'index.mjs':name,bytes});
  }
  await registerFiles('paintcraft',bundle);
}
if (flags['--clothcraft-site']) {
  const appRoot = 'apps/clothcraft';
  const checkout = path.join(root, appRoot);
  const site = path.resolve(flags['--clothcraft-site']);
  const git = (cwd, ...args) => execFileSync('git', ['-C', cwd, ...args], {encoding:'utf8'}).trim();
  const receipt = JSON.parse(await readFile(path.join(site,'component-build.json'),'utf8'));
  const pin = git(root,'rev-parse','HEAD:'+appRoot);
  const required = new Map([
    ['index.mjs','webos/app.mjs'],
    ['webos/view.mjs','webos/view.mjs'],
    ['webos/worker.mjs','webos/worker.mjs'],
    ['webos/workspace.css','webos/workspace.css'],
    ['legal/LICENSE','LICENSE'],
    ['legal/THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES.md'],
    ['legal/MAKEHUMAN.md','assets/makehuman/LICENSE.ASSETS.md'],
    ['webos/native/clothcraft.js',null],
    ['webos/native/clothcraft_bg.wasm',null],
  ]);
  if (receipt.schema !== 'webos-component-build/1' || receipt.component !== 'clothcraft' ||
      receipt.sourceCommit !== pin || git(checkout,'rev-parse','HEAD') !== pin ||
      receipt.sourceTree !== git(checkout,'rev-parse','HEAD^{tree}') ||
      receipt.cargoLockSHA256 !== hash(await readFile(path.join(checkout,'Cargo.lock'))) ||
      receipt.wasmBindgen !== '0.2.129' || !Array.isArray(receipt.files) ||
      receipt.files.length !== required.size) {
    throw Error('Invalid ClothCraft build receipt');
  }
  const bundle = [];
  for (const record of receipt.files) {
    const name = record.path;
    if (!required.has(name)) throw Error('Invalid ClothCraft artifact path: '+name);
    const tracked = required.get(name);
    required.delete(name);
    const bytes = await readFile(path.join(site,name));
    if (bytes.length !== record.bytes || hash(bytes) !== record.sha256) {
      throw Error('ClothCraft artifact hash mismatch: '+name);
    }
    if (tracked) {
      const committed = execFileSync('git',['-C',checkout,'show','HEAD:'+tracked]);
      if (!bytes.equals(committed)) throw Error('ClothCraft file differs from its pin: '+tracked);
      sourceInputs.set(appRoot+'/'+tracked,hash(bytes));
    }
    bundle.push({name,bytes});
  }
  await registerFiles('clothcraft',bundle);
}
if (flags['--notecraft-site']) {
  const appRoot = 'apps/notecraft';
  const site = path.resolve(flags['--notecraft-site']);
  const checkout = path.join(root,appRoot);
  const git = (cwd,...args) => execFileSync('git',['-C',cwd,...args],{encoding:'utf8'}).trim();
  const pin = git(root,'rev-parse','HEAD:'+appRoot);
  const receipt = JSON.parse(await readFile(path.join(site,'component-build.json'),'utf8'));
  const nativeNames = ['NotoSansCJKsc-Regular.otf','OFL-NotoSansCJKsc.txt','notecraft.js','notecraft_bg.wasm','welcome.zip'];
  if (receipt.schema !== 'webos-component-build/1' || receipt.component !== 'notecraft' ||
      receipt.sourceCommit !== pin || pin !== git(checkout,'rev-parse','HEAD') ||
      receipt.sourceTree !== git(checkout,'rev-parse','HEAD^{tree}') ||
      receipt.cargoLockSHA256 !== hash(await readFile(path.join(checkout,'Cargo.lock'))) ||
      receipt.wasmBindgen !== 'wasm-bindgen 0.2.129' || !Array.isArray(receipt.files) ||
      receipt.files.map(item=>item.path).sort().join(',') !== nativeNames.join(',')) throw Error('Invalid NoteCraft build receipt');
  const bundle = [];
  for (const item of receipt.files) {
    const bytes = await readFile(path.join(site,item.path));
    if (bytes.length !== item.bytes || hash(bytes) !== item.sha256) throw Error('Invalid NoteCraft artifact '+item.path);
    bundle.push({name:'webos/native/'+item.path,bytes});
  }
  const names = ['app.mjs','webos/app.css','webos/index.html','webos/native.css','webos/frame.mjs',
    'webos/notebook.mjs','webos/archive-worker.mjs','webos/vendor/fflate.mjs','webos/vendor/fflate-LICENSE',
    'LICENSE-MIT','LICENSE-APACHE','NOTICE','ATTRIBUTION.md',
    ...git(checkout,'ls-files','assets/fonts/*OFL*.txt').split('\n').filter(Boolean)];
  for (const name of names) {
    const source = appRoot+'/'+name;
    const bytes = await readFile(path.join(root,source));
    sourceInputs.set(source,hash(bytes));
    bundle.push({name:name === 'app.mjs' ? 'index.mjs' : name,bytes});
  }
  await registerFiles('notecraft',bundle);
}
if (flags['--notebook-site']) {
  const id = 'notebook';
  const component = path.join(root,'apps',id);
  const site = path.resolve(flags['--notebook-site']);
  const receipt = JSON.parse(await readFile(path.join(site,'component-build.json'),'utf8'));
  const inventory = await readFile(path.join(component,'app.json'));
  const assets = JSON.parse(inventory).assets;
  const git = (cwd,...args) => execFileSync('git',['-C',cwd,...args],{encoding:'utf8'}).trim();
  const pin = git(root,'rev-parse','HEAD:apps/notebook');
  if (receipt.schema !== 'webos-component-build/1' || receipt.component !== id ||
      receipt.sourceCommit !== pin || pin !== git(component,'rev-parse','HEAD') ||
      receipt.sourceTree !== git(component,'rev-parse','HEAD^{tree}') ||
      receipt.inventorySHA256 !== hash(inventory) || !Array.isArray(receipt.files) ||
      receipt.files.length !== assets.length || new Set(assets).size !== assets.length) {
    throw Error('Notebook requires the exact JupyterLite package of the selected component');
  }
  sourceInputs.set('apps/notebook/app.json',hash(inventory));
  const files = [];
  for (const [index,artifact] of receipt.files.entries()) {
    if (artifact.path !== assets[index] || !safe(artifact.path)) throw Error('Invalid Notebook inventory');
    const bytes = await readFile(path.join(site,artifact.path));
    if (bytes.length !== artifact.bytes || hash(bytes) !== artifact.sha256) throw Error('Invalid Notebook asset '+artifact.path);
    files.push({name:artifact.path,bytes});
  }
  await emitBuild({
    entryPoints:{index:'apps/notebook/index.mjs'},outdir:path.join(output,'.virtual-notebook'),outExtension:{'.js':'.mjs'}
  },async built=>files.push(...built));
  await registerFiles(id,files,['index.css']);
}
if (flags['--i-success-site']) {
  const id = 'i-success';
  const appRoot = 'apps/' + id;
  const site = path.resolve(flags['--i-success-site']);
  const native = JSON.parse(await readFile(path.join(site,'component-build.json'),'utf8'));
  const git = (cwd,...args) => execFileSync('git',['-C',cwd,...args],{encoding:'utf8'}).trim();
  const checkout = path.join(root,appRoot);
  const pin = git(root,'rev-parse','HEAD:'+appRoot);
  if (native.schema !== 'webos-component-build/1' || native.component !== id ||
      native.sourceCommit !== pin || git(checkout,'rev-parse','HEAD') !== pin ||
      native.sourceTree !== git(checkout,'rev-parse','HEAD^{tree}') ||
      native.cargoLockSHA256 !== hash(await readFile(path.join(checkout,'Cargo.lock'))) ||
      native.wasmBindgen !== 'wasm-bindgen 0.2.130' || !Array.isArray(native.files) ||
      native.files.map(f => f.path).sort().join(',') !== 'THIRD-PARTY-NOTICES.txt,i_success.js,i_success_bg.wasm') {
    throw Error('I-SUCCESS requires the exact browser build of the selected component');
  }
  const bundle = [];
  for (const artifact of native.files) {
    const bytes = await readFile(path.join(site,artifact.path));
    if (bytes.length !== artifact.bytes || hash(bytes) !== artifact.sha256) throw Error('Invalid I-SUCCESS artifact '+artifact.path);
    bundle.push({name:artifact.path,bytes});
  }
  for (const [name,relative] of [
    ['index.mjs','assembly/viewer/i-success.mjs'],['index.css','assembly/viewer/i-success.css'],
    ...['LICENSE-MIT','LICENSE-APACHE','NOTICE','ATTRIBUTION.md'].map(name => [name,appRoot+'/'+name])
  ]) {
    const bytes = await readFile(path.join(root,relative));
    sourceInputs.set(relative,hash(bytes));
    bundle.push({name,bytes});
  }
  await registerFiles(id,bundle,['index.css']);
}
// The three DRAKON generators are independently installable browser apps.
for (const id of ['drakon-python','drakon-javascript','drakon-bash']) {
  const appRoot = 'apps/'+id;
  const manifest = appRoot+'/webos-files.json';
  let bytes;
  try { bytes = await readFile(path.join(root,manifest)); }
  catch (error) { if (error.code === 'ENOENT') continue; throw error; }
  sourceInputs.set(manifest,hash(bytes));
  const names = JSON.parse(bytes);
  if (!Array.isArray(names) || new Set(names).size !== names.length ||
      names.some(name => !safe(name) || !/^(app[.]mjs|language[.]mjs|icon[.]svg|runtime\/[a-zA-Z0-9./_-]+)$/.test(name)) ||
      !['app.mjs','language.mjs','icon.svg'].every(name=>names.includes(name))) throw Error('Invalid '+id+' inventory');
  const bundle = [];
  for (const name of names) {
    const relative = appRoot+'/'+name;
    const content = await readFile(path.join(root,relative));
    sourceInputs.set(relative,hash(content));
    bundle.push({name:name === 'app.mjs' ? 'index.mjs' : name,bytes:content});
    if (name === 'icon.svg') await put('assets/desktop/'+id+'.svg',content);
  }
  await registerFiles(id,bundle);
}
// One independently pinned Narrator repository supplies the window and speech API.
{
  const appRoot = 'apps/narrator';
  execFileSync(process.execPath, ['scripts/inventory.mjs', '--check'], { cwd: path.join(root, appRoot) });
  const manifest = appRoot + '/webos-files.json';
  const bytes = await readFile(path.join(root, manifest));
  sourceInputs.set(manifest, hash(bytes));
  const names = JSON.parse(bytes);
  if (!Array.isArray(names) || !names.includes('app.mjs') || !names.includes('index.html') ||
      new Set(names).size !== names.length || names.includes('index.mjs') ||
      names.some(n => !safe(n) || !/^[a-zA-Z0-9_./-]+$/.test(n))) throw Error('Invalid Narrator inventory');
  const bundle = [{ name: 'index.mjs', bytes: Buffer.from("export * from './app.mjs';\n") }];
  for (const name of names) {
    const relative = appRoot + '/' + name;
    const content = await readFile(path.join(root, relative));
    sourceInputs.set(relative, hash(content));
    bundle.push({ name, bytes: content });
    if (name === 'icon.svg') await put('assets/desktop/narrator.svg', content);
  }
  await registerFiles('narrator', bundle);
}
await put('assets/desktop/apps.json',JSON.stringify({version:'codi-public-apps/2',hostAPI:2,apps}));
const speechInputs=flags['--speech-inputs'];
let speechReceipt;
if(speechInputs){
  const engineRoot=path.join(root,'engines/speech');
  const pin=execFileSync('git',['-C',root,'rev-parse','HEAD:engines/speech'],{encoding:'utf8'}).trim();
  const checkedOut=execFileSync('git',['-C',engineRoot,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
  if(checkedOut!==pin)throw Error('Speech engine must match the assembly pin');
  const destination=path.join(output,'assets/speech');
  execFileSync(process.execPath,[path.join(engineRoot,'scripts/build.mjs'),'--inputs',path.resolve(speechInputs),'--output',destination]);
  const receipt=await readFile(path.join(destination,'component-build.json'));
  speechReceipt={sourceCommit:pin,receiptSHA256:hash(receipt)};
}
await put('viewer-profile.json',JSON.stringify({version:'webos-existing-viewer/1',apps:apps.map(a=>a.id),guest:terminalEnabled,...(accountGuestHome?{accountGuestHome:true}:{}),speech:!!speechReceipt,offlineCache:false}));
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
  const trunkSite = id==='photocraft'||graphicsEngines.some(app=>app.id===id && !app.externalModule);
  let total=0;const seen=new Set();
  for(const file of receipt.files){
    if(!safe(file.path)||seen.has(file.path)||file.path==='component-build.json'||!Number.isSafeInteger(file.bytes)||file.bytes<0)throw Error('Invalid '+id+' engine path/size');
    seen.add(file.path);const bytes=await readFile(path.join(site,file.path));
    if(bytes.length!==file.bytes||hash(bytes)!==file.sha256)throw Error(id+' engine input hash mismatch');
    if(trunkSite&&file.path==='.htaccess')continue;
    if(trunkSite&&file.path==='index.html'){
      const html=bytes.toString('utf8');
      const scripts=[...html.matchAll(/<script type="module">([\s\S]*?)<\/script>/g)];
      if(scripts.length!==1)throw Error(`Expected one generated ${id} module bootstrap`);
      const [inline,bootstrap]=scripts[0];
      const name='webos-boot-'+hash(bootstrap).slice(0,16)+'.mjs';
      if(receipt.files.some(file=>file.path===name))throw Error(`${id} bootstrap path collision`);
      const transformed=html.replace(inline,'<script type="module" src="./'+name+'"></script>');
      await put(id+'/'+name,bootstrap);
      await put(id+'/index.html',transformed);
      total+=Buffer.byteLength(transformed)+Buffer.byteLength(bootstrap);
      continue;
    }
    await put(id+'/'+file.path,bytes);total+=bytes.length;
  }
  await put(id+'/component-build.json',receiptBytes);
  additionalReceipts[id+'Engine']={sourceCommit:receipt.sourceCommit,bytes:total,receiptSHA256:hash(receiptBytes),
    ...(graphicsEngines.some(app=>app.id===id)?{sourceTree:receipt.sourceTree}:{})};
}
// No backend/package/credential state is included in public output.
const receipt={schema:'webos-existing-viewer-build/1',engine:{sourceCommit:engine.sourceCommit,bytes:engineBytes,receiptSHA256:hash(await readFile(path.join(wordcraft,'component-build.json')))},
  ...(photoTest||graphicsEngines.some(app=>app.review)?{developmentOnly:true}:{}),
  ...(pdfEngine?{pdfcraftEngine:{sourceCommit:pdfEngine.sourceCommit,bytes:pdfEngineBytes,receiptSHA256:hash(await readFile(path.join(pdfcraft,'component-build.json')))}}:{}),
  ...(speechReceipt?{speechEngine:speechReceipt}:{}),...additionalReceipts,sourceInputs:[...sourceInputs].map(([path,sha256])=>({path,sha256})),apps:apps.map(a=>a.id),qualification:'Source-assembled candidate. Real viewer/browser/account acceptance remains separate; WordCraft engine is a verified prebuilt input.'};
await put('viewer-build.json',JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({output,apps:receipt.apps,sourceInputs:sourceInputs.size,engineBytes,engineSourceCommit:engine.sourceCommit,guest:terminalEnabled,sourceAssembled:true}));
