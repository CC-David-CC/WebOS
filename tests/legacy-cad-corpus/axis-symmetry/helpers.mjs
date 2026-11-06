import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export {harness,cmd,launch,frame,sync,save,reopen,nativeOnly} from '../numeric-expressions/helpers.mjs';
export {inspect,append,plane,point,closeEnough,check} from '../signed-distance/helpers.mjs';
export {preserved} from '../line-relations/helpers.mjs';
import {capture as baseCapture} from '../line-relations/helpers.mjs';
import {cmd,frame} from '../numeric-expressions/helpers.mjs';
import {inspect,point,closeEnough} from '../signed-distance/helpers.mjs';
// The inherited oracle supports two concurrent inspections. This lane has
// three faces, so retain its exact oracles while respecting that public cap.
export async function capture(p,faces){
 const inspected=[];for(const id of faces)inspected.push(await inspect(p,id));
 const state=await baseCapture(p,[]);state.inspected=inspected;
 state.native.sketches=await(await frame(p)).evaluate(ids=>ids.map(id=>({id,source:__CAD_APP.sketchStorageService.getSketchData(id)})),faces);
 return state;
}
export function requireReviewedPins(){
 for(const name of['CODI_EXPECTED_APP_SHA','CODI_EXPECTED_SKETCH_SHA','CODI_EXPECTED_PROJECT_SHA'])assert.match(process.env[name]||'',/^[a-f0-9]{64}$/,name+' must come from parent-reviewed combined runtime');
 assert.ok(process.env.CODI_SOURCE,'Reviewed combined CAD source required');
 assert.equal(new URL(process.env.CODI_TEST_URL).port,'20403','Use the new isolated fixture');
}
export async function verifyRuntime(p){
 const origin=new URL((await frame(p)).url()),cookies=await p.cookies(origin.href);
 // Driver-side hashing; synthetic account cookies stay only in memory.
 async function read(url){const response=await fetch(url,{headers:{cookie:cookies.map(c=>c.name+'='+c.value).join('; ')}});assert.equal(response.status,200,'Pinned runtime asset');return Buffer.from(await response.arrayBuffer());}
 const appUrl=new URL('static/index.bundle.js',origin),app=await read(appUrl),sha=b=>createHash('sha256').update(b).digest('hex'),assets={app:{url:appUrl.href,sha256:sha(app)}};
 assert.equal(assets.app.sha256,process.env.CODI_EXPECTED_APP_SHA);
 for(const [key,pattern,expected] of[['sketch',/sketch-solver\.[a-f0-9]+\.js/g,process.env.CODI_EXPECTED_SKETCH_SHA],['project',/project-validator\.[a-f0-9]+\.js/g,process.env.CODI_EXPECTED_PROJECT_SHA]]){
  const names=[...new Set(app.toString().match(pattern))];assert.equal(names.length,1,key+' production Worker reference');
  const url=new URL('static/'+names[0],origin),bytes=await read(url);assets[key]={url:url.href,sha256:sha(bytes)};assert.equal(assets[key].sha256,expected);
 }return assets;
}
export async function apply(p,faceId,ids){const info=await inspect(p,faceId);return cmd(p,'apply-closed-sketch-line-relation',{revision:info.revision,faceId,kind:'axis-symmetry',ids});}
export function receipt(r,ids,existing=false){assert.equal(r.changed,!existing);assert.equal(r.authoredUndo,!existing);assert.equal(r.relation.kind,'axis-symmetry');assert.equal(r.relation.typeId,'AxisSymmetry');assert.deepEqual(r.relation.objects,ids);assert.equal(r.relation.existing,existing);assert.ok(['accepted','redundant'].includes(r.relation.status));if(existing)assert.equal(r.relation.status,'redundant');assert.ok(Number.isSafeInteger(r.relation.stage)&&r.relation.stage>=0);assert.ok(Number.isSafeInteger(r.relation.index)&&r.relation.index>=0);}
export async function reflected(p,faceId,ids){
 const info=await inspect(p,faceId),[P,Q,A,B]=[point(info,ids[0]),point(info,ids[1]),point(info,ids[2]+':A'),point(info,ids[2]+':B')];assert.equal(info.objects.find(o=>o.id===ids[2])?.type,'Segment');
 const dx=B.x-A.x,dy=B.y-A.y,length=Math.hypot(dx,dy);assert.ok(length>1e-9,'Live nonzero axis');
 const projection=((P.x-A.x)*dx+(P.y-A.y)*dy)/(length*length),foot={x:A.x+projection*dx,y:A.y+projection*dy},expected={x:2*foot.x-P.x,y:2*foot.y-P.y};
 closeEnough(Q.x,expected.x,'independent reflected X');closeEnough(Q.y,expected.y,'independent reflected Y');return{points:[P,Q],axis:[A,B],length,expected,boundaryFrame:info.boundaryFrame};
}
