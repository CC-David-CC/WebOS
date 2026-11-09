// Independent exact6 stepped fixture oracle; no production geometry imports.
import assert from 'node:assert/strict';
import {deriveRevolveExpectation,REVOLVE_ORACLE_TOLERANCE} from './oracle.mjs';
const keys=['version','unit','engine','engineRevision','featureId','faceId','regionId','axisSegmentId','angleRadians','bodyPolicy'];
const fail=(code,message)=>{throw Object.assign(Error(message),{code});};
const unsupported=message=>fail('ORACLE_UNSUPPORTED',message),requireBinding=(ok,message)=>{if(!ok)fail('ORACLE_BINDING_MISMATCH',message);};
const equal=(a,b,message)=>{try{assert.deepEqual(a,b);}catch{fail('ORACLE_BINDING_MISMATCH',message);}};
const sorted=a=>[...a].sort(),id=v=>typeof v==='string'&&v.length>0,finite=v=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<=1e6;
function point(p){if(!p||!finite(p.x)||!finite(p.y))unsupported('Source points must be bounded primitive millimeters.');return[p.x,p.y];}
function segment(o){if(o?.type!=='Segment'||o.stage!==0||![null,'construction'].includes(o.role))unsupported('Only stage-zero native Segments are covered.');return{a:point(o.data?.a),b:point(o.data?.b)};}
function frozen(v){if(v&&typeof v==='object'){for(const x of Object.values(v))frozen(x);Object.freeze(v);}return v;}

// Only absence selects the historical rectangle default. Explicit undefined,
// null, unknown strings or other malformed kinds cannot broaden its domain.
export function deriveRevolveFixtureExpectation(input){
 const kind=Object.hasOwn(input,'oracleKind')?input.oracleKind:'rectangle-v1';
 if(kind==='rectangle-v1')return deriveRevolveExpectation(input);
 if(kind==='stepped-orthogonal-v1')return deriveSteppedRevolveExpectation(input);
 fail('ORACLE_UNSUPPORTED_KIND','Unknown or malformed fixture oracle kind.');
}

export function deriveSteppedRevolveExpectation({native,binding,discovery}){
 if(native?.format!=='codi-jsketcher-project'||native.version!==2||native.unit!=='millimeter')unsupported('Requires normal native v2 millimeter design.');
 const b=binding;requireBinding(b&&['faceId','axisSegmentId','regionId','bodyId','engineRevision','sourceDigest'].every(k=>id(b[k])),'Missing actual public source/output bindings.');
 requireBinding(Number.isSafeInteger(b.featureId)&&b.featureId>0,'Missing public feature identity.');
 requireBinding(Array.isArray(b.profileSegmentIds)&&b.profileSegmentIds.length===6&&b.profileSegmentIds.every(id)&&new Set(b.profileSegmentIds).size===6&&!b.profileSegmentIds.includes(b.axisSegmentId),'Six unique profile IDs and a distinct actual axis ID are required.');
 requireBinding(/^[a-f0-9]{64}$/.test(b.sourceDigest)&&/^sha256:[a-f0-9]{64}:[a-f0-9]{64}$/.test(b.engineRevision),'Invalid public digest/build binding.');
 requireBinding(discovery?.faceId===b.faceId&&id(discovery.revision)&&discovery.sourceDigest===b.sourceDigest&&discovery.engine==='occ'&&discovery.engineRevision===b.engineRevision&&discovery.unit==='millimeter','Discovery source/build/digest differs.');
 const history=native.project?.model?.history,sketches=native.project?.sketches;if(!Array.isArray(history)||!Array.isArray(sketches))unsupported('Missing native authored history/source.');
 if(history.length!==2||history[0].type!=='PLANE'||history[1].type!=='WORKER_SELECTED_PROFILE_REVOLVE_V1')unsupported('Fixture requires one source plane and one revolve.');
 const plane=history[0].params;if(plane?.orientation!=='XY'||plane.datum!==null||plane.depth!==0)unsupported('Initial oracle is canonical XY at zero depth without datum.');
 const params=history[1].params;requireBinding(params&&JSON.stringify(sorted(Object.keys(params)))===JSON.stringify(sorted(keys)),'History must contain exactly ten authored fields.');
 requireBinding(params.version===1&&params.unit==='millimeter'&&params.engine==='occ'&&params.bodyPolicy==='separate','Unexpected authored revolve contract.');
 for(const key of['featureId','faceId','regionId','axisSegmentId','engineRevision','angleRadians'])requireBinding(params[key]===b[key],'Saved/public '+key+' differs.');
 if(b.authored)equal(params,b.authored,'Saved/current public ten-field intent differs.');
 if(typeof params.angleRadians!=='number'||!Number.isFinite(params.angleRadians)||params.angleRadians===0||Math.abs(params.angleRadians)>2*Math.PI)unsupported('Requires nonzero signed sweep at most2π.');
 requireBinding(sketches.length===1&&sketches[0].id===b.faceId,'Saved source plane identity differs.');
 const data=sketches[0].data,objects=data?.objects;if(data?.version!==3||!Array.isArray(objects)||!Array.isArray(data.stages)||data.stages.length!==1)unsupported('Requires one-stage native v3 source.');
 const byId=new Map();for(const o of objects){requireBinding(id(o?.id)&&!byId.has(o.id),'Saved identities missing or duplicated.');byId.set(o.id,o);}
 equal(sorted(objects.map(o=>o.id)),sorted([...b.profileSegmentIds,b.axisSegmentId]),'Saved object IDs differ from actual public IDs.');
 const regions=discovery.regions?.filter(r=>r.regionId===b.regionId);requireBinding(regions?.length===1&&regions[0].support==='supported','One exact supported region required.');
 const d=regions[0].descriptor;requireBinding(Array.isArray(d?.outerCurveIds)&&Array.isArray(d.holeCurveIds),'Missing explicit region membership.');equal(sorted(d.outerCurveIds),sorted(b.profileSegmentIds),'Region membership differs.');equal(d.holeCurveIds,[],'Initial stepped fixture has no holes.');
 const axes=discovery.axes?.filter(a=>a.axisSegmentId===b.axisSegmentId);requireBinding(axes?.length===1&&axes[0].supported===true&&axes[0].reason===null,'Actual source axis unavailable.');
 const ao=byId.get(b.axisSegmentId),axis=segment(ao),pa=axes[0];equal(pa.a,axis.a,'Directed axis start differs.');equal(pa.b,axis.b,'Directed axis end differs.');requireBinding(pa.role===ao.role&&pa.stage===ao.stage,'Axis role/stage differs.');
 if(axis.a[0]!==axis.b[0]||axis.a[1]===axis.b[1])unsupported('Initial oracle requires nonzero vertical axis.');
 const lines=b.profileSegmentIds.map(k=>{const o=byId.get(k);if(o?.role!==null)unsupported('Profile must be normal authored geometry.');return segment(o);});
 const coordinate=p=>JSON.stringify(p),vertices=new Map(),edges=new Set();
 for(let index=0;index<lines.length;index++){
  const {a,b:end}=lines[index];if(a[0]===end[0]&&a[1]===end[1]||a[0]!==end[0]&&a[1]!==end[1])unsupported('Six nonzero orthogonal edges are required.');
  const pair=[coordinate(a),coordinate(end)].sort().join('|');if(edges.has(pair))unsupported('Duplicate stepped edge.');edges.add(pair);
  for(const p of[a,end]){const key=coordinate(p);let row=vertices.get(key);if(!row){row={point:p,incident:[]};vertices.set(key,row);}row.incident.push(index);}
 }
 if(vertices.size!==6||[...vertices.values()].some(v=>v.incident.length!==2))unsupported('Requires six unique vertices of closed degree2 incidence.');
 for(const v of vertices.values()){const [a,b]=v.incident.map(i=>lines[i]);if((a.a[0]===a.b[0])===(b.a[0]===b.b[0]))unsupported('Consecutive source edges must be perpendicular.');}
 const visited=new Set(),queue=[0];while(queue.length){const n=queue.pop();if(visited.has(n))continue;visited.add(n);for(const p of[lines[n].a,lines[n].b])for(const next of vertices.get(coordinate(p)).incident)queue.push(next);}
 if(visited.size!==6)unsupported('Requires one connected source loop.');
 // Exact closed-segment intersection over authored double coordinates. No
 // proximity/welding, arrangement, midpoint sampling or implicit repair.
 for(let i=0;i<lines.length;i++)for(let j=i+1;j<lines.length;j++){
  const a=lines[i],b=lines[j],shared=[a.a,a.b].some(p=>[b.a,b.b].some(q=>coordinate(p)===coordinate(q)));
  if(shared)continue;
  const av=a.a[0]===a.b[0],bv=b.a[0]===b.b[0],within=(v,x,y)=>v>=Math.min(x,y)&&v<=Math.max(x,y);
  let touches=false;
  if(av===bv){if(av&&a.a[0]===b.a[0])touches=Math.max(Math.min(a.a[1],a.b[1]),Math.min(b.a[1],b.b[1]))<=Math.min(Math.max(a.a[1],a.b[1]),Math.max(b.a[1],b.b[1]));
   if(!av&&a.a[1]===b.a[1])touches=Math.max(Math.min(a.a[0],a.b[0]),Math.min(b.a[0],b.b[0]))<=Math.min(Math.max(a.a[0],a.b[0]),Math.max(b.a[0],b.b[0]));
  }else{const vertical=av?a:b,horizontal=av?b:a;touches=within(vertical.a[0],horizontal.a[0],horizontal.b[0])&&within(horizontal.a[1],vertical.a[1],vertical.b[1]);}
  if(touches)unsupported('Nonadjacent source contact, crossing or overlap is outside this oracle.');
 }
 const points=[...vertices.values()].map(v=>v.point),axisX=axis.a[0];if(points.some(p=>p[0]<=axisX))unsupported('Entire stepped loop must be strictly right of axis.');
 const ys=[...new Set(points.map(p=>p[1]))].sort((a,b)=>a-b),bands=[];
 for(let i=0;i<ys.length-1;i++){
  const bottom=ys[i],top=ys[i+1];if(!(top>bottom))unsupported('Positive exact height bands required.');
  const crossing=lines.filter(l=>l.a[0]===l.b[0]&&Math.min(l.a[1],l.b[1])<=bottom&&Math.max(l.a[1],l.b[1])>=top).map(l=>l.a[0]).sort((a,b)=>a-b);
  if(crossing.length!==2||crossing[0]>=crossing[1])unsupported('Each open height band must have one exact radial interval.');
  bands.push({bottom,top,height:top-bottom,innerRadius:crossing[0]-axisX,outerRadius:crossing[1]-axisX});
 }
 const theta=params.angleRadians*Math.sign(axis.b[1]-axis.a[1]),lo=Math.min(0,theta),hi=Math.max(0,theta),angles=[0,theta];for(let n=-4;n<=4;n++){const a=n*Math.PI/2;if(a>=lo&&a<=hi)angles.push(a);}
 const x=[],z=[];for(const band of bands)for(const a of angles)for(const r of[band.innerRadius,band.outerRadius]){x.push(axisX+r*Math.cos(a));z.push(-r*Math.sin(a));}
 const coefficient=bands.reduce((sum,v)=>sum+v.height*(v.outerRadius*v.outerRadius-v.innerRadius*v.innerRadius),0);
 return frozen({scope:'canonical-XY vertical-axis six-edge orthogonal y-monotone fixture',binding:structuredClone(b),authored:structuredClone(params),source:{axis,axisX,bands,ys},volumeMM3:Math.abs(params.angleRadians)*coefficient/2,boundsMM:{min:[Math.min(...x),ys[0],Math.min(...z)],max:[Math.max(...x),ys[ys.length-1],Math.max(...z)]},tolerance:REVOLVE_ORACLE_TOLERANCE,digestScope:'public solved-source binding only, no independent solve or hash of authored serialization'});
}
