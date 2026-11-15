// Independent saved-source arithmetic, not a CAD/kernel/mesh implementation.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const REVOLVE_ORACLE_TOLERANCE=Object.freeze({volumeMM3:1e-6,boundsMM:1e-6});
export const sha256=b=>createHash('sha256').update(b).digest('hex');
const keys=['version','unit','engine','engineRevision','featureId','faceId','regionId','axisSegmentId','angleRadians','bodyPolicy'];
const fail=(code,message)=>{throw Object.assign(Error(message),{code});};
const unsupported=message=>fail('ORACLE_UNSUPPORTED',message),requireBinding=(ok,message)=>{if(!ok)fail('ORACLE_BINDING_MISMATCH',message);};
const equal=(a,b,message)=>{try{assert.deepEqual(a,b);}catch{fail('ORACLE_BINDING_MISMATCH',message);}};
const sorted=a=>[...a].sort(),id=v=>typeof v==='string'&&v.length>0,finite=v=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<=1e6;
function point(p){if(!p||!finite(p.x)||!finite(p.y))unsupported('Source points must be bounded primitive millimeters.');return[p.x,p.y];}
function segment(o){if(o?.type!=='Segment'||o.stage!==0||![null,'construction'].includes(o.role))unsupported('Only stage-zero native Segments are covered.');return{a:point(o.data?.a),b:point(o.data?.b)};}
function frozen(v){if(v&&typeof v==='object'){for(const x of Object.values(v))frozen(x);Object.freeze(v);}return v;}

// binding contains actual returned IDs and current public history's signed
// angle. discovery is an unmodified inspect-worker-revolve-regions response.
// Solved-source digest is checked as public binding; authored bytes are NOT
// claimed to be the solver's serialization. No opaque ID is decoded.
export function deriveRevolveExpectation({native,binding,discovery}){
 if(native?.format!=='codi-jsketcher-project'||native.version!==2||native.unit!=='millimeter')unsupported('Requires normal native v2 millimeter design.');
 const b=binding;requireBinding(b&&['faceId','axisSegmentId','regionId','bodyId','engineRevision','sourceDigest'].every(k=>id(b[k])),'Missing actual public source/output bindings.');
 requireBinding(Number.isSafeInteger(b.featureId)&&b.featureId>0,'Missing public feature identity.');
 requireBinding(Array.isArray(b.profileSegmentIds)&&b.profileSegmentIds.length===4&&b.profileSegmentIds.every(id)&&new Set(b.profileSegmentIds).size===4&&!b.profileSegmentIds.includes(b.axisSegmentId),'Four unique profile IDs and a distinct actual axis ID are required.');
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
 const d=regions[0].descriptor;requireBinding(Array.isArray(d?.outerCurveIds)&&Array.isArray(d.holeCurveIds),'Missing explicit region membership.');equal(sorted(d.outerCurveIds),sorted(b.profileSegmentIds),'Region membership differs.');equal(d.holeCurveIds,[],'Initial rectangle fixture has no holes.');
 const axes=discovery.axes?.filter(a=>a.axisSegmentId===b.axisSegmentId);requireBinding(axes?.length===1&&axes[0].supported===true&&axes[0].reason===null,'Actual source axis unavailable.');
 const ao=byId.get(b.axisSegmentId),axis=segment(ao),pa=axes[0];equal(pa.a,axis.a,'Directed axis start differs.');equal(pa.b,axis.b,'Directed axis end differs.');requireBinding(pa.role===ao.role&&pa.stage===ao.stage,'Axis role/stage differs.');
 if(axis.a[0]!==axis.b[0]||axis.a[1]===axis.b[1])unsupported('Initial oracle requires nonzero vertical axis.');
 const lines=b.profileSegmentIds.map(k=>{const o=byId.get(k);if(o?.role!==null)unsupported('Profile must be normal authored geometry.');return segment(o);});
 const xs=[...new Set(lines.flatMap(s=>[s.a[0],s.b[0]]))].sort((a,b)=>a-b),ys=[...new Set(lines.flatMap(s=>[s.a[1],s.b[1]]))].sort((a,b)=>a-b);
 if(xs.length!==2||ys.length!==2||xs[0]>=xs[1]||ys[0]>=ys[1])unsupported('Not an axis-aligned nondegenerate rectangle.');
 const corners=new Map(),edges=new Set();for(const{a,b:end}of lines){if(a[0]===end[0]&&a[1]===end[1]||a[0]!==end[0]&&a[1]!==end[1])unsupported('Nonzero axis-aligned edges required.');const pair=[JSON.stringify(a),JSON.stringify(end)].sort().join('|');if(edges.has(pair))unsupported('Duplicate rectangle edge.');edges.add(pair);for(const p of[a,end]){const k=JSON.stringify(p);corners.set(k,(corners.get(k)||0)+1);}}
 if(corners.size!==4||[...corners.values()].some(n=>n!==2))unsupported('Not one exact closed four-edge rectangle.');
 const axisX=axis.a[0],inner=xs[0]-axisX,outer=xs[1]-axisX,height=ys[1]-ys[0];if(inner<=0||outer<=inner)unsupported('Rectangle must be strictly right of axis.');
 const theta=params.angleRadians*Math.sign(axis.b[1]-axis.a[1]),lo=Math.min(0,theta),hi=Math.max(0,theta),angles=[0,theta];for(let n=-4;n<=4;n++){const a=n*Math.PI/2;if(a>=lo&&a<=hi)angles.push(a);}
 const x=[],z=[];for(const a of angles)for(const r of[inner,outer]){x.push(axisX+r*Math.cos(a));z.push(-r*Math.sin(a));}
 return frozen({scope:'canonical-XY vertical-axis rectangular fixture',binding:structuredClone(b),authored:structuredClone(params),source:{axis,axisX,innerRadius:inner,outerRadius:outer,height,xs,ys},volumeMM3:Math.abs(params.angleRadians)*(outer*outer-inner*inner)*height/2,boundsMM:{min:[Math.min(...x),ys[0],Math.min(...z)],max:[Math.max(...x),ys[1],Math.max(...z)]},tolerance:REVOLVE_ORACLE_TOLERANCE,digestScope:'public solved-source binding only, no independent solve or hash of authored serialization'});
}

// observation is the driver's normalized real public body observation.
// Optional expectedRevision is an explicit same-state token; fresh Open tokens
// must NOT be compared to the previous session. A file cannot prove freshness.
export function checkRevolveObservation(observation,expected,{expectedRevision=null}={}){
 const b=expected.binding,o=observation,m=o?.metrics;requireBinding(id(o?.revision),'Missing observation revision.');if(expectedRevision!==null)requireBinding(o.revision===expectedRevision,'Stale solid observation.');
 requireBinding(o.featureId===b.featureId&&o.bodyId===b.bodyId&&o.engineRevision===b.engineRevision,'Output feature/body/build differs.');
 requireBinding('sha256:'+m?.runtime?.jsSha256+':'+m?.runtime?.wasmSha256===b.engineRevision,'Native runtime differs.');requireBinding(m.nativeValidity?.valid===true&&m.solidCount===1&&m.empty!==true,'Requires one native-valid nonempty solid.');
 requireBinding(typeof m.nativeVolume==='number'&&Number.isFinite(m.nativeVolume)&&m.nativeVolume>0&&Math.abs(m.nativeVolume-expected.volumeMM3)<=REVOLVE_ORACLE_TOLERANCE.volumeMM3,'Native volume differs from saved-source analytic volume.');
 for(const k of['min','max']){requireBinding(Array.isArray(m.nativeBounds?.[k])&&m.nativeBounds[k].length===3,'Missing native bounds.');for(let i=0;i<3;i++)requireBinding(typeof m.nativeBounds[k][i]==='number'&&Number.isFinite(m.nativeBounds[k][i])&&Math.abs(m.nativeBounds[k][i]-expected.boundsMM[k][i])<=REVOLVE_ORACLE_TOLERANCE.boundsMM,'Native angular bounds differ on '+k+' axis'+i);}
 for(let i=0;i<3;i++)requireBinding(m.nativeBounds.min[i]<=m.nativeBounds.max[i],'Native bounds are reversed.');
 return frozen({featureId:b.featureId,bodyId:b.bodyId,volumeMM3:m.nativeVolume,expectedVolumeMM3:expected.volumeMM3,boundsMM:structuredClone(m.nativeBounds),expectedBoundsMM:expected.boundsMM,unit:'millimeter',nativeValidity:true,tolerance:REVOLVE_ORACLE_TOLERANCE});
}
