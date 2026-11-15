import assert from 'node:assert/strict';
import {canonical} from '../strict-join/oracle.mjs';
import {sameIntent} from './signed-author.mjs';

export async function workflow(h,a,record,kind){
 const b=await a.create(kind),created=await a.snapshot(b);
 await h.travel('undo');const removed=await h.capture(b.faceId);assert.equal(removed.solids.bodies.length,0);assert.equal(removed.native.history.length,2);assert.equal(removed.native.source,created.native.source);assert.equal(canonical(removed.native.sketches),canonical(created.native.sketches));assert.equal(canonical(removed.native.counters),canonical(created.native.counters));
 await h.travel('redo');sameIntent(created,await a.snapshot(b));record('Creation Undo retains both source planes; Redo retains feature/output identity',{binding:b,counters:created.native.counters});
 await a.persist(b,kind+'-baseline');
 const base=await a.snapshot(b),stale=await a.discover(b);
 await a.profileEdit(b);const profileEdited=await a.snapshot(b);
 await a.pathEdit(b,kind.startsWith('straight')?15:12);const bothEdited=await a.snapshot(b);
 assert.equal(canonical(base.native.history),canonical(bothEdited.native.history),'Source edits must replay the unchanged authored sweep suffix.');assert.equal(canonical(base.native.counters),canonical(bothEdited.native.counters));
 await h.travel('undo');sameIntent(profileEdited,await a.snapshot(b));await h.travel('undo');sameIntent(base,await a.snapshot(b));await h.travel('redo');sameIntent(profileEdited,await a.snapshot(b));await h.travel('redo');sameIntent(bothEdited,await a.snapshot(b));
 record('Profile and path source edits replay same suffix; normal LIFO UndoRedo',{binding:b,before:base.observation,profileEdited:profileEdited.observation,bothEdited:bothEdited.observation});
 const request=d=>({revision:d.revision,version:1,unit:'millimeter',engine:'occ',engineRevision:b.engineRevision,faceId:b.faceId,regionId:b.regionId,pathFaceId:b.pathFaceId,pathCurves:b.pathCurves,transport:'corrected-frenet',bodyPolicy:'separate'});
 await a.refuse(b,'Stale discovery refuses without accepted mutation',()=>h.command('create-worker-sweep',request(stale)),{name:'AbortError'});
 if(b.unsupportedPathId){const d=await a.discover(b);await a.refuse(b,'Actual advertised unsupported Circle path refuses explicitly',()=>h.command('create-worker-sweep',{...request(d),pathCurves:[{curveId:b.unsupportedPathId,reversed:false}]}),{code:'SWEEP_UNSUPPORTED_PATH'});}
 if(kind==='straight-disk'){
  const i=await h.inspect(b.pathFaceId),end=i.points.filter(p=>p.parentId===b.pathId&&p.y===15);assert.equal(end.length,1);
  await a.refuse(b,'Tilted current source path refuses native non-normal attachment',()=>h.command('edit-closed-sketch-points',{revision:i.revision,faceId:b.pathFaceId,points:[{id:end[0].id,x:1,y:15}]}),{code:'SWEEP_PROFILE_NOT_NORMAL'});
  assert(typeof b.initialProfileBuild==='string'&&b.initialProfileBuild!==b.engineRevision);const current=await a.discover(b);
  await a.refuse(b,'Recorded old build explicitly lacks sweep capability',()=>h.command('create-worker-sweep',{...request(current),engineRevision:b.initialProfileBuild}),{code:'UNSUPPORTED_SWEEP_BUILD'});
 }
 await a.persist(b,kind+'-source-edited');const reopenedBaseline=await a.snapshot(b);
 // A fresh normal Open resets only the session journal. Re-edit the actual path.
 await a.pathEdit(b,kind.startsWith('straight')?20:14);const reopenedEdited=await a.snapshot(b);await h.travel('undo');sameIntent(reopenedBaseline,await a.snapshot(b));await h.travel('redo');sameIntent(reopenedEdited,await a.snapshot(b));
 await a.persist(b,kind+'-reopened-reedit');record('Fresh Open supports actual path re-edit and normal UndoRedo',{binding:b,observation:reopenedEdited.observation});
 return b;
}
