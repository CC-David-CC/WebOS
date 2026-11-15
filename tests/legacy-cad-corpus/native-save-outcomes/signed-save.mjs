// Genuine public authoring and ordinary sequential Save/Open only.
// No storage/geometry doubles, private setters, forced Close or filesystem race.
import a from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
import {harness,sha} from '../sweep/signed-harness.mjs';
import {author,edit} from '../step-shared/signed-author.mjs';
import {expected,checkMetrics,checkSaved,accepted,canonical} from '../step-shared/oracle.mjs';
const need=k=>{a(process.env[k],k);return process.env[k]},out=path.resolve(need('CODI_EVIDENCE')),pins=JSON.parse(fs.readFileSync(need('CODI_SIGNED_PINS'))),build=need('CODI_STEP_ENGINE_REVISION');
a.equal(pins.source,need('CODI_EXPECT_SOURCE'));a.equal(pins.desktop,need('CODI_EXPECT_DESKTOP'));a(!fs.existsSync(out));for(const key of ['CODI_TEST_URL','CODI_TEST_CDP'])a(['127.0.0.1','localhost'].includes(new URL(need(key)).hostname));fs.mkdirSync(out,{recursive:true});
const inputs=['signed-save.mjs','../sweep/signed-harness.mjs','../strict-join/oracle.mjs','../step-shared/signed-author.mjs','../step-shared/oracle.mjs'],hashes=()=>Object.fromEntries(inputs.map(f=>[f,sha(fs.readFileSync(new URL(f,import.meta.url)))])),receipt={status:'RUNNING',scope:'ordinary sequential Save and fresh-session Open of genuine parametric plate; not full Gate1',pins,sourcePins:hashes(),syntheticGeometry:false,syntheticStorage:false,crossAccountProbes:false,forcedClose:false,rows:[]};
const flush=()=>fs.writeFileSync(path.join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n'),record=(label,data={})=>{receipt.rows.push(structuredClone({label,...data}));flush();console.log(label);};
const browser=await createRequire(import.meta.url)(need('PUPPETEER_CORE_PATH')).connect({browserURL:need('CODI_TEST_CDP'),defaultViewport:null,protocolTimeout:300000}),h=await harness(browser,need('CODI_TEST_URL'),out,record);
async function pin(){const outer=await h.pinOuter({bundle:pins.outer.bundleSHA256});a.equal(outer.sha256,pins.outer.sha256);const rows=await h.pinFiles(Object.keys(pins.files));for(const row of rows)a.equal(row.sha256,pins.files[row.name]);record('Exact outer and inner source-bound runtime',{outer,files:rows});}
let binding;const file='/save-repair-plate.jsketcher.json';
async function save(label,edited){
 const before=await h.capture(binding.faceId),info=await h.command('inspect'),result=await h.command('save',{revision:info.revision,...(!info.path?{path:file}:{})});
 a.equal(result.committed,true);a.equal(result.persistence,'browser');a.equal(result.serverStatus,'not-verified');a.equal(result.path,file);a.equal(result.dirty,false);a.equal(typeof result.version,'string');a(result.version.length>0);
 a.equal(canonical(accepted(await h.capture(binding.faceId))),canonical(accepted(before)),'Save preserves authored source, history, geometry and journal');
 const after=await h.command('inspect');a.equal(after.path,file);a.equal(after.dirty,false);const saved=await h.synchronize(file),data=Buffer.from(saved.bytes),artifact=label+'.jsketcher.json';fs.writeFileSync(path.join(out,artifact),data);a.equal(sha(data),saved.sha256);const truth=expected('plate-hole',edited);const native=checkSaved(saved.native,binding,truth,build),metrics=checkMetrics(await h.command('inspect-worker-solids'),truth,build);record(label,{receipt:result,artifact,bytes:data.length,sha256:saved.sha256,native,metrics,sourcePreserved:true,after});return saved;
}
try{
 await h.login();await h.launch();await pin();record('Public New project',{created:await h.newProject()});binding=await author(h,'plate-hole',build,record);receipt.binding=binding;flush();const first=await save('initial',false);
 record('Public diameter edit',{result:await edit(h,'plate-hole',binding)});const second=await save('edited',true);a.notEqual(first.sha256,second.sha256,'Authored diameter edit changes saved native source');
 record('Fresh session Open',{result:await h.freshOpen(file)});await pin();const before=await h.command('inspect');a.equal(before.path,file);a.equal(before.dirty,false);const metrics=checkMetrics(await h.command('inspect-worker-solids'),expected('plate-hole',true),build);record('Reopened genuine geometry',{metrics});await save('reopened',true);
 receipt.status='PASS';
}catch(error){receipt.status='FAIL';receipt.error={name:error.name,message:error.message,stack:error.stack};process.exitCode=1;console.error(error.stack)}finally{await h.retire();receipt.ownedContextClosed=true;receipt.sourceHashesAfter=hashes();a.deepEqual(receipt.sourceHashesAfter,receipt.sourcePins);receipt.sharedBrowserDisconnectedOnly=true;flush();await browser.disconnect();}
