"""Independent recorded analytic native/file checks; no CAD imports."""
from pathlib import Path
import json,hashlib,math
base=Path(__file__).parent/'evidence/r1';r=json.loads((base/'receipt.json').read_text());assert r['status']=='PASS'
rows=[x for x in r['rows'] if 'geometry' in x];assert len(rows)==3
checks=[]
for x,w in zip(rows,[150,150,160]):
 g=x['geometry'];expected=w*50*20-math.pi*20*(10**2+4*4**2)/4;error=abs(expected-g['nativeVolume']);assert error<1e-6
 assert all(abs(a-b)<1e-7 for a,b in zip(g['nativeBounds']['min'],[0,0,0]))
 assert all(abs(a-b)<1e-7 for a,b in zip(g['nativeBounds']['max'],[w,50,20]))
 assert {k:g['nativeTopology']['counts'][k] for k in ['faces','edges','vertices']}=={'faces':11,'edges':27,'vertices':18}
 checks.append({'width':w,'analyticVolume':expected,'nativeVolume':g['nativeVolume'],'absoluteError':error})
saves=[]
for name in ['driving-rectangle','driving-circle','driving-typed']:
 raw=(base/(name+'.jsketcher.json')).read_bytes();record=next(x for x in r['rows'] if x['label']==name+' normal native Save and server sync');digest=hashlib.sha256(raw).hexdigest();assert digest==record['sha256'] and len(raw)==record['bytes'];v=json.loads(raw);assert v['unit']=='millimeter';assert b'sketch-driving-constraint:' not in raw
 s=v['project']['sketches'][0]['data']
 if name!='driving-rectangle':
  circle=next(o for o in s['objects'] if o['type']=='Circle');assert abs(2*circle['data']['r']-12)<1e-6
  constants=[c for stage in s['stages'] for c in stage['constraints'] if c['typeId']=='DiameterLength'];assert len(constants)==1 and constants[0]['constants']['diameter']==('lengthA' if name=='driving-typed' else '12')
  if name=='driving-circle':
   edges=[o['data'] for o in s['objects'] if o['type']=='Segment'];assert edges==[{'a':{'x':30,'y':30},'b':{'x':40,'y':30}},{'a':{'x':40,'y':30},'b':{'x':35,'y':40}},{'a':{'x':35,'y':40},'b':{'x':30,'y':30}}]
  else:
   expression=v['project']['model']['expressions'];assert expression.startswith('codi-physical-parameters:2\n');assert json.loads(expression.split('\n',1)[1])['definitions']==r['typed']['definitions']
 saves.append({'name':name,'sha256':digest,'bytes':len(raw)})
print(json.dumps({'status':'PASS','scope':'Independent recorded native arithmetic/bounds/topology and three saved native source files; no new geometry execution','nativeSnapshots':len(checks),'checks':checks,'saves':saves},indent=2))
