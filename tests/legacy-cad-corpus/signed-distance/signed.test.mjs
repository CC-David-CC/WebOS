import assert from 'node:assert/strict';
import {harness,cmd,launch,sync,save,reopen,capture,plane,append,apply,check,inspect,point,accepted,preserved,nativeOnly,closeEnough} from './helpers.mjs';
import {cancelThenApply,closePending} from './lifecycle.mjs';
const h=await harness(),user='sdist'+Date.now(),path='/signed-distance.jsketcher.json',rows=[];
try{
 let p=await h.login(true,user);await launch(p);console.log('TEST_ACCOUNTS',user,user+'b','FILE',path,'SETUP public commands only; no native/formula seed');
 const xy=await plane(p,'XY',0),face=xy.faceId,ids={};
 for(const [name,x,y] of [['a',0,0],['b',3,4],['c',9,8],['ya',30,0],['yb',32,3],['za',40,0],['zb',42,3],['pa',60,0],['pb',63,4],['ca',100,0],['cb',103,4]])ids[name]=await append(p,face,'Point',{x,y});
 ids.datum=await append(p,face,'Segment',{a:{x:70,y:0},b:{x:73,y:4}},'construction');ids.circle=await append(p,face,'Circle',{c:{x:90,y:20},r:5});
 const xz=await plane(p,'XZ',17);ids.xza=await append(p,xz.faceId,'Point',{x:3,y:4});ids.xzb=await append(p,xz.faceId,'Point',{x:8,y:9});
 const faces=[face,xz.faceId],baseline=await save(p,path);
 async function relation(label,faceId,axis,targets,distance,status){const r=await apply(p,faceId,axis,targets,distance);accepted(r,axis,targets,distance,status);await check(p,faceId,axis,targets,distance);rows.push({label,receipt:r});return r;}
 const firstRevision=(await inspect(p,face)).revision;
 await relation('positive X',face,'x',[ids.a,ids.b],12);
 await relation('duplicate authored redundant X',face,'x',[ids.a,ids.b],12,'redundant');
 await relation('reversed ordered points',face,'x',[ids.b,ids.a],-12);
 await relation('dependent second X',face,'x',[ids.b,ids.c],3);
 let acceptedState=await capture(p,faces);
 await assert.rejects(cmd(p,'apply-closed-sketch-signed-distance',{revision:firstRevision,faceId:face,axis:'x',ids:[ids.a,ids.b],distance:2}));assert.deepEqual(await capture(p,faces),acceptedState);
 const bad=[['contradictory X cycle',{axis:'x',ids:[ids.a,ids.c],distance:99}],['missing point',{axis:'x',ids:[ids.a,'missing-point'],distance:1}],['segment not point',{axis:'y',ids:[ids.a,ids.datum],distance:1}],['wrong direction type',{axis:'projected',ids:[ids.a,ids.b,ids.c],distance:1}],['same point',{axis:'x',ids:[ids.a,ids.a],distance:0}],['wrong arity',{axis:'x',ids:[ids.a,ids.b,ids.datum],distance:1}],['unknown axis',{axis:'z',ids:[ids.a,ids.b],distance:1}],['not numeric',{axis:'x',ids:[ids.a,ids.b],distance:'12'}],['outside public bound',{axis:'x',ids:[ids.a,ids.b],distance:1000001}],['cross-face point',{axis:'y',ids:[ids.a,ids.xza],distance:1}]];
 for(const [label,request] of bad){const info=await inspect(p,face);await assert.rejects(cmd(p,'apply-closed-sketch-signed-distance',{revision:info.revision,faceId:face,...request}));const after=await capture(p,faces);preserved(after,acceptedState);acceptedState=after;rows.push({label,refused:true,preserved:true});assert.equal((await sync(p,path)).server,baseline.server);}
 await relation('negative Y',face,'y',[ids.ya,ids.yb],-7);
 await relation('zero X is a valid relation',face,'x',[ids.za,ids.zb],0);
 await relation('circle center target',face,'y',[ids.circle+':C',ids.ya],-5);
 await relation('projection with live datum',face,'projected',[ids.pa,ids.pb,ids.datum],2);
 const beforeDatum=await capture(p,faces),oldDatum=await inspect(p,face);const oldA=point(oldDatum,ids.datum+':A'),oldB=point(oldDatum,ids.datum+':B');assert.ok(Math.abs(oldB.x-oldA.x)>1);
 await relation('rotate datum: endpoint X=0',face,'x',[ids.datum+':A',ids.datum+':B'],0);
 await relation('rotate datum: endpoint Y=10',face,'y',[ids.datum+':A',ids.datum+':B'],10);
 await check(p,face,'projected',[ids.pa,ids.pb,ids.datum],2);const live=await inspect(p,face);closeEnough(point(live,ids.pb).y-point(live,ids.pa).y,2,'vertical datum produces live Y projection');
 const afterDatum=await capture(p,faces);for(let i=0;i<2;i++){const j=await cmd(p,'inspect-authored-edits');await cmd(p,'travel-authored-edit',{revision:j.revision,direction:'undo'});}assert.deepEqual((await capture(p,faces)).native,beforeDatum.native);for(let i=0;i<2;i++){const j=await cmd(p,'inspect-authored-edits');await cmd(p,'travel-authored-edit',{revision:j.revision,direction:'redo'});}assert.deepEqual((await capture(p,faces)).native,afterDatum.native);
 await relation('XZ local negative X',xz.faceId,'x',[ids.xza,ids.xzb],-4);await relation('XZ local positive Y',xz.faceId,'y',[ids.xza,ids.xzb],6);
 // Existing point edit no-op remains distinct from dimension redundancy.
 const beforeNoop=await capture(p,faces),info=await inspect(p,face),same=point(info,ids.cb);const noOp=await cmd(p,'edit-closed-sketch-point',{revision:info.revision,faceId:face,id:same.id,x:same.x,y:same.y});assert.equal(noOp.changed,false);assert.deepEqual(await capture(p,faces),beforeNoop);
 assert.equal((await sync(p,path)).server,baseline.server);const won=await cancelThenApply(p,faces,{faceId:face,axis:'x',ids:[ids.ca,ids.cb],distance:8});accepted(won,'x',[ids.ca,ids.cb],8);await check(p,face,'x',[ids.ca,ids.cb],8);rows.push({label:'genuine candidate canceled by normal Open/Keep editing; next public apply accepted',passed:true});
 const final=await capture(p,faces),saved=await save(p,path),native=JSON.parse(saved.text);for(const s of final.native.sketches)assert.deepEqual(native.project.sketches.find(x=>x.id===s.id).data,JSON.parse(s.source));
 for(const row of rows.filter(r=>r.receipt)){const d=row.receipt.dimension,sketch=native.project.sketches.find(s=>s.id===row.receipt.faceId)?.data;assert.ok(sketch,'Saved owning face');assert.ok(sketch.stages.flatMap(s=>s.constraints).some(c=>c.typeId===d.typeId&&JSON.stringify(c.objects)===JSON.stringify(d.objects)),'Native dimension retains actual ordered IDs');}
 await closePending(p,{faceId:face,axis:'y',ids:[ids.ca,ids.cb],distance:6});assert.equal((await sync(p,path)).server,saved.server);
 const other=await h.login(true,user+'b'),denied=await other.evaluate(async path=>{try{await(await serverFileContext()).files.read(path.slice(1));return 'read succeeded';}catch(e){return e.status;}},path);assert.ok([403,404].includes(denied));await h.retire(p);p=await h.login(false,user);await p.bringToFront();await reopen(p,path);await nativeOnly(p);const fresh=await capture(p,faces);assert.deepEqual(fresh.native.sketches,final.native.sketches);await check(p,face,'projected',[ids.pa,ids.pb,ids.datum],2);await check(p,xz.faceId,'x',[ids.xza,ids.xzb],-4);await check(p,xz.faceId,'y',[ids.xza,ids.xzb],6);assert.equal((await sync(p,path)).server,saved.server);
 console.log('SEED_SERVER_HASH',baseline.server,'FINAL_SERVER_HASH',saved.server);console.log('ROWS',JSON.stringify(rows));console.log('PASS actual signed public X/Y/projected relations, ordered sign/zero/redundancy, endpoint/circle-center/local axes, live datum, refusal/stale/travel/noop, genuine candidate cancellation/Close, normal Save/sync/account denial/fresh Files reopen; no seeds');
}finally{await h.close();}
