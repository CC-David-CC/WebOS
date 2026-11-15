#!/usr/bin/env python3
"""Whole-file oracle for the actual separate plate/box public export workflow."""
from pathlib import Path
import math,json,sys,io,zipfile
from xml.etree import ElementTree as ET
from check import ENGINE,IDENTITY,NS,sha,identity_transform
from mesh import inspect

def derive(native,binding,depth):
 assert native['format']=='codi-jsketcher-project' and native['version']==2 and native['unit']=='millimeter'
 project=native['project'];history=project['model']['history']
 assert [x['type'] for x in history]==['PLANE','WORKER_SELECTED_PROFILE_EXTRUDE_V2','WORKER_THROUGH_HOLES_V1','WORKER_SOLID_BOX_V1']
 plane,profile,hole,box=[x['params'] for x in history]
 assert plane['orientation']=='XY' and plane['datum'] is None and plane['depth']==0
 for params in [profile,hole,box]:assert params['version']==1 and params['engine']=='occ' and params['engineRevision']==ENGINE and params['unit']=='millimeter'
 assert profile['faceId']==binding['faceId'] and profile['regionId']==binding['regionId'] and profile['featureId']==binding['profile']['featureId'] and profile['depth']==depth and profile['bodyPolicy']=='separate'
 assert hole['featureId']==binding['hole']['featureId'] and hole['sourceFeatureId']==hole['producerFeatureId']==profile['featureId'] and hole['sourceFaceId']==profile['faceId'] and hole['sourceRegionId']==profile['regionId'] and hole['target']==binding['profile']['outputId'] and hole['kind']=='centered-through' and hole['diameter']==10
 assert box['featureId']==binding['box']['featureId'] and [box[k] for k in ['x','y','z','width','depth','height']]==[120,0,0,10,20,30]
 sketches=project['sketches'];assert len(sketches)==1 and sketches[0]['id']==binding['faceId'];source=sketches[0]['data']
 assert source['metadata']['boundaryFrame']=={'origin':[0,0,0],'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}
 objects=source['objects'];assert len(objects)==4 and all(x['type']=='Segment' and x['role'] is None for x in objects)
 ids=[x['id'] for x in objects];assert len(set(ids))==4;edges=set()
 for segment in objects:
  p,q=[tuple(segment['data'][k][axis] for axis in ['x','y']) for k in ['a','b']]
  assert all(math.isfinite(v) for v in p+q) and p!=q
  key=tuple(sorted([p,q]));assert key not in edges;edges.add(key)
 corners=[(0,0),(100,0),(100,50),(0,50)]
 assert edges=={tuple(sorted([corners[i],corners[(i+1)%4]])) for i in range(4)}
 discovery=binding['discovery'];assert discovery['faceId']==binding['faceId'] and discovery['engineRevision']==ENGINE and discovery['unit']=='millimeter'
 rows=[x for x in discovery['regions'] if x['regionId']==binding['regionId']]
 assert len(rows)==1 and rows[0]['support']=='supported' and set(rows[0]['descriptor']['outerCurveIds'])==set(ids) and rows[0]['descriptor']['holeCurveIds']==[]
 m=native['manufacturing'];assert m['version']==1 and m['unit']=='millimeter' and len(m['revision'])==71 and m['revision'].startswith('sha256-') and all(c in '0123456789abcdef' for c in m['revision'][7:])
 assert m['materials']==[{'id':'pla','name':'PLA'}] and m['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'}]
 assert len(m['objects'])==len(m['bindings'])==2
 parts={x['id']:x for x in m['objects']};aliases={x['id']:x for x in m['bindings']};assert set(parts)=={'plate','box'} and len(aliases)==2
 expected={}
 for partId,name,producer,operation,public in [('plate','Mounting plate',hole,'WORKER_THROUGH_HOLES_V1',binding['hole']),('box','Separate box',box,'WORKER_SOLID_BOX_V1',binding['box'])]:
  part=parts[partId];assert part['name']==name and len(part['regions'])==1
  region=part['regions'][0];alias=aliases[region['bodyId']]
  assert region['id']=='main' and region['materialId']=='pla' and region['appearanceId']=='blue' and region['transform']==IDENTITY and alias['featureId']==producer['featureId'] and alias['operationType']==operation
  truth=({'bounds':{'min':[0,0,0],'max':[100,50,depth]},'bores':[(50,25,5)],'volume':(5000-25*math.pi)*depth} if partId=='plate' else {'bounds':{'min':[box['x'],box['y'],box['z']],'max':[box['x']+box['width'],box['y']+box['depth'],box['z']+box['height']]},'bores':[],'volume':box['width']*box['depth']*box['height']})
  expected[partId]={'part':part,'producer':producer,'bodyId':public['outputId'],'truth':truth}
 return {'metadata':m,'source':source,'history':history,'parts':expected}

def check3mf(file,truth):
 raw=file.read_bytes();assert len(raw)<=67108864
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist();assert len(names)==len(set(names)) and set(names)=={'[Content_Types].xml','_rels/','_rels/.rels','3D/','3D/3dmodel.model'} and z.testzip() is None
  rel=ET.fromstring(z.read('_rels/.rels'));assert len(rel)==1 and rel[0].attrib['Target']=='/3D/3dmodel.model' and rel[0].attrib['Type']=='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
  ct=ET.fromstring(z.read('[Content_Types].xml'));assert any(x.attrib.get('Extension')=='model' and x.attrib.get('ContentType')=='application/vnd.ms-package.3dmanufacturing-3dmodel+xml' for x in ct)
  xml=z.read('3D/3dmodel.model');assert len(xml)<=48*1024*1024
  decl=dict(value for _,value in ET.iterparse(io.BytesIO(xml),events=['start-ns']));assert decl['codi']=='https://ksu.codes/3mf/metadata/2026'
  model=ET.fromstring(xml);assert model.attrib['unit']=='millimeter';md=model.findall('m:metadata',NS);assert len(md)==2
  metadata={x.attrib['name']:x.text for x in md};assert set(metadata)=={'codi:SourceRevision','codi:ManufacturingBindings'} and metadata['codi:SourceRevision']==truth['metadata']['revision'][7:]
  p=json.loads(metadata['codi:ManufacturingBindings']);assert p['version']==1 and p['revision']==metadata['codi:SourceRevision'] and len(p['parts'])==2 and len(p['materialPairs'])==1
  pair=p['materialPairs'][0];assert pair['materialId']=='pla' and pair['appearanceId']=='blue' and pair['index']==0
  resources=model.find('m:resources',NS);assert len(resources)==7;resourceIds=[int(x.attrib['id']) for x in resources];assert len(set(resourceIds))==7 and all(x>0 for x in resourceIds)
  objects={int(x.attrib['id']):x for x in resources.findall('m:object',NS)};assert len(objects)==6 and all(x.attrib['type']=='model' for x in objects.values())
  materials=resources.findall('m:basematerials',NS);assert len(materials)==1 and int(materials[0].attrib['id'])==pair['resourceId'] and len(materials[0])==1 and materials[0][0].attrib=={'name':'PLA','displaycolor':'#3366FF'}
  build=model.find('m:build',NS);assert len(build)==2
  seenIds=set();seenResources={pair['resourceId']};seenBodies=set();geometry={}
  for part,item in zip(p['parts'],build):
   partId=part['id'];assert partId in truth['parts'] and partId not in seenIds;seenIds.add(partId);expected=truth['parts'][partId]
   assert part['name']==expected['part']['name'] and len(part['regions'])==1 and int(item.attrib['objectid'])==part['buildResourceId'];identity_transform(item)
   region=part['regions'][0];assert region['id']=='main' and region['bodyId']==expected['bodyId'] and region['bodyId'] not in seenBodies;seenBodies.add(region['bodyId'])
   assert region['featureId']==expected['producer']['featureId'] and region['engine']=='occ' and region['engineRevision']==ENGINE and region['materialId']=='pla' and region['appearanceId']=='blue' and region['materialResourceId']==pair['resourceId'] and region['materialIndex']==0
   newIds={part['buildResourceId'],region['componentResourceId'],region['meshResourceId']};assert len(newIds)==3 and not(newIds&seenResources);seenResources.update(newIds)
   group=objects[part['buildResourceId']];assert group.attrib['name']==part['name'] and group.find('m:mesh',NS) is None
   refs=group.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['componentResourceId'];identity_transform(refs[0])
   component=objects[region['componentResourceId']];assert component.attrib['name']=='main' and component.find('m:mesh',NS) is None
   refs=component.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['meshResourceId'];identity_transform(refs[0])
   obj=objects[region['meshResourceId']];assert obj.attrib['name']=='main' and int(obj.attrib['pid'])==pair['resourceId'] and int(obj.attrib['pindex'])==0 and obj.find('m:components',NS) is None
   mesh=obj.find('m:mesh',NS);vr=mesh.find('m:vertices',NS);tr=mesh.find('m:triangles',NS)
   assert all(set(x.attrib)=={'x','y','z'} for x in vr) and all(set(x.attrib)=={'v1','v2','v3'} for x in tr)
   vertices=[tuple(float(x.attrib[k]) for k in ['x','y','z']) for x in vr];triangles=[tuple(int(x.attrib[k]) for k in ['v1','v2','v3']) for x in tr]
   geometry[partId]=inspect(vertices,triangles,expected['truth'],True)
  assert seenIds=={'plate','box'} and seenResources==set(resourceIds)
 return {'file':file.name,'bytes':len(raw),'sha256':sha(raw),'provenance':p,'geometry':geometry}

def main(folder):
 receiptRaw=(folder/'receipt.json').read_bytes();r=json.loads(receiptRaw)
 assert r['status']=='PASS' and r['partCase']=='two-outputs' and r['ownedContextClosed'] and r['sharedBrowserDisconnectedOnly'] and r['syntheticGeometry'] is False and r['syntheticStorage'] is False and r['filesystemRace'] is False and r['driverPins']==r['driverPinsAfter']
 rows=r['rows'];find=lambda label:next(x for x in rows if x['label']==label);binding=find('Actual public STEP part authored')['binding']
 pins=[x for x in rows if x['label']=='Exact source-bound outer app and critical inner runtime'];assert len(pins)==3
 for row in pins:assert row['outer']['sha256']==r['pins']['outer']['sha256'] and {x['name']:x['sha256'] for x in row['files']}==r['pins']['files']
 natives={};files={}
 for name in ['material-plate','reopened-material-plate','edited-material-plate']:
  raw=(folder/(name+'.jsketcher.json')).read_bytes();row=find(name+' normal native Save and server sync');assert len(raw)==row['bytes'] and sha(raw)==row['sha256'];natives[name]=json.loads(raw);files[name]={'bytes':len(raw),'sha256':sha(raw)}
 assert (folder/'material-plate.jsketcher.json').read_bytes()==(folder/'reopened-material-plate.jsketcher.json').read_bytes()
 initial=derive(natives['material-plate'],binding,20);edited=derive(natives['edited-material-plate'],binding,25)
 assert initial['source']==edited['source'];expected=json.loads(json.dumps(initial['history']));expected[1]['params']['depth']=25;assert expected==edited['history']
 A=dict(initial['metadata']);B=dict(edited['metadata']);A.pop('revision');B.pop('revision');assert A==B and initial['metadata']['revision']!=edited['metadata']['revision']
 results=[]
 for label,truth in [('initial',initial),('edited',edited),('reopened',edited)]:
  row=find(label+' public 3MF export and matching browser/server bytes');result=check3mf(folder/(label+'.3mf'),truth)
  assert row['sha256']==result['sha256'] and row['bytes']==result['bytes'] and row['authoredStatePreserved'];commit=row['result']
  assert commit['path']==row['file'] and commit['persistence']=='browser' and commit['committed'] is True and commit['dirty'] is False and commit['serverStatus']=='not-verified' and isinstance(commit['version'],str) and commit['version']
  result['commit']=commit;results.append(result)
 a,b,c=[x['geometry'] for x in results]
 assert a['plate']['meshVolume']<b['plate']['meshVolume']
 assert len({x['box']['canonicalOrientedTriangleSha256'] for x in [a,b,c]})==1
 assert b['plate']['canonicalOrientedTriangleSha256']==c['plate']['canonicalOrientedTriangleSha256'] and results[1]['provenance']==results[2]['provenance']
 print(json.dumps({'status':'PASS','scope':'Independent complete separate-parts public workflow ZIP/XML/source/mesh oracle; no new Native execution or general nesting/physical-print claim','receiptSha256':sha(receiptRaw),'runtimePins':r['pins'],'nativeFiles':files,'exports':results,'boxUnchangedAcrossDepthEditAndOpen':True,'editedReopenedPlateOrientedTrianglesEqual':True,'sameLocalRegionIdAcrossSeparateParts':'main is scoped by part; generated resources and public bodies remain distinct','tolerances':{'surfaceMm':1e-7,'boundsMm':1e-6,'meshArithmeticMM3':1e-6,'winding':1e-7}},indent=2))

if __name__=='__main__':main(Path(sys.argv[1]).resolve())
