#!/usr/bin/env python3
"""Independent complete saved-source/ZIP/XML/planar inset-lid fixture oracle."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
from xml.etree import ElementTree as ET
import math,json,hashlib,zipfile,io,sys,subprocess,posixpath,importlib.util
spec=importlib.util.spec_from_file_location('retained_box_mesh_oracle',Path(__file__).parent.parent/'two-material-box-interface/oracle.py');common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
NS=common.NS;IDENTITY=common.IDENTITY;sha=common.sha;cross=common.cross;sub=common.sub;dot=common.dot
def open_rect_area(triangle,lo,hi):
 p=[tuple(F(x)for x in q[:2])for q in triangle]
 for axis,value,sign in[(0,F(lo[0]),1),(0,F(hi[0]),-1),(1,F(lo[1]),1),(1,F(hi[1]),-1)]:
  out=[]
  for i,a in enumerate(p):
   b=p[(i+1)%len(p)];insideA=(a[axis]-value)*sign>=0;insideB=(b[axis]-value)*sign>=0
   if insideA:out.append(a)
   if insideA!=insideB:
    ratio=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+ratio*(b[j]-a[j])for j in range(2)))
  p=out
  if not p:return F(0)
 return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1]for i in range(len(p))))/2
def patches(lo,hi,prefix):
 result=[]
 for axis in range(3):
  for side in range(2):
   a=list(lo);b=list(hi);value=[lo,hi][side][axis];a[axis]=b[axis]=value;area=math.prod(hi[j]-lo[j]for j in range(3)if j!=axis);result.append({'id':prefix+str(axis)+str(side),'axis':axis,'value':value,'sign':1 if side else -1,'lo':a,'hi':b,'area':area})
 return result
def pocket_mesh(vertices,triangles,truth):
 lo=[0,0,0];hi=[80,50,4];x,y,z=truth['fillMin'];xx,yy,zz=truth['fillMax'];fillLo=[x,y,z];fillHi=[xx,yy,zz]
 surfaces=patches(lo,hi,'outer');surfaces[-1]['area']-=(xx-x)*(yy-y);surfaces[-1]['opening']=True
 inner=patches(fillLo,fillHi,'pocket')[:-1]
 for p in inner:p['sign']=-p['sign']
 surfaces+=inner;areas=defaultdict(list);edges=defaultdict(list);links=defaultdict(list);seen=set();adj=[set()for _ in triangles]
 assert 4<=len(vertices)<=150000 and 4<=len(triangles)<=100000 and all(len(p)==3 and all(math.isfinite(x)for x in p)for p in vertices)
 for i,t in enumerate(triangles):
  assert len(t)==len(set(t))==3 and all(isinstance(j,int)and 0<=j<len(vertices)for j in t);key=tuple(sorted(t));assert key not in seen;seen.add(key)
  q=[vertices[j]for j in t];n=cross(sub(q[1],q[0]),sub(q[2],q[0]));matches=[p for p in surfaces if all(point[p['axis']]==p['value']and all(p['lo'][j]<=point[j]<=p['hi'][j]for j in range(3))for point in q)];assert len(matches)==1;surface=matches[0];axis=surface['axis'];assert n[axis]*surface['sign']>0 and all(n[j]==0 for j in range(3)if j!=axis)
  if surface.get('opening'):assert open_rect_area(q,fillLo,fillHi)==0,'Triangle crosses pocket opening'
  areas[surface['id']].append(F(abs(n[axis]))/2)
  for j in range(3):
   a,b=t[j],t[(j+1)%3];edges[tuple(sorted((a,b)))].append((a,b,i));links[a].append((b,t[(j+2)%3]))
 assert len(links)==len(vertices)
 for uses in edges.values():
  assert len(uses)==2 and uses[0][:2]==uses[1][:2][::-1];a,b=uses[0][2],uses[1][2];adj[a].add(b);adj[b].add(a)
 for rows in links.values():
  graph=defaultdict(list)
  for a,b in rows:graph[a].append(b);graph[b].append(a)
  assert all(len(v)==2 for v in graph.values());todo=[next(iter(graph))];visited=set()
  while todo:
   a=todo.pop()
   if a not in visited:visited.add(a);todo.extend(graph[a])
  assert len(visited)==len(graph)
 todo=[0];visited=set()
 while todo:
  a=todo.pop()
  if a not in visited:visited.add(a);todo.extend(adj[a])
 assert len(visited)==len(triangles)and len(vertices)-len(edges)+len(triangles)==2
 observedAreas={}
 for surface in surfaces:
  area=sum(areas[surface['id']],F(0));assert area==surface['area'];observedAreas[surface['id']]=float(area)
 volume=math.fsum(dot(sub(vertices[a],vertices[0]),cross(sub(vertices[b],vertices[0]),sub(vertices[c],vertices[0])))/6 for a,b,c in triangles);assert abs(volume-truth['pocketVolume'])<=1e-6
 canonical=[]
 for t in triangles:
  q=tuple(tuple(0. if x==0 else x for x in vertices[i])for i in t);canonical.append(min(q,q[1:]+q[:1],q[2:]+q[:2]))
 return {'vertices':len(vertices),'triangles':len(triangles),'euler':2,'surfaceAreas':observedAreas,'meshVolume':volume,'expectedVolume':truth['pocketVolume'],'canonicalTrianglesSha256':sha(json.dumps(sorted(canonical),separators=(',',':')).encode())}
def derive(native,binding,engine):
 assert native['format']=='codi-jsketcher-project'and native['version']==2 and native['unit']=='millimeter'and native['project']['sketches']==[]
 history=native['project']['model']['history'];assert [x['type']for x in history]==['WORKER_SOLID_BOX_V1','WORKER_SOLID_BOX_V1','WORKER_SOLID_BOOLEAN_V1','WORKER_SOLID_BOX_V1'];base,tool,cut,label=[x['params']for x in history]
 for key,p in [('base',base),('tool',tool),('pocket',cut),('label',label)]:assert p['version']==1 and p['unit']=='millimeter'and p['engine']=='occ'and p['engineRevision']==engine and p['featureId']==binding[key]['featureId']
 keys={'version','unit','engine','engineRevision','featureId','x','y','z','width','depth','height'};assert all(set(p)==keys for p in[base,tool,label])
 assert set(cut)=={'version','unit','engine','engineRevision','featureId','kind','a','b'}and cut['kind']=='subtract'and cut['a']==binding['base']['outputId']and cut['b']==binding['tool']['outputId']
 assert [base[k]for k in['x','y','z','width','depth','height']]==[0,0,0,80,50,4];width=tool['width'];assert width in[30,36]and [tool[k]for k in['x','y','z','depth','height']]==[25,15,2,20,3]and [label[k]for k in['x','y','z','width','depth','height']]==[25,15,2,width,20,2]
 m=native['manufacturing'];assert m['version']==1 and m['unit']=='millimeter'and m['revision'].startswith('sha256-')and len(m['revision'])==71 and m['materials']==[{'id':'pla','name':'PLA'},{'id':'petg','name':'PETG'}]and m['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'},{'id':'white','name':'White','color':'#ffffff'}]
 assert len(m['objects'])==1 and len(m['bindings'])==2;part=m['objects'][0];assert part['id']=='lid'and part['name']=='Inset-label lid'and [x['id']for x in part['regions']]==['lid','label'];aliases={x['id']:x for x in m['bindings']};assert len(aliases)==2
 for r in part['regions']:
  k='pocket'if r['id']=='lid'else'label';b=aliases[r['bodyId']];assert b['featureId']==binding[k]['featureId']and b['operationType']==('WORKER_SOLID_BOOLEAN_V1'if k=='pocket'else'WORKER_SOLID_BOX_V1')and r['transform']==IDENTITY and(r['materialId'],r['appearanceId'])==({'lid':('pla','blue'),'label':('petg','white')}[r['id']])
 return {'history':history,'metadata':m,'part':part,'width':width,'fillMin':[25,15,2],'fillMax':[25+width,35,4],'pocketVolume':16000-width*40,'labelVolume':width*40,'interfaceAreas':{'floor':width*20,'twoXWalls':80,'twoYWalls':width*4},'binding':binding}
def artifact(file,truth,engine):
 raw=file.read_bytes();assert 0<len(raw)<=67108864
 with zipfile.ZipFile(io.BytesIO(raw))as z:
  assert len(z.namelist())==5 and set(z.namelist())=={'[Content_Types].xml','_rels/','_rels/.rels','3D/','3D/3dmodel.model'}and sum(x.file_size for x in z.infolist())<=64*1024*1024 and z.testzip()is None
  rel=ET.fromstring(z.read('_rels/.rels'));assert len(rel)==1 and rel[0].attrib['Target']=='/3D/3dmodel.model'and rel[0].attrib['Type']=='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel';ct=ET.fromstring(z.read('[Content_Types].xml'));assert any(x.attrib.get('Extension')=='model'and x.attrib.get('ContentType')=='application/vnd.ms-package.3dmanufacturing-3dmodel+xml'for x in ct)
  xml=z.read('3D/3dmodel.model');assert len(xml)<=48*1024*1024;namespaces=dict(x for _,x in ET.iterparse(io.BytesIO(xml),events=['start-ns']));assert namespaces['codi']=='https://ksu.codes/3mf/metadata/2026';model=ET.fromstring(xml);assert model.attrib['unit']=='millimeter';md=model.findall('m:metadata',NS);assert len(md)==2;md={x.attrib['name']:x.text for x in md};assert set(md)=={'codi:SourceRevision','codi:ManufacturingBindings'}and md['codi:SourceRevision']==truth['metadata']['revision'][7:];provenance=json.loads(md['codi:ManufacturingBindings']);assert provenance['version']==1 and provenance['revision']==md['codi:SourceRevision']and len(provenance['parts'])==1 and len(provenance['materialPairs'])==2
  part=provenance['parts'][0];assert part['id']=='lid'and part['name']=='Inset-label lid'and [x['id']for x in part['regions']]==['lid','label'];resources=model.find('m:resources',NS);assert len(resources)==6;ids=[int(x.attrib['id'])for x in resources];assert len(set(ids))==6 and min(ids)>0;objects={int(x.attrib['id']):x for x in resources.findall('m:object',NS)};assert len(objects)==5 and all(x.attrib['type']=='model'for x in objects.values());materials=resources.findall('m:basematerials',NS);assert len(materials)==1 and len(materials[0])==2
  builds=model.find('m:build',NS);assert len(builds)==1 and int(builds[0].attrib['objectid'])==part['buildResourceId'];common.identity(builds[0]);group=objects[part['buildResourceId']];assert group.attrib['name']=='Inset-label lid'and group.find('m:mesh',NS)is None;refs=group.find('m:components',NS);assert len(refs)==2;pairs={x['materialId']:x for x in provenance['materialPairs']};assert set(pairs)=={'pla','petg'};used={part['buildResourceId']};results=[]
  for i,r in enumerate(part['regions']):
   name=r['id'];key='pocket'if name=='lid'else'label';binding=truth['binding'][key];material,appearance,color={'lid':('pla','blue','#3366FF'),'label':('petg','white','#FFFFFF')}[name]
   assert r['bodyId']==binding['outputId']and r['featureId']==binding['featureId']and r['engine']=='occ'and r['engineRevision']==engine and r['materialId']==material and r['appearanceId']==appearance;pair=pairs[material];assert pair['appearanceId']==appearance and pair['resourceId']==r['materialResourceId']==int(materials[0].attrib['id'])and pair['index']==r['materialIndex'];assert materials[0][pair['index']].attrib=={'name':{'pla':'PLA','petg':'PETG'}[material],'displaycolor':color}
   assert int(refs[i].attrib['objectid'])==r['componentResourceId'];common.identity(refs[i]);component=objects[r['componentResourceId']];assert component.attrib['name']==name and component.find('m:mesh',NS)is None;c=component.find('m:components',NS);assert len(c)==1 and int(c[0].attrib['objectid'])==r['meshResourceId'];common.identity(c[0]);obj=objects[r['meshResourceId']];assert obj.attrib['name']==name and int(obj.attrib['pid'])==r['materialResourceId']and int(obj.attrib['pindex'])==pair['index']and obj.find('m:components',NS)is None;assert not used.intersection({r['componentResourceId'],r['meshResourceId']});used.update({r['componentResourceId'],r['meshResourceId']})
   mesh=obj.find('m:mesh',NS);vr=mesh.find('m:vertices',NS);tr=mesh.find('m:triangles',NS);assert all(set(x.attrib)=={'x','y','z'}for x in vr)and all(set(x.attrib)=={'v1','v2','v3'}for x in tr);vertices=[tuple(float(x.attrib[k])for k in['x','y','z'])for x in vr];triangles=[tuple(int(x.attrib[k])for k in['v1','v2','v3'])for x in tr]
   geometry=pocket_mesh(vertices,triangles,truth)if name=='lid'else common.inspect_mesh(vertices,triangles,[truth['fillMin'],truth['fillMax']]);points=[]
   for p in[[40,25,3],[40,25,1],[10,25,3],[40,25,4.5],[58,25,3],[81,25,2]]:
    inFill=all(truth['fillMin'][j]<p[j]<truth['fillMax'][j]for j in range(3));inBase=all([0,0,0][j]<p[j]<[80,50,4][j]for j in range(3));expected=inBase and not inFill if name=='lid'else inFill;observed=common.winding(vertices,triangles,p);assert abs(observed-int(expected))<=1e-7;points.append({'point':p,'material':expected,'winding':observed})
   geometry['insetMaterialPoints']=points;results.append({'regionId':name,'materialId':material,'geometry':geometry})
  assert used==set(objects)
 A=results[0]['geometry']['surfaceAreas'];B=results[1]['geometry']['surfaceAreas'];interfaces=[]
 for a,b in [('pocket00','(0, 0)'),('pocket01','(0, 1)'),('pocket10','(1, 0)'),('pocket11','(1, 1)'),('pocket20','(2, 0)')]:
  assert A[a]==B[b]>0;interfaces.append({'pocketPatch':a,'labelPatch':b,'area':A[a]})
 totalArea=sum(x['area']for x in interfaces);assert totalArea==sum(truth['interfaceAreas'].values());totalVolume=sum(x['geometry']['meshVolume']for x in results);assert abs(totalVolume-16000)<=1e-6
 return {'file':file.name,'bytes':len(raw),'sha256':sha(raw),'oneBuildItem':True,'regions':results,'interfaces':interfaces,'interfaceArea':totalArea,'totalVolume':totalVolume,'provenance':provenance}
def main(folder,repo):
 raw=(folder/'receipt.json').read_bytes();r=json.loads(raw);assert r['status']=='PASS'and r['ownedContextClosed']and r['sharedBrowserDisconnectedOnly']and r['syntheticGeometry']is False and r['syntheticStorage']is False and r['sourcePins']==r['sourcePinsAfter'];commit=r['driverSourceCommit'];assert len(commit)==40 and all(c in'0123456789abcdef'for c in commit)
 for name,digest in r['sourcePins'].items():
  target=posixpath.normpath('test/agent-cad-corpus/inset-label-interface/'+name);assert not target.startswith('../');assert sha(subprocess.check_output(['git','-C',str(repo),'show',commit+':'+target]))==digest
 pins=[x for x in r['rows']if x['label']=='Exact composed runtime byte pins'];assert len(pins)==3
 for x in pins:assert x['outer']['sha256']==r['pins']['outer']['sha256']and {p['name']:p['sha256']for p in x['files']}==r['pins']['files']
 sources={};saved={}
 for e in r['saved']:
  b=(folder/e['file']).read_bytes();assert len(b)==e['bytes']and sha(b)==e['sha256'];sources[e['label']]=derive(json.loads(b),r['binding'],r['engineRevision']);saved[e['label']]={'bytes':len(b),'sha256':sha(b)}
 assert set(sources)=={'initial-source','initial-reopened-source','edited-source','post-refusals-source','reopened-source'}and saved['initial-source']==saved['initial-reopened-source']and saved['edited-source']==saved['post-refusals-source']==saved['reopened-source'];assert sources['initial-source']['width']==30 and sources['edited-source']['width']==36
 changed=json.loads(json.dumps(sources['initial-source']['history']));changed[1]['params']['width']=36;changed[3]['params']['width']=36;assert changed==sources['edited-source']['history']
 failures=[x for x in r['rows']if x['label'].startswith('Rejected ')and x['label'].endswith(' raw outcome')];assert len(failures)==6
 for x in failures:assert x['failure']['code']=='UNQUALIFIED_REGION_INTERFACE'and not x['failure']['committed']and not x['failure']['possiblyCommitted']and not x['fileExists']and x['before']==x['after']
 outputs=[]
 for name,s in [('initial',sources['initial-source']),('edited',sources['edited-source']),('reopened',sources['reopened-source'])]:
  x=next(x for x in r['rows']if x['label']==name+' actual inset-lid3MF');value=artifact(folder/(name+'.3mf'),s,r['engineRevision']);assert value['sha256']==x['sha256']and value['bytes']==x['bytes']and x['acceptedStatePreserved'];c=x['result'];assert c['path']==x['file']and c['persistence']=='browser'and c['committed']is True and c['dirty']is False and c['serverStatus']=='not-verified';outputs.append(value)
 assert outputs[1]['provenance']==outputs[2]['provenance']and [x['geometry']['canonicalTrianglesSha256']for x in outputs[1]['regions']]==[x['geometry']['canonicalTrianglesSha256']for x in outputs[2]['regions']]
 print(json.dumps({'status':'PASS','scope':'Independent complete saved Native source/3MF inset-lid fixture oracle, exact planar patch coverage and five material interfaces; no new Native execution, general interface, slicer or print claim','receiptSha256':sha(raw),'driverSourceCommit':commit,'runtimePins':r['pins'],'savedSources':saved,'exports':outputs,'refusedInterfaces':len(failures),'editedReopenedCanonicalRegionMeshesEqual':True,'tolerances':{'coordinateAndPatchArea':'exact integer/rational fixture','volumeMm3':1e-6,'winding':1e-7}},indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
