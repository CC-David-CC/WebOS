"""Independent arithmetic/native-file checks; no CAD oracle or product imports."""
from pathlib import Path
import json,hashlib,math
root=Path(__file__).parent
r=json.loads((root/'evidence/r2/receipt.json').read_text())
assert r['status']=='PASS'
checks=[]
def visit(value):
 if isinstance(value,list):
  for x in value: visit(x)
 elif isinstance(value,dict):
  if {'expected','nativeVolume','nativeBounds','resources'}<=value.keys():
   e=value['expected'];w,h,d=e['width'],e['height'],e['depth']
   n=e.get('patternCount',1) if e.get('centerDiameter',0) else 0
   bore_area=math.pi*(n*e.get('centerDiameter',0)**2+4*e.get('cornerDiameter',0)**2)/4
   # Two opposite vertical rounds, plus two equal-distance chamfers.
   expected=w*h*d-d*bore_area-2*d*e.get('fillet',0)**2*(1-math.pi/4)-d*e.get('chamfer',0)**2
   delta=abs(value['nativeVolume']-expected);assert delta<1e-6,(expected,value['nativeVolume'])
   assert all(abs(a-b)<1e-7 for a,b in zip(value['nativeBounds']['min'],[0,0,0]))
   assert all(abs(a-b)<1e-7 for a,b in zip(value['nativeBounds']['max'],[w,h,d]))
   usage=value['resources']['usage'];assert usage=={'owners':1,'mounts':0,'candidates':0,'accepted':0,'detached':1,'cleanupFailed':False},usage
   checks.append({'nativeVolume':value['nativeVolume'],'analyticVolume':expected,'absoluteError':delta,'resourceUsage':usage})
  for x in value.values():visit(x)
visit(r['rows']);assert len(checks)==12
saves=[]
for name,expected in [('source-bound-pattern',r['savedExpected']),('source-bound-pattern-reedited',r['resavedExpected'])]:
 raw=(root/'evidence/r2'/f'{name}.jsketcher.json').read_bytes();sha=hashlib.sha256(raw).hexdigest()
 receipt=next(x for x in r['rows'] if x['label']==name+' normal native Save and server sync')
 assert len(raw)==receipt['bytes'] and sha==receipt['sha256']
 v=json.loads(raw);assert v['unit']=='millimeter' and v['presentation']=={'version':1,'lengthUnit':'inch'}
 h=v['project']['model']['history'];assert len(h)==7
 assert [x['type'] for x in h]==['PLANE','WORKER_SELECTED_PROFILE_EXTRUDE_V2','WORKER_THROUGH_HOLES_V1','WORKER_THROUGH_HOLES_V1','WORKER_SOLID_EDGE_TREATMENT_V1','WORKER_SOLID_EDGE_TREATMENT_V1','WORKER_LINEAR_HOLE_PATTERN_V1']
 p=h[-1]['params'];assert (p['count'],p['spacing'])==(expected['patternCount'],expected['spacing'])
 assert p['seedFeatureId']==h[2]['params']['featureId'] and p['producerFeatureId']==h[5]['params']['featureId']
 assert len(v['project']['sketches'])==1 and len(v['project']['sketches'][0]['data']['objects'])==4
 saves.append({'name':name,'bytes':len(raw),'sha256':sha,'patternCount':p['count'],'spacing':p['spacing']})
result={'status':'PASS','scope':'Independent recorded native arithmetic, bounds, stable settled resource records and native file bytes/intent; no fresh native execution','nativeSnapshots':len(checks),'maximumVolumeError':max(x['absoluteError'] for x in checks),'checks':checks,'saves':saves}
print(json.dumps(result,indent=2))
