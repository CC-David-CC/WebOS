// Reuse qualified login/public-command/native Save/Open/custody observations.
// No model/history writer, source injection or fabricated successful output.
import assert from'node:assert/strict';
import{harness as existingHarness,sha}from'../source-bound-pattern/harness.mjs';
import{canonical}from'../source-bound-pattern/oracle.mjs';
export{sha,canonical};
export async function harness(browser,base,out,record){
 const h=await existingHarness(browser,base,out,record),cmd=h.command;
 async function inspect(faceId){const i=await h.inspect(faceId);assert(Array.isArray(i.dimensionTargets),'Existing-dimension discovery unavailable in this runtime');assert.equal(i.dimensionTargets.length,i.constraints.length);for(const[r,c]of i.dimensionTargets.map((r,n)=>[r,i.constraints[n]])){assert.equal(r.stage,c.stage);assert.equal(r.index,c.index);assert.equal(r.typeId,c.typeId);assert.equal(canonical(r.objects),canonical(c.objects));if(r.canEdit||r.canRemove){assert.equal(r.canEdit,true);assert.equal(r.canRemove,true);assert.equal(r.unit,'millimeter');assert(typeof r.constraintId==='string'&&r.constraintId.length>0&&r.constraintId.length<=4096);assert(typeof r.resolvedValue==='number'&&Number.isFinite(r.resolvedValue)&&r.resolvedValue>0);assert.equal(r.reason,null);}else{assert.equal(r.constraintId,null);assert.equal(r.canEdit,false);assert.equal(r.canRemove,false);assert(typeof r.reason==='string'&&r.reason.length>0);}}return i;}
 const one=(rows,label)=>{assert.equal(rows.length,1,'Expected one '+label);return rows[0];};
 async function target(faceId,predicate){const info=await inspect(faceId);return{info,row:one(info.dimensionTargets.filter(predicate),'discovered driving dimension')};}
 async function edit(faceId,row,value,info){const current=info||await inspect(faceId);return cmd('edit-closed-sketch-dimension',{revision:current.revision,faceId,constraintId:row.constraintId,value});}
 async function remove(faceId,row,info){const current=info||await inspect(faceId);return cmd('remove-closed-sketch-dimension',{revision:current.revision,faceId,constraintId:row.constraintId});}
 async function append(faceId,kind,data,role=null){const before=await inspect(faceId),ids=new Set(before.objects.map(o=>o.id));await cmd('append-sketch-primitive',{revision:before.revision,faceId,kind,role,stage:0,data});const after=await inspect(faceId);return one(after.objects.filter(o=>!ids.has(o.id)&&o.type===kind),'actual appended '+kind);}
 async function plane(){const i=await cmd('inspect-sketch-creation');return cmd('create-empty-sketch-plane',{revision:i.revision,unit:'millimeter',plane:'XY',depth:0});}
 async function diameter(faceId,id,value){const i=await inspect(faceId);return cmd('apply-closed-sketch-diameter',{revision:i.revision,faceId,id,diameter:value});}
 const admission=(info,row)=>one(info.constraints.filter(c=>c.stage===row.stage&&c.index===row.index),'read-only admission observation').admission.state;
 return{...h,inspect,target,edit,remove,append,plane,diameter,admission,one};
}
