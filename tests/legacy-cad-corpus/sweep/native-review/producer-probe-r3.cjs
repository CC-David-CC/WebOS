function runTest(runtimePins){
const assert=require('node:assert/strict'),fs=require('node:fs'),rows=[],pi=Math.PI,I=[0,0,0,1,0,0,0,1,0,0,0,1],XZ=[0,0,0,1,0,0,0,0,1,0,-1,0],Q=[10,0,0,1,0,0,0,0,-1,0,1,0],QR=[0,10,0,0,1,0,0,0,1,1,0,0];
const poly=p=>[2,p.length,...p.flat()],face=(loops,f=I)=>[1,...f,loops.length,...loops.flat()],rect=poly([[-2,-.5],[2,-.5],[2,.5],[-2,.5]]),circle=[1,0,0,2],annulus=[circle,[1,0,0,1]],line=(rev=0)=>[1,0,...XZ,1,0,0,0,0,10,rev],arc=(a=[10,0],b=[0,10],rev=0)=>[1,0,...I,1,1,...a,...b,0,0,rev];
const count=()=>Module._OwnedShapeNamesV2(),query=(method,name)=>{const n=str2C(name);try{globalThis.__OCI_EXCHANGE_VAL=null;Module[method](n);return globalThis.__OCI_EXCHANGE_VAL;}finally{_free(n);}},release=name=>{const n=str2C(name);try{return Module._ReleaseOwnedShapeV2(n);}finally{_free(n);}};
const live=new Map(),state=name=>({metrics:query('_InspectOwnedSolidV2',name),catalog:query('_ReadOwnedTopologyV1',name)}),retained=()=>{for(const[name,before]of live)assert.deepEqual(state(name),before,'retained '+name);};
function call(name,profile,path){const f=new Float64Array(profile),p=new Float64Array(path),fp=_malloc(f.byteLength),pp=_malloc(p.byteLength),np=name===null?0:str2C(name);try{HEAPF64.set(f,fp/8);HEAPF64.set(p,pp/8);globalThis.__OCI_EXCHANGE_VAL=null;Module._CreateOwnedSweepV1(np,fp,f.length,pp,p.length);assert.deepEqual(Array.from(HEAPF64.subarray(fp/8,fp/8+f.length)),profile);assert.deepEqual(Array.from(HEAPF64.subarray(pp/8,pp/8+p.length)),path);return globalThis.__OCI_EXCHANGE_VAL;}finally{_free(fp);_free(pp);if(np)_free(np);}}
function check(label,profile,path,volume,bounds,points=[],error=null,name=label){const before=count(),result=call(name,profile,path),row={label,profile,path,result,expected:error?{error}:{volume,bounds},ownedBefore:before,ownedAfter:count(),callerPayloadPreserved:true};rows.push(row);retained();assert(result);if(error){assert.equal(result.error,error,label);assert.equal(count(),before);return;}assert.equal(result.error,undefined,label);assert.equal(result.valid,true);assert.equal(result.solidCount,1);assert(Math.abs(result.nativeVolume-volume)<Math.max(1e-7,volume*1e-9),label+' volume '+result.nativeVolume+' expected '+volume);for(const k of['min','max'])bounds[k].forEach((x,i)=>assert(Math.abs(x-result.nativeBounds[k][i])<1e-6,label+' bounds '+k+i));assert.equal(count(),before+1);row.snapshot=state(name);const n=str2C(name);try{row.points=points.map(([point,expected])=>{const actual=Module._ClassifyOwnedPointV2(n,...point);assert.equal(actual,expected,label+' point '+point);return{point,expected,actual};});}finally{_free(n);}assert.equal(release(name),1);assert.equal(count(),before);}
let failure;try{
assert.equal(count(),0);const data=new Float64Array([3,...I,1,0,0,0,2,0,2,2,0,2]),ptr=_malloc(data.byteLength),np=str2C('retained');HEAPF64.set(data,ptr/8);Module._CreateSelectedProfileV3(np,ptr,data.length);_free(ptr);_free(np);live.set('retained',state('retained'));assert(Math.abs(live.get('retained').metrics.nativeVolume-12)<1e-10);
const box={min:[-2,-2,0],max:[2,2,10]},qbox={min:[0,0,-2],max:[12,12,2]},rb={min:[-2,-.5,0],max:[2,.5,10]},qb={min:[0,0,-.5],max:[12,12,.5]},s=Math.SQRT1_2;
check('straight-circle',face([circle]),line(),40*pi,box,[[[0,0,5],0],[[3,0,5],1],[[2,0,5],2]]);
check('straight-annulus',face(annulus),line(),30*pi,box,[[[0,0,5],1],[[1.5,0,5],0],[[1,0,5],2]]);
check('straight-polygon',face([rect]),line(),40,rb,[[[1.5,0,5],0],[[0,.75,5],1]]);
check('straight-reverse',face([circle],[0,0,10,...I.slice(3)]),line(1),40*pi,box);
check('straight-antiparallel',face([circle],[0,0,0,1,0,0,0,-1,0,0,0,-1]),line(),40*pi,box);
check('offset-frame-origin',face([[1,-3,0,2]],[3,0,0,...I.slice(3)]),line(),40*pi,box);
check('offset-profile',face([[1,3,0,2]]),line(),40*pi,{min:[1,-2,0],max:[5,2,10]});
check('quarter-circle',face([circle],Q),arc(),20*pi*pi,qbox,[[[10*s,10*s,0],0],[[13*s,13*s,0],1],[[10,0,0],2]]);
check('quarter-annulus',face(annulus,Q),arc(),15*pi*pi,qbox,[[[10*s,10*s,0],1],[[11.5*s,11.5*s,0],0]]);
check('quarter-rectangle-roll',face([rect],Q),arc(),20*pi,qb,[[[11.5*s,11.5*s,0],0],[[10*s,10*s,.75],1]]);
check('quarter-reversed',face([circle],QR),arc([10,0],[0,10],1),20*pi*pi,qbox);
check('quarter-rectangle-reversed',face([rect],QR),arc([10,0],[0,10],1),20*pi,qb,[[[11.5*s,11.5*s,0],0],[[10*s,10*s,.75],1]]);
check('major-circle-not-shortest',face([circle],[0,10,0,0,1,0,0,0,-1,-1,0,0]),arc([0,10],[10,0]),60*pi*pi,{min:[-12,-12,-2],max:[12,12,2]});
check('zero-path',face([circle]),[1,0,...XZ,1,0,0,0,0,0,0],0,null,[],'SWEEP_ZERO_PATH');
check('closed-arc',face([circle],Q),arc([10,0],[10,0]),0,null,[],'SWEEP_CLOSED_PATH_UNSUPPORTED');
check('near-full-model',face([circle],Q),arc([10,0],[10,5e-7]),0,null,[],'SWEEP_CLOSED_PATH_UNSUPPORTED');
check('radius-mismatch',face([circle],Q),arc([10,0],[0,11]),0,null,[],'SWEEP_INVALID_PATH');
check('not-attached',face([circle],[0,0,1,...I.slice(3)]),line(),0,null,[],'SWEEP_PROFILE_NOT_ATTACHED');
check('not-normal',face([circle],XZ),line(),0,null,[],'SWEEP_PROFILE_NOT_NORMAL');
check('axis-contact',face([[1,-9,0,2]],Q),arc(),0,null,[],'SWEEP_UNSUPPORTED_AXIS_CONTACT');
check('multi-curve',face([circle]),[...line().slice(0,14),2,...line().slice(15),...line().slice(15)],0,null,[],'SWEEP_UNSUPPORTED_PATH');
check('truncated-profile',face([circle]).slice(0,-1),line(),0,null,[],'SWEEP_INVALID_REQUEST');
check('bad-profile',face([[1,0,0,-2]]),line(),0,null,[],'SWEEP_INVALID_PROFILE');
check('bad-transport',face([circle]),[1,1,...line().slice(2)],0,null,[],'SWEEP_INVALID_REQUEST');
check('duplicate',face([circle]),line(),0,null,[],'SWEEP_INVALID_REQUEST','retained');
check('null-name',face([circle]),line(),0,null,[],'SWEEP_INVALID_REQUEST',null);
const step=face([poly([[0,0],[10,0],[10,10],[5,10],[5,30],[0,30]])]),sd=new Float64Array(step),sp=_malloc(sd.byteLength),sn=str2C('old-revolve');HEAPF64.set(sd,sp/8);globalThis.__OCI_EXCHANGE_VAL=null;Module._CreateOwnedRevolveV1(sn,sp,sd.length,0,0,0,0,1,0,2*pi);const result=globalThis.__OCI_EXCHANGE_VAL;rows.push({label:'retained-revolve',result});assert(Math.abs(result.nativeVolume-1500*pi)<1e-7);assert.equal(release('old-revolve'),1);_free(sp);_free(sn);retained();
for(let i=0;i<8;i++)check('repeat-'+i,face([circle]),line(),40*pi,box);
}catch(error){failure={message:error.message,stack:error.stack};}finally{for(const[name]of live)try{assert.equal(release(name),1);}catch(error){failure=failure||{message:error.message};}const receipt={status:failure?'FAIL':'PASS',scope:'Genuine full-main C++→WASM; component inputs, no public authoring/history claim',runtimePins,rows,finalOwnedNames:count(),failure};fs.writeFileSync(process.env.CODI_SWEEP_RECEIPT,JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({status:receipt.status,rows:rows.length,finalOwnedNames:count(),failure}));if(failure||count()!==0)process.exitCode=1;}
}
