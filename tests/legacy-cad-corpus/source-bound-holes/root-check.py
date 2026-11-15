import json,math,hashlib,sys
from pathlib import Path
root=Path(sys.argv[1]);r=json.loads((root/'receipt.json').read_text());assert r['status']=='PASS' and len(r['rows'])==19
rev='sha256:dd666902fe926d69cc3c8843f5568c2a3e569f38ff49291baa2f248165b5ea99:8d5e537e0d7f9e12b8ae0eaf239c0be1080934ed12a24bf6e7f849c9135ed5a2'
files=[];documents=[]
for stem,d in [('source-bound-holes',12),('source-bound-holes-reedited',14)]:
 raw=(root/(stem+'.jsketcher.json')).read_bytes();doc=json.loads(raw);assert doc['format']=='codi-jsketcher-project' and doc['version']==2 and doc['unit']=='millimeter'
 p=doc['project'];h=p['model']['history'];assert [f['type'] for f in h]==['PLANE','WORKER_SELECTED_PROFILE_EXTRUDE_V2','WORKER_THROUGH_HOLES_V1','WORKER_THROUGH_HOLES_V1','WORKER_SOLID_EDGE_TREATMENT_V1','WORKER_SOLID_EDGE_TREATMENT_V1'];assert len(p['sketches'])==1
 base,center,corners,fillet,chamfer=[f['params'] for f in h[1:]]
 assert all(v['engine']=='occ' and v['engineRevision']==rev and v['unit']=='millimeter' for v in [base,center,corners,fillet,chamfer]);assert base['depth']==25 and base['bodyPolicy']=='separate'
 for v,expected,producer in [(center,{'kind':'centered-through','diameter':d},base),(corners,{'kind':'four-corner-through','diameter':5,'offsetX':12,'offsetY':10},center)]:
  assert set(v)=={'version','unit','engine','engineRevision','featureId','target','producerFeatureId','sourceFeatureId','sourceFaceId','sourceRegionId',*expected}
  assert all(v[k]==val for k,val in expected.items());assert v['sourceFeatureId']==base['featureId'] and v['sourceFaceId']==base['faceId'] and v['sourceRegionId']==base['regionId']
  assert v['producerFeatureId']==producer['featureId'] and v['target']=='worker-solid:1:'+json.dumps([producer['featureId'],'body'],separators=(',',':'))
 assert fillet['kind']=='fillet' and fillet['size']==3 and chamfer['kind']=='chamfer-equal' and chamfer['size']==1
 sketch=p['sketches'][0];assert sketch['id']==base['faceId'];entities=sketch['data']['objects'];assert len(entities)==4 and all(e['type']=='Segment' for e in entities)
 pairs=[(e['data']['a']['x'],e['data']['a']['y']) for e in entities];assert pairs==[(0,0),(150,0),(150,30),(0,30)]
 assert not p['model']['assembly'];assert p['model']['expressions']=='';assert p['model']['counters']['featureId']==6
 v=(150*30 - math.pi*((d/2)**2+4*(5/2)**2)-2*(3**2-math.pi*3**2/4)-1**2)*25
 files.append({'file':stem+'.jsketcher.json','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'centerDiameter':d,'expectedNativeVolume':v,'authoredFeatures':len(h),'sourceSketches':1,'semanticHoleFeatures':2,'authoredToolBooleans':0});documents.append(doc)
# Exact save/reopen/edit persistence invariant: the two complete native files
# differ ONLY in one authored center diameter. No blanket metadata exclusions.
assert documents[0]['project']['model']['history'][2]['params']['diameter']==12
documents[0]['project']['model']['history'][2]['params']['diameter']=14
assert documents[0]==documents[1]
measures=[]
def visit(v):
 if isinstance(v,dict):
  if 'expected' in v and 'nativeVolume' in v:
   e=v['expected'];area=e['width']*e['height']-math.pi*((e['centerDiameter']/2)**2+4*(e['cornerDiameter']/2)**2)-2*(e['fillet']**2-math.pi*e['fillet']**2/4)-e['chamfer']**2
   truth=area*e['depth'];assert math.isclose(v['nativeVolume'],truth,rel_tol=1e-10,abs_tol=1e-6)
   bounds=v['nativeBounds'];want={'min':[0,0,0],'max':[e['width'],e['height'],e['depth']]};tol=64*math.ulp(max(1,e['width'],e['height'],e['depth']));assert set(bounds)=={'min','max'} and all(len(bounds[k])==3 and all(abs(a-b)<=tol for a,b in zip(bounds[k],want[k])) for k in want);assert len(v['selections']['plan']['sourceContexts'])==1
   measures.append({'expected':truth,'native':v['nativeVolume']})
  for x in v.values():visit(x)
 elif isinstance(v,list):
  for x in v:visit(x)
visit(r['rows']);assert len(measures)==13
print(json.dumps({'status':'PASS','scope':'Independent root native-file field checks, exact one-field full-document comparison, and analytic volume/bounds/origin checks of recorded app observations; no fresh native execution or full Gate1 claim','receiptSHA256':hashlib.sha256((root/'receipt.json').read_bytes()).hexdigest(),'rows':len(r['rows']),'files':files,'onlySavedDifference':'center hole diameter 12 to 14','measuredStates':len(measures),'lastNativeVolume':measures[-1]['native']},indent=2))
