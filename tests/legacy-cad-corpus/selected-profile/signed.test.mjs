// Real desktop commands, production Workers/native OCC, signed My files.
// No native authoring seeds, private wizard, provider, or fake successful reply.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {harness,cmd,launch,frame,save,sync,reopen,plane,append,requiredPins,verifyRuntime,discover,intent,capture,disk} from './helpers.mjs';
import {openKeepEditing,closePending} from './lifecycle.mjs';
requiredPins();
const receipt={result:'RUNNING',cadSource:process.env.CODI_SOURCE,desktopSource:'478970d72',scope:'Actual signed public selected-profile authoring, normal My files persistence and real window lifecycle; no full CAD1 or dependent-edit qualification',authoringSeeds:false,fakeSuccessfulReplies:false,rows:[]},h=await harness(),user='selected'+Date.now(),path='/selected-circle.jsketcher.json';
try{
 let p=await h.login(true,user);await launch(p);receipt.assets=await verifyRuntime(p);
 const empty=await plane(p,'XY',0),faceId=empty.faceId,pointId=await append(p,faceId,'Point',{x:0,y:0}),circleId=await append(p,faceId,'Circle',{c:{x:.0005,y:0},r:10});
 const before=await capture(p,faceId),d=await discover(p,faceId);assert.equal(d.result.regions.length,1);const row=d.result.regions[0];assert.equal(row.support,'supported');assert.equal(row.reason,null);
 const descriptor=JSON.parse(row.regionId.slice('sketch-region:'.length));assert.deepEqual(descriptor,{faceId,outer:[faceId+'/'+circleId],holes:[]});assert.deepEqual(await capture(p,faceId),before);
 receipt.rows.push({label:'public empty plane + ordinary Circle + ignored Point + genuine region discovery',faceId,pointId,circleId,descriptor,sourceDigest:d.result.sourceDigest});
 for(const change of[{revision:'stale'},{bodyPolicy:'union'},{engine:'smlib'},{depth:0}]){const captured=await capture(p,faceId);await assert.rejects(cmd(p,'create-selected-extrusion',{...intent(d,faceId),...change}));assert.deepEqual(await capture(p,faceId),captured);}
 receipt.rows.push({label:'stale and invalid command refusal preserves prior native/source/history/streams'});
 receipt.rows.push(await openKeepEditing(p,faceId));
 const current=await discover(p,faceId),created=await cmd(p,'create-selected-extrusion',intent(current,faceId));assert.equal(created.sourceFaceId,faceId);assert.equal(created.regionId,row.regionId);assert.equal(created.persistence,'volatile-workspace');
 const accepted=await capture(p,faceId),measurements=disk(accepted);assert.equal(measurements.id,created.outputId);assert.equal(accepted.native.source,before.native.source);
 const history=JSON.parse(accepted.native.history).history,features=history.filter(x=>x.type==='WORKER_SELECTED_PROFILE_EXTRUDE_V2');assert.equal(features.length,1);const params=features[0].params;
 assert.deepEqual(Object.keys(params).sort(),['version','unit','engine','engineRevision','featureId','faceId','regionId','depth','bodyPolicy'].sort());assert.equal(params.faceId,faceId);assert.equal(params.regionId,row.regionId);assert.equal(params.engineRevision,d.info.engineRevision);assert.equal(params.depth,5);
 receipt.rows.push({label:'public selected extrusion after canceled attempt; exact nine-field intent and independently measured disk',created,measurements});
 const rediscovered=await discover(p,faceId);assert.deepEqual(rediscovered.result.regions,d.result.regions);assert.equal((await capture(p,faceId)).native.source,before.native.source);
 const saved=await save(p,path);receipt.serverHash=saved.server;assert.equal(saved.local,saved.server);const other=await h.login(true,user+'b');
 const denied=await other.evaluate(async path=>{try{await(await serverFileContext()).files.read(path.slice(1));return{read:true};}catch(e){return{status:e.status};}},path);assert.equal(denied.status,404);receipt.rows.push({label:'normal My files Save/server sync and foreign synthetic account denial',serverHash:saved.server,denial:denied.status});
 await h.retire(p);p=await h.login(false,user);await p.bringToFront();await reopen(p,path);await verifyRuntime(p);
 const reopened=await capture(p,faceId);assert.deepEqual(disk(reopened),measurements);assert.equal(reopened.native.source,accepted.native.source);assert.equal(reopened.native.history,accepted.native.history);assert.deepEqual((await discover(p,faceId)).result.regions,d.result.regions);assert.equal((await sync(p,path)).server,saved.server);
 receipt.rows.push({label:'fresh Files reopen preserves source bytes, selected-region identity, exact authored intent and native measurements'});
 receipt.rows.push(await closePending(p,faceId));assert.equal((await sync(p,path)).server,saved.server);
 await h.retire(p);p=await h.login(false,user);await p.bringToFront();await reopen(p,path);await verifyRuntime(p);assert.deepEqual(disk(await capture(p,faceId)),measurements);assert.equal((await capture(p,faceId)).native.history,accepted.native.history);assert.equal((await sync(p,path)).server,saved.server);
 receipt.rows.push({label:'fresh Files recovery after Close/late native reply preserves last saved intent and server hash'});receipt.result='PASS';
 console.log('PASS signed selected-profile workflow',JSON.stringify(receipt));
}catch(error){receipt.result='FAIL';receipt.error={message:error.message,stack:error.stack,details:error.details};throw error;}
finally{if(process.env.CODI_RECEIPT)await writeFile(process.env.CODI_RECEIPT,JSON.stringify(receipt,null,2)+'\n');await h.close();}
