"""Independent saved-intent/difference and analytic-volume oracle; no browser run."""
from pathlib import Path
import collections,hashlib,json,math,sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'evidence-r2'
receipt=json.loads((root/'receipt.json').read_text());assert receipt['status']=='PASS' and len(receipt['rows'])==17
revision='sha256:dd666902fe926d69cc3c8843f5568c2a3e569f38ff49291baa2f248165b5ea99:8d5e537e0d7f9e12b8ae0eaf239c0be1080934ed12a24bf6e7f849c9135ed5a2'
documents=[];files=[]
for name,radius in [('boolean-chain',3),('boolean-chain-reedited',4)]:
 raw=(root/(name+'.jsketcher.json')).read_bytes();document=json.loads(raw)
 recorded=next(row for row in receipt['rows'] if row['label']==name+' normal native Save and server sync')
 digest=hashlib.sha256(raw).hexdigest();assert digest==recorded['sha256'] and len(raw)==recorded['bytes']
 history=document['project']['model']['history'];counts=collections.Counter(row['type'] for row in history)
 assert counts=={'PLANE':6,'WORKER_SELECTED_PROFILE_EXTRUDE_V2':6,'WORKER_SOLID_BOOLEAN_V1':5,'WORKER_SOLID_EDGE_TREATMENT_V1':2}
 assert len(document['project']['sketches'])==6
 for row in history:
  if row['type']!='PLANE':
   assert row['params']['engineRevision']==revision and row['params']['unit']=='millimeter'
   assert not {'handle','nativeIndex','mesh','triangles'}.intersection(row['params'])
 fillet=next(row for row in history if row['type']=='WORKER_SOLID_EDGE_TREATMENT_V1' and row['params']['kind']=='fillet')
 assert fillet['params']['size']==radius;fillet['params']['size']=0;documents.append(document)
 files.append({'name':name,'sha256':digest,'bytes':len(raw)})
assert documents[0]==documents[1], 'Reopened reedit changed more than the intended fillet size'
volumes=[row['geometry']['nativeVolume'] for row in receipt['rows'] if isinstance(row.get('geometry'),dict) and 'nativeVolume' in row['geometry']]
formulas=[]
for radius in [3,4]:
 # Plate minus circular holes (R5 + four R2), two quarter-circle corner
 # fillets and two unit equal chamfers, all along the20mm extrusion.
 expected=100*50*20-41*math.pi*20-2*radius**2*(1-math.pi/4)*20-20
 assert any(math.isclose(v,expected,rel_tol=1e-12) for v in volumes)
 formulas.append({'filletRadius':radius,'expectedNativeVolume':expected})
print(json.dumps({'status':'PASS','scope':'Independent saved source/difference and analytic-volume checks; no fresh browser execution','files':files,'nativeFeatures':13,'planes':6,'sketches':6,'onlyAuthoredChange':'fillet size3 to4','analyticChecks':formulas},indent=2))
