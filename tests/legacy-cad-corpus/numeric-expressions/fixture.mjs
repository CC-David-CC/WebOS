import assert from 'node:assert/strict';import {cmd,save,initialSource} from './helpers.mjs';
// Publicly build actual geometry. The first named/formula bindings below are
// explicit test-only edits of our own native file, followed by normal Files open.
export async function seed(p,path){
 let info=await cmd(p,'inspect-rectangle-creation');const main=await cmd(p,'create-rectangle-sketch',{revision:info.revision,unit:'millimeter',origin:[0,0],width:100,height:50,depth:0});
 info=await cmd(p,'inspect-worker-features');await cmd(p,'create-worker-extrusion',{revision:info.revision,...info.extrusionCandidates.find(c=>c.faceId===main.faceId&&c.regionId===main.regionId),depth:20});
 info=await cmd(p,'inspect-rectangle-creation');const local=await cmd(p,'create-rectangle-sketch',{revision:info.revision,unit:'millimeter',origin:[200,0],width:30,height:10,depth:0});
 const base=JSON.parse((await save(p,'/numeric-base.jsketcher.json')).text);assert.equal(base.format,'codi-jsketcher-project');assert.equal(base.version,2);base.project.model.expressions=initialSource;const extrusion=base.project.model.history.find(h=>h.type==='WORKER_RECTANGLE_EXTRUDE_V1');assert.ok(extrusion);extrusion.params.length='D';
 for(const [id,width,height,constants] of [[main.faceId,'W','H',''],[local.faceId,'W','LH','W = 30\nLH = 5 * 2']]){const sketch=base.project.sketches.find(s=>s.id===id).data;sketch.constants=constants;const dimensions=sketch.stages[0].constraints.filter(c=>c.typeId==='SegmentLength');assert.equal(dimensions.length,2);for(const c of dimensions)c.constants.length=c.objects[0]==='rect-0'?width:height;}
 await p.evaluate(async({path,base})=>{const f=(await mirrorFileContext()).files;await f.write(path,JSON.stringify(base),null);await f.sync();},{path,base});return {ids:[main.faceId,local.faceId]};
}
