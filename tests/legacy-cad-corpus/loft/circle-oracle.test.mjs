// Analytic-oracle controls only; these do not fabricate a passing native result.
import test from 'node:test';import assert from 'node:assert/strict';
import {circleLoftFromSaved} from './circle-oracle.mjs';
function model(r0,r1,height,phase=0){
  return{project:{model:{history:[{type:'WORKER_SELECTED_PROFILE_LOFT_V1',params:{version:1,unit:'millimeter',engine:'occ',engineRevision:'fixture-only-no-native-runtime',featureId:3,construction:'ruled-solid',bodyPolicy:'separate',sections:[0,1].map(i=>({faceId:'plane'+i,regionId:'opaque-region'+i,seam:{kind:'circle-angle',curveId:'circle'+i,angleRadians:i?phase:0,reversed:false}}))}}]},sketches:[r0,r1].map((r,i)=>({id:'plane'+i,data:{objects:[{id:'circle'+i,type:'Circle',role:null,stage:0,data:{c:{x:0,y:0},r}}],metadata:{boundaryFrame:{origin:[0,0,i===0?0:height],x:[1,0,0],y:[0,1,0],z:[0,0,1]}}}}))}};
}
test('cylinder, conical frustum and quarter-twisted correspondence have independent analytic volumes',()=>{
  for(const [r0,r1,h,phase,multiple]of [[2,2,10,0,40],[2,4,30,0,280],[2,4,30,Math.PI/2,200]]){
    const result=circleLoftFromSaved(model(r0,r1,h,phase),3);
    assert(Math.abs(result.volumeMM3-multiple*Math.PI)<1e-10);
    // Independent composite midpoint integration of ruled section coordinates.
    let sum=0;const n=10000;
    for(let i=0;i<n;i++){const t=(i+.5)/n,x=(1-t)*r0+t*r1*Math.cos(phase),y=t*r1*Math.sin(phase);sum+=Math.PI*(x*x+y*y)*h/n;}
    assert(Math.abs(sum-result.volumeMM3)<1e-5);
    assert.equal(result.probes.filter(p=>p.classification==='boundary').length,2);
  }
});
test('reversing section elevation preserves physical volume and bounds',()=>{
  const positive=circleLoftFromSaved(model(2,4,30),3),negative=circleLoftFromSaved(model(2,4,-30),3);
  assert.equal(positive.volumeMM3,negative.volumeMM3);
  assert.deepEqual(negative.boundsMM,{min:[-4,-4,-30],max:[4,4,0]});
});
test('wrong source identity, unsupported frames, noncoaxial sections and collapse are refused',()=>{
  for(const alter of [m=>m.project.sketches[1].data.objects[0].id='wrong',m=>m.project.sketches[1].data.metadata.boundaryFrame.x=[0,1,0],m=>m.project.sketches[1].data.objects[0].data.c.x=1,m=>m.project.sketches[1].data.objects[0].data.r=0,m=>m.project.model.history[0].params.sections[1].seam.angleRadians=Math.PI,m=>m.project.model.history[0].params.sections[1].seam.reversed=true,m=>m.project.sketches[1].data.metadata.boundaryFrame.origin[2]=0]){
    const m=model(2,4,30);alter(m);assert.throws(()=>circleLoftFromSaved(m,3));
  }
});
