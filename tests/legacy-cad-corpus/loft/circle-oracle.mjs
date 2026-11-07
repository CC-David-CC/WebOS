// Independent analytic oracle for the explicitly bounded signed circle fixture.
// No product/kernel code, triangulation, solved metrics or serialized BRep used.
import assert from 'node:assert/strict';
export const LOFT_OP='WORKER_SELECTED_PROFILE_LOFT_V1';
const exact=(a,b,message)=>assert.deepEqual(a,b,message);
function finite(value){assert(typeof value==='number'&&Number.isFinite(value));return value;}
export function circleLoftFromSaved(native,featureId){
  const rows=native.project.model.history.filter(r=>r.type===LOFT_OP&&r.params.featureId===featureId);
  assert.equal(rows.length,1,'One actual saved loft feature required');
  const p=rows[0].params;
  exact(Object.keys(p).sort(),['version','unit','engine','engineRevision','featureId','sections','construction','bodyPolicy'].sort());
  assert.equal(p.version,1);assert.equal(p.unit,'millimeter');assert.equal(p.engine,'occ');
  assert.equal(p.construction,'ruled-solid');assert.equal(p.bodyPolicy,'separate');
  assert.equal(p.sections.length,2);assert.notEqual(p.sections[0].faceId,p.sections[1].faceId);
  const sections=p.sections.map(section=>{
    assert.equal(section.seam.kind,'circle-angle');assert.equal(section.seam.reversed,false);
    const found=native.project.sketches.filter(s=>s.id===section.faceId);assert.equal(found.length,1);
    const data=found[0].data,curves=data.objects.filter(o=>o.role===null&&o.stage===0);
    assert.equal(curves.length,1,'Oracle fixture has exactly one ordinary source circle');
    const circle=curves[0];assert.equal(circle.type,'Circle');assert.equal(circle.id,section.seam.curveId);
    const f=data.metadata.boundaryFrame;
    exact(f.x,[1,0,0]);exact(f.y,[0,1,0]);exact(f.z,[0,0,1]);
    assert.equal(f.origin.length,3);f.origin.forEach(finite);
    const radius=finite(circle.data.r);assert(radius>0);
    const cx=f.origin[0]+finite(circle.data.c.x),cy=f.origin[1]+finite(circle.data.c.y);
    return {faceId:section.faceId,curveId:circle.id,radius,cx,cy,z:f.origin[2],angle:finite(section.seam.angleRadians)};
  });
  const [a,b]=sections;assert.equal(a.cx,b.cx);assert.equal(a.cy,b.cy);
  const height=Math.abs(b.z-a.z);assert(height>0);
  const phase=b.angle-a.angle;
  // This fixture excludes collapse/branch ambiguity, rather than claiming it valid.
  assert(Math.abs(phase)<Math.PI-1e-8,'Antipodal/collapsing correspondence is outside the positive oracle');
  const radiusAt=t=>Math.sqrt((1-t)**2*a.radius**2+t*t*b.radius**2+2*t*(1-t)*a.radius*b.radius*Math.cos(phase));
  const middleRadius=radiusAt(.5),middleZ=(a.z+b.z)/2,r=Math.max(a.radius,b.radius);
  const probes=[
    {point:[a.cx,a.cy,middleZ],classification:'inside'},
    {point:[a.cx+middleRadius/2,a.cy,middleZ],classification:'inside'},
    {point:[a.cx+middleRadius,a.cy,middleZ],classification:'boundary'},
    {point:[a.cx+middleRadius+1,a.cy,middleZ],classification:'outside'},
    {point:[a.cx,a.cy,Math.max(a.z,b.z)+1],classification:'outside'},
    {point:[a.cx,a.cy,a.z],classification:'boundary'},
  ];
  return {featureId,engineRevision:p.engineRevision,sections,unit:'millimeter',
    volumeMM3:Math.PI*height*(a.radius*a.radius+b.radius*b.radius+a.radius*b.radius*Math.cos(phase))/3,
    boundsMM:{min:[a.cx-r,a.cy-r,Math.min(a.z,b.z)],max:[a.cx+r,a.cy+r,Math.max(a.z,b.z)]},probes};
}
export function checkCircleLoftMetrics(metrics,expected){
  assert.equal(metrics.nativeValidity.valid,true);assert.equal(metrics.solidCount,1);
  assert.equal(metrics.resultKind,'single-solid');
  assert(Math.abs(metrics.nativeVolume-expected.volumeMM3)<=1e-6,'Native volume differs from saved-source analytic oracle');
  for(const side of ['min','max'])for(let i=0;i<3;i++)assert(Math.abs(metrics.nativeBounds[side][i]-expected.boundsMM[side][i])<=1e-6,'Native bound differs from saved-source analytic oracle');
}
