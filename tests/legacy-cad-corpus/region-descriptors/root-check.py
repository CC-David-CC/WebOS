"""Independent recorded arithmetic/file checks, without CAD test imports."""
from pathlib import Path
import json,math,hashlib
base=Path(__file__).parent/'evidence-r2'
r=json.loads((base/'receipt.json').read_text());assert r['status']=='PASS_SCOPED_SUBSETS'
rows=[x for x in r['rows'] if 'geometry' in x];assert len(rows)==8
checks=[]
for i,row in enumerate(rows):
 bodies=row['geometry']['bodies'];assert len(bodies)==2
 if i<4:
  w=[20,25,25,26][i];expected=[(500,[30,0,0],[40,10,5]),(w*50,[0,0,0],[w,10,5])]
 else:
  radius=[10,11,11,11][i-4];depth=[10,10,10,12][i-4];expected=[(math.pi*(225-radius**2)*depth,[-15,-15,0],[15,15,depth]),(250*math.pi,[-5,-5,0],[5,5,10])]
 for body,(volume,minimum,maximum) in zip(bodies,expected):
  m=body['metrics'];assert m['nativeValidity']['valid'] and m['solidCount']==1
  error=abs(m['nativeVolume']-volume);assert error<1e-6
  assert all(abs(a-b)<1e-7 for a,b in zip(m['nativeBounds']['min'],minimum))
  assert all(abs(a-b)<1e-7 for a,b in zip(m['nativeBounds']['max'],maximum))
  checks.append({'row':row['label'],'featureId':body['featureId'],'analyticVolume':volume,'nativeVolume':m['nativeVolume'],'absoluteError':error})
saves=[]
for name in ['E04-disjoint','E04-disjoint-reedited','E05-nested','E05-nested-reedited']:
 raw=(base/(name+'.jsketcher.json')).read_bytes();receipt=next(x for x in r['rows'] if x['label']==name+' normal native Save and server sync');digest=hashlib.sha256(raw).hexdigest();assert digest==receipt['sha256'] and len(raw)==receipt['bytes']
 v=json.loads(raw);assert v['unit']=='millimeter';h=v['project']['model']['history'];assert [x['type'] for x in h]==['PLANE','WORKER_SELECTED_PROFILE_EXTRUDE_V2','WORKER_SELECTED_PROFILE_EXTRUDE_V2'];assert [int(x['params']['featureId']) for x in h]==[1,2,3]
 assert h[1]['params']['regionId']!=h[2]['params']['regionId'];sketches=v['project']['sketches'];assert len(sketches)==1
 objects=sketches[0]['data']['objects'];assert len(objects)==(8 if name.startswith('E04') else 3)
 assert all(o['type']==('Segment' if name.startswith('E04') else 'Circle') for o in objects)
 saves.append({'name':name,'bytes':len(raw),'sha256':digest,'sourceObjects':len(objects),'features':len(h)})
print(json.dumps({'status':'PASS','scope':'Independent recorded native arithmetic/bounds/validity and four exact saved files; no fresh geometry execution','nativeBodyObservations':len(checks),'maximumVolumeError':max(x['absoluteError'] for x in checks),'checks':checks,'saves':saves},indent=2))
