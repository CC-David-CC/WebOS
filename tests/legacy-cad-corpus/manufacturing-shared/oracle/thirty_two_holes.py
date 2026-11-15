#!/usr/bin/env python3
"""Independent complete exported-artifact oracle for the real 32-circle plate."""
from pathlib import Path
import json,math,sys,io,zipfile
from xml.etree import ElementTree as ET
from check import ENGINE,IDENTITY,NS,sha,identity_transform
from mesh import inspect

def derive(native,binding,creationRows,depth):
 assert native['format']=='codi-jsketcher-project' and native['version']==2 and native['unit']=='millimeter'
 project=native['project'];history=project['model']['history'];assert [x['type'] for x in history]==['PLANE','WORKER_SELECTED_PROFILE_EXTRUDE_V2']
 plane,profile=[x['params'] for x in history];assert plane['orientation']=='XY' and plane['datum'] is None and plane['depth']==0
 assert profile['version']==1 and profile['unit']=='millimeter' and profile['engine']=='occ' and profile['engineRevision']==ENGINE and profile['featureId']==binding['profile']['featureId'] and profile['faceId']==binding['faceId'] and profile['regionId']==binding['regionId'] and profile['bodyPolicy']=='separate' and profile['depth']==depth
 assert binding['last']==binding['profile'] and binding['profile']['bodyId']==binding['profile']['outputId']
 sketches=project['sketches'];assert len(sketches)==1 and sketches[0]['id']==binding['faceId'];source=sketches[0]['data']
 assert source['metadata']['boundaryFrame']=={'origin':[0,0,0],'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}
 objects=source['objects'];assert len(objects)==36 and all(x['role'] is None and x['stage']==0 for x in objects)
 byId={x['id']:x for x in objects};assert len(byId)==36
 segments=[x for x in objects if x['type']=='Segment'];circles=[x for x in objects if x['type']=='Circle'];assert len(segments)==4 and len(circles)==32
 corners=[(0,0),(100,0),(100,50),(0,50)];edges=set()
 for segment in segments:
  p,q=[tuple(segment['data'][k][axis] for axis in ['x','y']) for k in ['a','b']];assert all(math.isfinite(v) for v in p+q) and p!=q
  key=tuple(sorted([p,q]));assert key not in edges;edges.add(key)
 assert edges=={tuple(sorted([corners[i],corners[(i+1)%4]])) for i in range(4)}
 assert len(binding['circleIds'])==32 and len(set(binding['circleIds']))==32 and set(binding['circleIds'])=={x['id'] for x in circles}
 assert len(creationRows)==32
 bores=[]
 for i,row in enumerate(creationRows):
  primitive=row['primitive'];assert row['index']==i and primitive=={'id':binding['circleIds'][i],'kind':'Circle','role':None,'stage':0}
  circle=byId[primitive['id']];data=circle['data'];assert set(data)=={'c','r'} and set(data['c'])=={'x','y'}
  x,y,r=data['c']['x'],data['c']['y'],data['r'];assert all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in [x,y,r])
  assert (x,y,r)==(10+10*(i%8),10+10*(i//8),2);bores.append((x,y,r))
 discovery=binding['discovery'];assert discovery['faceId']==binding['faceId'] and discovery['engineRevision']==ENGINE and discovery['unit']=='millimeter' and discovery['depth']==20
 regions=[x for x in discovery['regions'] if x['regionId']==binding['regionId']];assert len(regions)==1 and regions[0]['support']=='supported'
 descriptor=regions[0]['descriptor'];assert len(descriptor['outerCurveIds'])==4 and set(descriptor['outerCurveIds'])=={x['id'] for x in segments}
 loops=descriptor['holeCurveIds'];assert len(loops)==32 and all(len(x)==1 for x in loops) and len({x[0] for x in loops})==32 and {x[0] for x in loops}==set(binding['circleIds'])
 m=native['manufacturing'];assert m['version']==1 and m['unit']=='millimeter' and len(m['revision'])==71 and m['revision'].startswith('sha256-') and all(c in '0123456789abcdef' for c in m['revision'][7:])
 assert m['materials']==[{'id':'pla','name':'PLA'}] and m['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'}] and len(m['objects'])==len(m['bindings'])==1
 part=m['objects'][0];assert part['id']=='plate' and part['name']=='Mounting plate' and len(part['regions'])==1
 region=part['regions'][0];alias=m['bindings'][0]
 assert region['id']=='main' and region['bodyId']==alias['id'] and alias['featureId']==profile['featureId'] and alias['operationType']=='WORKER_SELECTED_PROFILE_EXTRUDE_V2' and region['materialId']=='pla' and region['appearanceId']=='blue' and region['transform']==IDENTITY
 truth={'bounds':{'min':[0,0,0],'max':[100,50,depth]},'bores':bores,'volume':(5000-math.pi*sum(r*r for x,y,r in bores))*depth}
 return {'truth':truth,'metadata':m,'source':source,'history':history,'producer':profile,'bodyId':binding['profile']['outputId'],'part':part,'sourceCircles':[{'id':binding['circleIds'][i],'center':[x,y],'radius':r} for i,(x,y,r) in enumerate(bores)]}

def check3mf(file,truth):
 raw=file.read_bytes();assert len(raw)<=67108864
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist();assert len(names)==len(set(names)) and set(names)=={'[Content_Types].xml','_rels/','_rels/.rels','3D/','3D/3dmodel.model'} and z.testzip() is None
  rel=ET.fromstring(z.read('_rels/.rels'));assert len(rel)==1 and rel[0].attrib['Target']=='/3D/3dmodel.model' and rel[0].attrib['Type']=='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
  ct=ET.fromstring(z.read('[Content_Types].xml'));assert any(x.attrib.get('Extension')=='model' and x.attrib.get('ContentType')=='application/vnd.ms-package.3dmanufacturing-3dmodel+xml' for x in ct)
  xml=z.read('3D/3dmodel.model');assert len(xml)<=48*1024*1024;decl=dict(value for _,value in ET.iterparse(io.BytesIO(xml),events=['start-ns']));assert decl['codi']=='https://ksu.codes/3mf/metadata/2026'
  model=ET.fromstring(xml);assert model.attrib['unit']=='millimeter';md=model.findall('m:metadata',NS);assert len(md)==2
  metadata={x.attrib['name']:x.text for x in md};assert set(metadata)=={'codi:SourceRevision','codi:ManufacturingBindings'} and metadata['codi:SourceRevision']==truth['metadata']['revision'][7:]
  p=json.loads(metadata['codi:ManufacturingBindings']);assert p['version']==1 and p['revision']==metadata['codi:SourceRevision'] and len(p['parts'])==len(p['materialPairs'])==1
  part=p['parts'][0];assert part['id']==truth['part']['id'] and part['name']==truth['part']['name'] and len(part['regions'])==1
  region=part['regions'][0];assert region['id']=='main' and region['bodyId']==truth['bodyId'] and region['featureId']==truth['producer']['featureId'] and region['engine']=='occ' and region['engineRevision']==ENGINE and region['materialId']=='pla' and region['appearanceId']=='blue'
  pair=p['materialPairs'][0];assert pair['materialId']=='pla' and pair['appearanceId']=='blue' and pair['index']==region['materialIndex']==0
  resources=model.find('m:resources',NS);assert len(resources)==4;resourceIds=[int(x.attrib['id']) for x in resources];assert len(set(resourceIds))==4 and all(x>0 for x in resourceIds)
  objects={int(x.attrib['id']):x for x in resources.findall('m:object',NS)};assert len(objects)==3 and all(x.attrib['type']=='model' for x in objects.values())
  materials=resources.findall('m:basematerials',NS);assert len(materials)==1 and int(materials[0].attrib['id'])==pair['resourceId']==region['materialResourceId'] and len(materials[0])==1 and materials[0][0].attrib=={'name':'PLA','displaycolor':'#3366FF'}
  assert {pair['resourceId'],part['buildResourceId'],region['componentResourceId'],region['meshResourceId']}==set(resourceIds)
  build=model.find('m:build',NS);assert len(build)==1 and int(build[0].attrib['objectid'])==part['buildResourceId'];identity_transform(build[0])
  group=objects[part['buildResourceId']];assert group.attrib['name']==part['name'] and group.find('m:mesh',NS) is None
  refs=group.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['componentResourceId'];identity_transform(refs[0])
  component=objects[region['componentResourceId']];assert component.attrib['name']=='main' and component.find('m:mesh',NS) is None
  refs=component.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['meshResourceId'];identity_transform(refs[0])
  obj=objects[region['meshResourceId']];assert obj.attrib['name']=='main' and int(obj.attrib['pid'])==pair['resourceId'] and int(obj.attrib['pindex'])==0 and obj.find('m:components',NS) is None
  mesh=obj.find('m:mesh',NS);vr=mesh.find('m:vertices',NS);tr=mesh.find('m:triangles',NS);assert all(set(x.attrib)=={'x','y','z'} for x in vr) and all(set(x.attrib)=={'v1','v2','v3'} for x in tr)
  vertices=[tuple(float(x.attrib[k]) for k in ['x','y','z']) for x in vr];triangles=[tuple(int(x.attrib[k]) for k in ['v1','v2','v3']) for x in tr]
 return {'file':file.name,'bytes':len(raw),'sha256':sha(raw),'provenance':p,'geometry':inspect(vertices,triangles,truth['truth'],True)}

def main(folder):
 raw=(folder/'receipt.json').read_bytes();receipt=json.loads(raw)
 assert receipt['status']=='PASS' and receipt['partCase']=='32-holes' and receipt['ownedContextClosed'] and receipt['sharedBrowserDisconnectedOnly'] and receipt['syntheticGeometry'] is False and receipt['syntheticStorage'] is False and receipt['filesystemRace'] is False and receipt['driverPins']==receipt['driverPinsAfter']
 rows=receipt['rows'];find=lambda label:next(x for x in rows if x['label']==label);binding=find('Actual public STEP part authored')['binding'];creationRows=[x for x in rows if x['label']=='Public circle appended']
 pinRows=[x for x in rows if x['label']=='Exact source-bound outer app and critical inner runtime'];assert len(pinRows)==3
 for row in pinRows:assert row['outer']['sha256']==receipt['pins']['outer']['sha256'] and {x['name']:x['sha256'] for x in row['files']}==receipt['pins']['files']
 natives={};nativeFiles={}
 for name in ['material-plate','reopened-material-plate','edited-material-plate']:
  nativeRaw=(folder/(name+'.jsketcher.json')).read_bytes();row=find(name+' normal native Save and server sync');assert len(nativeRaw)==row['bytes'] and sha(nativeRaw)==row['sha256'];natives[name]=json.loads(nativeRaw);nativeFiles[name]={'bytes':len(nativeRaw),'sha256':sha(nativeRaw)}
 assert (folder/'material-plate.jsketcher.json').read_bytes()==(folder/'reopened-material-plate.jsketcher.json').read_bytes()
 initial=derive(natives['material-plate'],binding,creationRows,20);edited=derive(natives['edited-material-plate'],binding,creationRows,25)
 assert initial['source']==edited['source'] and initial['sourceCircles']==edited['sourceCircles'];expected=json.loads(json.dumps(initial['history']));expected[1]['params']['depth']=25;assert expected==edited['history']
 A=dict(initial['metadata']);B=dict(edited['metadata']);A.pop('revision');B.pop('revision');assert A==B and initial['metadata']['revision']!=edited['metadata']['revision']
 results=[]
 for label,truth in [('initial',initial),('edited',edited),('reopened',edited)]:
  row=find(label+' public 3MF export and matching browser/server bytes');result=check3mf(folder/(label+'.3mf'),truth);assert row['sha256']==result['sha256'] and row['bytes']==result['bytes'] and row['authoredStatePreserved'];commit=row['result']
  assert commit['path']==row['file'] and commit['persistence']=='browser' and commit['committed'] is True and commit['dirty'] is False and commit['serverStatus']=='not-verified' and isinstance(commit['version'],str) and commit['version'];result['commit']=commit;results.append(result)
 a,b,c=[x['geometry'] for x in results];assert a['meshVolume']<b['meshVolume'] and b['canonicalOrientedTriangleSha256']==c['canonicalOrientedTriangleSha256'] and results[1]['provenance']==results[2]['provenance']
 print(json.dumps({'status':'PASS','scope':'Independent complete public 32-circle plate exported-artifact oracle; no fresh Native execution, general embedding or slicer/physical-print claim','receiptSha256':sha(raw),'runtimePins':receipt['pins'],'nativeFiles':nativeFiles,'sourceCircles':initial['sourceCircles'],'exports':results,'acceptedSourceAndIntentPreservedExceptDepth20To25':True,'editedReopenedOrientedTrianglesEqual':True,'analyticVolumesMM3':{'initial':(5000-128*math.pi)*20,'edited':(5000-128*math.pi)*25},'tolerances':{'surfaceMm':1e-7,'boundsMm':1e-6,'meshArithmeticMM3':1e-6,'winding':1e-7}},indent=2))

if __name__=='__main__':main(Path(sys.argv[1]).resolve())
