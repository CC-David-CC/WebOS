#!/usr/bin/env python3
"""Independent whole saved-source/two-part/three-region/planar mesh oracle."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
from xml.etree import ElementTree as E
import json,math,hashlib,zipfile,io,sys,subprocess,posixpath,importlib.util
HERE=Path(__file__).parent
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
common=load('enclosure_box_oracle',HERE.parent/'two-material-box-interface/oracle.py')
shell=load('enclosure_shell_oracle',HERE.parent/'shell-manufacturing/oracle.py')
inset=load('enclosure_inset_oracle',HERE.parent/'inset-label-interface/oracle.py')
NS=common.NS;identity=common.identity;sha=common.sha;sub=common.sub;cross=common.cross;dot=common.dot
IDENTITY=[1,0,0,0,1,0,0,0,1,0,0,0]
def derive(native,binding,engine):
 assert native['format']=='codi-jsketcher-project'and native['version']==2 and native['unit']=='millimeter'and native['project']['sketches']==[]
 history=native['project']['model']['history'];assert [x['type']for x in history]==['WORKER_SOLID_BOX_V1','WORKER_SOLID_SHELL_V1','WORKER_SOLID_BOX_V1','WORKER_SOLID_BOX_V1','WORKER_SOLID_BOOLEAN_V1','WORKER_SOLID_BOX_V1'];body,shellP,base,tool,cut,label=[r['params']for r in history]
 names=['source','body','base','tool','lid','label'];rows=[body,shellP,base,tool,cut,label];assert len(set(r['featureId']for r in rows))==6
 for name,row in zip(names,rows):assert row['version']==1 and row['unit']=='millimeter'and row['engine']=='occ'and row['engineRevision']==engine and row['featureId']==binding[name]['featureId']
 boxKeys={'version','unit','engine','engineRevision','featureId','x','y','z','width','depth','height'};assert all(set(r)==boxKeys for r in[body,base,tool,label]);assert set(shellP)=={'version','unit','engine','engineRevision','featureId','target','producerFeatureId','removedFaceIds','thickness','direction'}and shellP['target']==binding['source']['outputId']and shellP['producerFeatureId']==body['featureId']and shellP['direction']=='inward'and shellP['removedFaceIds']==[binding['removedFace']['id']]
 assert binding['removedFace']['role']=='Z_MAX'and binding['removedFace']['originFeatureId']==body['featureId']and binding['removedFace']['geometry']=='plane'
 assert set(cut)=={'version','unit','engine','engineRevision','featureId','kind','a','b'}and cut['kind']=='subtract'and cut['a']==binding['base']['outputId']and cut['b']==binding['tool']['outputId']
 assert [body[k]for k in['x','y','z','depth','height']]==[0,0,0,50,30]and body['width']in[80,100]and shellP['thickness']in[2,3]
 assert [base[k]for k in['x','y','z','depth','height']]==[100,0,0,50,4]and base['width']in[80,100]
 assert [tool[k]for k in['x','y','z','depth','height']]==[125,15,2,20,3]and tool['width']in[30,36]and [label[k]for k in['x','y','z','width','depth','height']]==[125,15,2,tool['width'],20,2]
 w=body['width'];t=shellP['thickness'];lw=base['width'];pw=tool['width'];bodyVolume=w*50*30-(w-2*t)*(50-2*t)*(30-t);lidVolume=lw*50*4-pw*20*2;labelVolume=pw*20*2
 metadata=native['manufacturing'];assert metadata['version']==1 and metadata['unit']=='millimeter'and metadata['materials']==[{'id':'pla','name':'PLA'},{'id':'petg','name':'PETG'}]and metadata['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'},{'id':'white','name':'White','color':'#ffffff'}]
 parts=metadata['objects'];assert [(p['id'],p['name'],[r['id']for r in p['regions']])for p in parts]==[('body','Open enclosure body',['main']),('lid','Inset-label lid',['main','label'])];aliases={b['id']:b for b in metadata['bindings']};assert len(aliases)==3
 regions={('body','main'):('body','WORKER_SOLID_SHELL_V1','pla','blue'),('lid','main'):('lid','WORKER_SOLID_BOOLEAN_V1','pla','blue'),('lid','label'):('label','WORKER_SOLID_BOX_V1','petg','white')}
 for p in parts:
  for r in p['regions']:
   name,op,material,appearance=regions[p['id'],r['id']];alias=aliases[r['bodyId']];assert alias['featureId']==binding[name]['featureId']and alias['operationType']==op and r['transform']==IDENTITY and r['materialId']==material and r['appearanceId']==appearance
 return {'history':history,'metadata':metadata,'binding':binding,'parts':parts,'regionBindings':regions,'dimensions':{'bodyWidth':w,'lidWidth':lw,'thickness':t,'toolWidth':pw,'labelWidth':pw},'bodyDimensions':{'width':w,'depth':50,'height':30,'thickness':t},'fillMin':[125,15,2],'fillMax':[125+pw,35,4],'pocketVolume':lidVolume,'bodyVolume':bodyVolume,'labelVolume':labelVolume,'totalVolume':bodyVolume+lidVolume+labelVolume,'interfaceArea':pw*20+80+pw*4}
def pocket_mesh(v,triangles,truth):
 lo=[100,0,0];hi=[100+truth['dimensions']['lidWidth'],50,4];fillLo=truth['fillMin'];fillHi=truth['fillMax'];pw=fillHi[0]-fillLo[0];surfaces=inset.patches(lo,hi,'outer');surfaces[-1]['area']-=pw*20;surfaces[-1]['opening']=True;inner=inset.patches(fillLo,fillHi,'pocket')[:-1]
 for p in inner:p['sign']=-p['sign']
 surfaces+=inner;areas=defaultdict(list);edges=defaultdict(list);links=defaultdict(list);seen=set();adj=[set()for _ in triangles]
 assert 4<=len(v)<=150000 and 4<=len(triangles)<=100000 and all(len(p)==3 and all(math.isfinite(x)for x in p)for p in v)
 for i,t in enumerate(triangles):
  assert len(t)==len(set(t))==3 and all(isinstance(j,int)and 0<=j<len(v)for j in t);key=tuple(sorted(t));assert key not in seen;seen.add(key);q=[v[j]for j in t];n=cross(sub(q[1],q[0]),sub(q[2],q[0]));matches=[p for p in surfaces if all(point[p['axis']]==p['value']and all(p['lo'][j]<=point[j]<=p['hi'][j]for j in range(3))for point in q)];assert len(matches)==1;surface=matches[0];axis=surface['axis'];assert n[axis]*surface['sign']>0 and all(n[j]==0 for j in range(3)if j!=axis)
  if surface.get('opening'):assert inset.open_rect_area(q,fillLo,fillHi)==0,'Triangle crosses actual pocket opening'
  areas[surface['id']].append(F(abs(n[axis]))/2)
  for j in range(3):
   a,b=t[j],t[(j+1)%3];edges[tuple(sorted((a,b)))].append((a,b,i));links[a].append((b,t[(j+2)%3]))
 assert len(links)==len(v)
 for uses in edges.values():
  assert len(uses)==2 and uses[0][:2]==uses[1][:2][::-1];a,b=uses[0][2],uses[1][2];adj[a].add(b);adj[b].add(a)
 for rows in links.values():
  graph=defaultdict(list)
  for a,b in rows:graph[a].append(b);graph[b].append(a)
  assert all(len(x)==2 for x in graph.values());todo=[next(iter(graph))];visited=set()
  while todo:
   x=todo.pop()
   if x not in visited:visited.add(x);todo.extend(graph[x])
  assert len(visited)==len(graph)
 todo=[0];visited=set()
 while todo:
  x=todo.pop()
  if x not in visited:visited.add(x);todo.extend(adj[x])
 assert len(visited)==len(triangles)and len(v)-len(edges)+len(triangles)==2
 resultAreas={}
 for p in surfaces:
  area=sum(areas[p['id']],F(0));assert area==p['area'];resultAreas[p['id']]=float(area)
 volume=math.fsum(dot(sub(v[a],v[0]),cross(sub(v[b],v[0]),sub(v[c],v[0])))/6 for a,b,c in triangles);assert abs(volume-truth['pocketVolume'])<=1e-6;canonical=[]
 for t in triangles:
  p=tuple(tuple(0. if x==0 else x for x in v[i])for i in t);canonical.append(min(p,p[1:]+p[:1],p[2:]+p[:2]))
 return {'vertices':len(v),'triangles':len(triangles),'euler':2,'surfaceAreas':resultAreas,'meshVolume':volume,'expectedVolume':truth['pocketVolume'],'canonicalTrianglesSha256':sha(json.dumps(sorted(canonical),separators=(',',':')).encode())}
def artifact(file,truth,engine):
 raw=file.read_bytes();assert 0<len(raw)<=67108864
 with zipfile.ZipFile(io.BytesIO(raw))as z:
  assert len(z.namelist())==5 and set(z.namelist())=={'[Content_Types].xml','_rels/','_rels/.rels','3D/','3D/3dmodel.model'}and z.testzip()is None and sum(x.file_size for x in z.infolist())<=64*1024*1024
  rel=E.fromstring(z.read('_rels/.rels'));assert len(rel)==1 and rel[0].attrib['Target']=='/3D/3dmodel.model'and rel[0].attrib['Type']=='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel';ct=E.fromstring(z.read('[Content_Types].xml'));assert any(x.attrib.get('Extension')=='model'and x.attrib.get('ContentType')=='application/vnd.ms-package.3dmanufacturing-3dmodel+xml'for x in ct)
  xml=z.read('3D/3dmodel.model');assert len(xml)<=48*1024*1024;model=E.fromstring(xml);assert model.attrib['unit']=='millimeter';md={x.attrib['name']:x.text for x in model.findall('m:metadata',NS)};assert set(md)=={'codi:SourceRevision','codi:ManufacturingBindings'}and md['codi:SourceRevision']==truth['metadata']['revision'][7:];provenance=json.loads(md['codi:ManufacturingBindings']);assert provenance['version']==1 and provenance['revision']==md['codi:SourceRevision']and len(provenance['parts'])==2 and len(provenance['materialPairs'])==2
  parts=provenance['parts'];assert [(p['id'],p['name'],[r['id']for r in p['regions']])for p in parts]==[('body','Open enclosure body',['main']),('lid','Inset-label lid',['main','label'])]
  resources=model.find('m:resources',NS);assert len(resources)==9;ids=[int(x.attrib['id'])for x in resources];assert len(set(ids))==9;objects={int(x.attrib['id']):x for x in resources.findall('m:object',NS)};assert len(objects)==8 and all(x.attrib['type']=='model'for x in objects.values());materials=resources.findall('m:basematerials',NS);assert len(materials)==1 and len(materials[0])==2;build=model.find('m:build',NS);assert len(build)==2
  pairs={x['materialId']:x for x in provenance['materialPairs']};assert set(pairs)=={'pla','petg'};used=set();results={}
  for part,item in zip(parts,build):
   assert int(item.attrib['objectid'])==part['buildResourceId'];identity(item);group=objects[part['buildResourceId']];assert group.attrib['name']==part['name']and group.find('m:mesh',NS)is None;refs=group.find('m:components',NS);assert len(refs)==len(part['regions']);assert part['buildResourceId']not in used;used.add(part['buildResourceId'])
   for r,ref in zip(part['regions'],refs):
    key,operation,material,appearance=truth['regionBindings'][part['id'],r['id']];b=truth['binding'][key];assert r['bodyId']==b['outputId']and r['featureId']==b['featureId']and r['engine']=='occ'and r['engineRevision']==engine and r['materialId']==material and r['appearanceId']==appearance;pair=pairs[material];assert pair['appearanceId']==appearance and pair['resourceId']==r['materialResourceId']==int(materials[0].attrib['id'])and pair['index']==r['materialIndex'];assert materials[0][pair['index']].attrib=={'name':{'pla':'PLA','petg':'PETG'}[material],'displaycolor':{'blue':'#3366FF','white':'#FFFFFF'}[appearance]}
    assert int(ref.attrib['objectid'])==r['componentResourceId'];identity(ref);component=objects[r['componentResourceId']];assert component.attrib['name']==r['id']and component.find('m:mesh',NS)is None;children=component.find('m:components',NS);assert len(children)==1 and int(children[0].attrib['objectid'])==r['meshResourceId'];identity(children[0]);meshObject=objects[r['meshResourceId']];assert meshObject.attrib['name']==r['id']and int(meshObject.attrib['pid'])==r['materialResourceId']and int(meshObject.attrib['pindex'])==pair['index']and meshObject.find('m:components',NS)is None;assert not used.intersection({r['componentResourceId'],r['meshResourceId']});used.update({r['componentResourceId'],r['meshResourceId']})
    mesh=meshObject.find('m:mesh',NS);vr=mesh.find('m:vertices',NS);tr=mesh.find('m:triangles',NS);assert all(set(x.attrib)=={'x','y','z'}for x in vr)and all(set(x.attrib)=={'v1','v2','v3'}for x in tr);v=[tuple(float(x.attrib[k])for k in ['x','y','z'])for x in vr];t=[tuple(int(x.attrib[k])for k in ['v1','v2','v3'])for x in tr]
    geometry=shell.mesh(v,t,truth['bodyDimensions'])if key=='body'else pocket_mesh(v,t,truth)if key=='lid'else common.inspect_mesh(v,t,[truth['fillMin'],truth['fillMax']]);points=[]
    if key!='body':
     cx=(truth['fillMin'][0]+truth['fillMax'][0])/2
     for p in [[cx,25,3],[cx,25,1],[110,25,3],[cx,25,4.5],[125+truth['dimensions']['toolWidth']+.5,25,3],[100+truth['dimensions']['lidWidth']+1,25,2]]:
      fill=all(truth['fillMin'][j]<p[j]<truth['fillMax'][j]for j in range(3));base=100<p[0]<100+truth['dimensions']['lidWidth']and 0<p[1]<50 and 0<p[2]<4;expected=base and not fill if key=='lid'else fill;observed=common.winding(v,t,p);assert abs(observed-int(expected))<=1e-7;points.append({'point':p,'material':expected,'winding':observed})
    results[key]={'partId':part['id'],'regionId':r['id'],'materialId':material,'geometry':geometry,'materialPoints':points}
  assert used==set(objects)
 A=results['lid']['geometry']['surfaceAreas'];B=results['label']['geometry']['surfaceAreas'];interfaces=[]
 for p,q in [('pocket00','(0, 0)'),('pocket01','(0, 1)'),('pocket10','(1, 0)'),('pocket11','(1, 1)'),('pocket20','(2, 0)')]:assert A[p]==B[q]>0;interfaces.append({'pocketPatch':p,'labelPatch':q,'area':A[p]})
 assert sum(x['area']for x in interfaces)==truth['interfaceArea'];total=sum(x['geometry']['meshVolume']for x in results.values());assert abs(total-truth['totalVolume'])<=1e-6
 return {'file':file.name,'sha256':sha(raw),'bytes':len(raw),'buildItems':2,'regions':results,'interfaceArea':truth['interfaceArea'],'interfaces':interfaces,'totalVolume':total,'provenance':provenance}
def main(folder,repo):
 raw=(folder/'receipt.json').read_bytes();r=json.loads(raw);assert r['status']=='PASS'and r['ownedContextClosed']and r['sharedBrowserDisconnectedOnly']and not r['syntheticGeometry']and not r['syntheticStorage']and not r['sourceSeeds']and r['sourcePins']==r['sourcePinsAfter'];commit=r['driverSourceCommit'];assert len(commit)==40
 for name,digest in r['sourcePins'].items():
  target=posixpath.normpath('test/agent-cad-corpus/source-bound-enclosure/'+name);assert not target.startswith('../');assert sha(subprocess.check_output(['git','-C',str(repo),'show',commit+':'+target]))==digest
 runtime=[x for x in r['rows']if x['label']=='Exact actual composed source/Native/outer byte pins'];assert len(runtime)==3
 for x in runtime:assert x['outer']['sha256']==r['pins']['outer']['sha256']and {p['name']:p['sha256']for p in x['files']}==r['pins']['files']
 truths={};saved={}
 for row in r['saved']:
  data=(folder/row['file']).read_bytes();assert len(data)==row['bytes']and sha(data)==row['sha256'];truth=derive(json.loads(data),r['binding'],r['engineRevision']);assert truth['dimensions']==row['dimensions'];truths[row['label']]=truth;saved[row['label']]={'bytes':len(data),'sha256':sha(data)}
 assert set(truths)=={'initial-source','initial-reopened-source','edited-source','reopened-source'}and saved['initial-source']==saved['initial-reopened-source']and saved['edited-source']==saved['reopened-source']
 initial=truths['initial-source'];edited=truths['edited-source'];assert initial['dimensions']=={'bodyWidth':80,'lidWidth':80,'thickness':2,'toolWidth':30,'labelWidth':30}and edited['dimensions']=={'bodyWidth':100,'lidWidth':100,'thickness':3,'toolWidth':36,'labelWidth':36};assert initial['bodyVolume']==22112 and initial['pocketVolume']+initial['labelVolume']==16000 and initial['totalVolume']==38112 and edited['totalVolume']==58328
 changed=json.loads(json.dumps(initial['history']));changed[0]['params']['width']=100;changed[1]['params']['thickness']=3;changed[2]['params']['width']=100;changed[3]['params']['width']=36;changed[5]['params']['width']=36;assert changed==edited['history'];old=json.loads(json.dumps(initial['metadata']));new=json.loads(json.dumps(edited['metadata']));del old['revision'];del new['revision'];assert old==new,'Part/region/material/producer IDs changed during explicit rebind'
 outputs=[]
 for row in r['exports']:
  truth=truths[row['label']+'-source'];value=artifact(folder/row['file'],truth,r['engineRevision']);assert value['sha256']==row['sha256']and value['bytes']==row['bytes']and row['acceptedStatePreserved'];c=row['result'];assert c['path']==row['path']and c['persistence']=='browser'and c['committed']is True and c['dirty']is False and c['serverStatus']=='not-verified';outputs.append(value)
 assert len(outputs)==3;assert outputs[1]['provenance']==outputs[2]['provenance'];assert [outputs[1]['regions'][k]['geometry']['canonicalTrianglesSha256']for k in ['body','lid','label']]==[outputs[2]['regions'][k]['geometry']['canonicalTrianglesSha256']for k in ['body','lid','label']]
 print(json.dumps({'status':'PASS','scope':'Independent entire actual saved-intent/3MF ZIP XML two-builditem three-region shell+inset fixture, exact planar patches/manifold/volume/materials/5interfaces; no new Native execution, general formula capability, assembly, slicer or physical-print claim','receiptSha256':sha(raw),'driverSourceCommit':commit,'runtimePins':r['pins'],'nativeSaves':saved,'exports':outputs,'tolerances':{'planarCoordinatesAndInsetAreas':'exact integer/rational fixture','bodyPatchAreaMm2':1e-6,'volumeMm3':1e-6,'winding':1e-7}},indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
