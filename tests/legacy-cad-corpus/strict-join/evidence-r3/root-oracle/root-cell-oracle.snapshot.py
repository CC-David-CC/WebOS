"""Independent exact rational box-CSG cell oracle; no CAD/kernel imports.
Checks saved geometry rows even from a stopped corpus, without certifying that run.
Opaque output IDs are resolved from public creation receipts, never parsed.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,sys,hashlib
root=Path(sys.argv[1]);raw=(root/'receipt.json').read_bytes();receipt=json.loads(raw);results=[]
for row in receipt['rows']:
 if row.get('label')!='Native Save/sync/fresh Open retains exact Join intent and resets session journal':continue
 case=next(c for c in receipt['cases'] if c['name']==row['case']);bindings={}
 def visit(v):
  if isinstance(v,dict):
   if isinstance(v.get('featureId'),int) and isinstance(v.get('outputId'),str):
    old=bindings.setdefault(v['featureId'],v['outputId']);assert old==v['outputId']
   for child in v.values():visit(child)
  elif isinstance(v,list):
   for child in v:visit(child)
 visit(case['bindings'])
 data=(root/(row['fileLabel']+'.jsketcher.json')).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];native=json.loads(data)
 assert native['unit']=='millimeter' and native['project']['sketches']==[]
 history=native['project']['model']['history'];assert history==row['history'];assert len({f['params']['featureId'] for f in history})==len(history)
 boxes=[f['params'] for f in history if f['type']=='WORKER_SOLID_BOX_V1'];axes=[]
 for origin,size in [('x','width'),('y','depth'),('z','height')]:
  values=sorted({F(str(p[origin]))+side*F(str(p[size])) for p in boxes for side in [0,1]});axes.append(list(zip(values,values[1:])))
 cells=list(product(*axes));centers=[tuple((lo+hi)/2 for lo,hi in c) for c in cells];solids={}
 for feature in history:
  p=feature['params'];assert p['engine']==case['discovery']['engine']['id'] and p['engineRevision']==case['discovery']['engine']['revision'];key=bindings[p['featureId']]
  if feature['type']=='WORKER_SOLID_BOX_V1':
   lo=[F(str(p[k])) for k in ['x','y','z']];hi=[v+F(str(p[k])) for v,k in zip(lo,['width','depth','height'])]
   solids[key]={i for i,c in enumerate(centers) if all(a<x<b for a,x,b in zip(lo,c,hi))}
  else:
   assert feature['type']=='WORKER_SOLID_BOOLEAN_V1';a,b=solids[p['a']],solids[p['b']]
   assert p['kind'] in ['join','union','subtract','common'];solids[key]=(a|b) if p['kind'] in ['join','union'] else (a-b) if p['kind']=='subtract' else (a&b)
 chosen=solids[bindings[history[-1]['params']['featureId']]];assert chosen
 volume=sum(((cells[i][0][1]-cells[i][0][0])*(cells[i][1][1]-cells[i][1][0])*(cells[i][2][1]-cells[i][2][0]) for i in chosen),F(0))
 lower=[min(cells[i][k][0] for i in chosen) for k in range(3)];upper=[max(cells[i][k][1] for i in chosen) for k in range(3)]
 m=row['geometry']['output']['metrics'];occ=case['discovery']['engine']['id']=='occ';actual=m['nativeVolume'] if occ else m['reportedVolume'];bounds=m['nativeBounds'] if occ else m['bounds'];error=abs(actual-float(volume));assert error<=1e-6
 for k in range(3):assert abs(bounds['min'][k]-float(lower[k]))<=1e-6 and abs(bounds['max'][k]-float(upper[k]))<=1e-6
 results.append({'fileLabel':row['fileLabel'],'sha256':row['sha256'],'cells':len(cells),'occupiedCells':len(chosen),'exactVolume':str(volume),'nativeVolume':actual,'error':error,'min':list(map(float,lower)),'max':list(map(float,upper))})
assert results
print(json.dumps({'status':'PASS_SAVED_SUBSET','parentCorpusStatus':receipt['status'],'receiptSha256':hashlib.sha256(raw).hexdigest(),'scope':'Independent rational cell decomposition of raw saved axis-aligned box/Boolean intent versus recorded native Open measurements; no execution or whole-corpus sign-off','results':results},indent=2))
