#!/usr/bin/env python3
"""Independent whole-output oracle for the bounded public box-shell workflow."""
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET
import math,hashlib,json,zipfile,io,sys,subprocess,posixpath

ENGINE='sha256:57b74074e0a249b917ac68357fbd003c37d1ab61897206886b575088e6995858:60dc956b08e01f43d08a48035a384e478e63bb34fb55f21a152c8cd12e8b8947'
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
IDENTITY=[1,0,0,0,1,0,0,0,1,0,0,0]
COORD=1e-7;BOUNDS=1e-6;VOLUME=1e-6;AREA=1e-6;WINDING=1e-7
sha=lambda b:hashlib.sha256(b).hexdigest()
sub=lambda a,b:tuple(x-y for x,y in zip(a,b))
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def winding(vertices,triangles,p):
 terms=[]
 for tri in triangles:
  a,b,c=[sub(vertices[i],p)for i in tri];la,lb,lc=[math.sqrt(dot(q,q))for q in [a,b,c]]
  terms.append(2*math.atan2(dot(a,cross(b,c)),la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb))
 return math.fsum(terms)/(4*math.pi)

def rectangle_overlap_area(triangle,x0,y0,x1,y1):
 # Bounded independent planar clipping: exclude every open top-cavity patch.
 p=[q[:2]for q in triangle]
 for axis,value,sign in [(0,x0,1),(0,x1,-1),(1,y0,1),(1,y1,-1)]:
  out=[]
  for i,a in enumerate(p):
   b=p[(i+1)%len(p)];ina=(a[axis]-value)*sign>=0;inb=(b[axis]-value)*sign>=0
   if ina:out.append(a)
   if ina!=inb:
    ratio=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+ratio*(b[j]-a[j])for j in range(2)))
  p=out
  if not p:return 0.
 return abs(math.fsum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1]for i in range(len(p))))/2

def mesh(vertices,triangles,truth):
 v,t=vertices,triangles;assert 4<=len(v)<=150000 and 4<=len(t)<=100000
 assert all(len(q)==3 and all(math.isfinite(x)and abs(x)<=1e9 for x in q)for q in v)
 edges=defaultdict(list);links=defaultdict(list);seen=set();adj=[set()for _ in t]
 for i,tri in enumerate(t):
  assert len(tri)==3 and len(set(tri))==3 and all(isinstance(n,int)and 0<=n<len(v)for n in tri)
  key=tuple(sorted(tri));assert key not in seen;seen.add(key)
  normal=cross(sub(v[tri[1]],v[tri[0]]),sub(v[tri[2]],v[tri[0]]));assert any(normal)and all(math.isfinite(x)for x in normal)
  for j in range(3):
   a,b=tri[j],tri[(j+1)%3];edges[tuple(sorted((a,b)))].append((a,b,i));links[a].append((b,tri[(j+2)%3]))
 assert len(links)==len(v)
 for uses in edges.values():
  assert len(uses)==2 and uses[0][:2]==uses[1][:2][::-1];a,b=uses[0][2],uses[1][2];adj[a].add(b);adj[b].add(a)
 for rows in links.values():
  graph=defaultdict(list)
  for a,b in rows:graph[a].append(b);graph[b].append(a)
  assert all(len(x)==2 for x in graph.values());todo=[next(iter(graph))];visited=set()
  while todo:
   a=todo.pop()
   if a not in visited:visited.add(a);todo.extend(graph[a])
  assert len(visited)==len(graph)
 todo=[0];visited=set()
 while todo:
  a=todo.pop()
  if a not in visited:visited.add(a);todo.extend(adj[a])
 assert len(visited)==len(t)and len(v)-len(edges)+len(t)==2
 w,d,h,k=[truth[x]for x in ['width','depth','height','thickness']]
 lo=[min(p[i]for p in v)for i in range(3)];hi=[max(p[i]for p in v)for i in range(3)]
 assert all(abs(lo[i])<=BOUNDS and abs(hi[i]-[w,d,h][i])<=BOUNDS for i in range(3))
 # Actual boundary planes and their outward orientation. Top rim is one
 # multiply connected planar patch, not a lid closing the opening.
 faces=[('outer-x0',0,0,-1,[0,0,0],[0,d,h],d*h),('outer-x1',0,w,1,[w,0,0],[w,d,h],d*h),
  ('outer-y0',1,0,-1,[0,0,0],[w,0,h],w*h),('outer-y1',1,d,1,[0,d,0],[w,d,h],w*h),
  ('outer-bottom',2,0,-1,[0,0,0],[w,d,0],w*d),
  ('inner-x0',0,k,1,[k,k,k],[k,d-k,h],(d-2*k)*(h-k)),('inner-x1',0,w-k,-1,[w-k,k,k],[w-k,d-k,h],(d-2*k)*(h-k)),
  ('inner-y0',1,k,1,[k,k,k],[w-k,k,h],(w-2*k)*(h-k)),('inner-y1',1,d-k,-1,[k,d-k,k],[w-k,d-k,h],(w-2*k)*(h-k)),
  ('inner-floor',2,k,1,[k,k,k],[w-k,d-k,k],(w-2*k)*(d-2*k)),('top-rim',2,h,1,[0,0,h],[w,d,h],w*d-(w-2*k)*(d-2*k))]
 areas=defaultdict(list);counts=defaultdict(int)
 for tri in t:
  q=[v[i]for i in tri];normal=cross(sub(q[1],q[0]),sub(q[2],q[0]));matches=[]
  for name,axis,value,sign,minimum,maximum,expectedArea in faces:
   if all(abs(p[axis]-value)<=COORD and all(minimum[i]-COORD<=p[i]<=maximum[i]+COORD for i in range(3))for p in q):matches.append((name,axis,sign))
  assert len(matches)==1,('Unexpected shell boundary triangle',q,matches)
  name,axis,sign=matches[0];assert normal[axis]*sign>0 and all(abs(normal[j])<=AREA for j in range(3)if j!=axis)
  if name=='top-rim':assert rectangle_overlap_area(q,k,k,w-k,d-k)<=1e-10,('Mesh silently caps open top',q)
  areas[name].append(abs(normal[axis])/2);counts[name]+=1
 faceAreas={}
 for name,axis,value,sign,minimum,maximum,expectedArea in faces:
  area=math.fsum(areas[name]);assert counts[name]>0 and abs(area-expectedArea)<=AREA,(name,area,expectedArea);faceAreas[name]={'area':area,'expectedArea':expectedArea,'triangles':counts[name]}
 origin=v[0];volume=math.fsum(dot(sub(v[a],origin),cross(sub(v[b],origin),sub(v[c],origin)))/6 for a,b,c in t);expectedVolume=w*d*h-(w-2*k)*(d-2*k)*(h-k)
 assert abs(volume-expectedVolume)<=VOLUME,(volume,expectedVolume)
 checks=[([w/2,d/2,(k+h)/2],False,'open-cavity'),([w/2,d/2,h+.25],False,'above-open-top'),([w/2,d/2,k/2],True,'floor-material'),([w/2,d/2,k+.25],False,'above-inner-floor'),([k/2,d/2,h/2],True,'wall-material'),([k+.25,d/2,h/2],False,'beyond-inner-wall'),([w-k/2,d/2,h/2],True,'opposite-wall'),([w/2,k/2,h-.25],True,'top-wall'),([-1,d/2,h/2],False,'outside')]
 points=[]
 for p,material,label in checks:
  observed=winding(v,t,p);assert abs(observed-int(material))<=WINDING,(p,material,observed);points.append({'point':p,'material':material,'winding':observed,'label':label})
 canonical=[]
 for tri in t:
  q=tuple(tuple(0. if x==0 else x for x in v[i])for i in tri);canonical.append(min(q,q[1:]+q[:1],q[2:]+q[:2]))
 return {'vertices':len(v),'triangles':len(t),'euler':2,'bounds':{'min':lo,'max':hi},'analyticVolume':expectedVolume,'meshVolume':volume,'volumeDifference':volume-expectedVolume,'faceAreas':faceAreas,'points':points,'canonicalTrianglesSha256':sha(json.dumps(sorted(canonical),separators=(',',':')).encode())}

def source(native,binding):
 assert native['format']=='codi-jsketcher-project'and native['version']==2 and native['unit']=='millimeter'
 project=native['project'];assert project['sketches']==[];history=project['model']['history'];assert [x['type']for x in history]==['WORKER_SOLID_BOX_V1','WORKER_SOLID_SHELL_V1']
 box,shell=[x['params']for x in history]
 assert set(box)=={'version','unit','engine','engineRevision','featureId','x','y','z','width','depth','height'}
 assert set(shell)=={'version','unit','engine','engineRevision','featureId','target','producerFeatureId','removedFaceIds','thickness','direction'}
 for p in [box,shell]:assert p['version']==1 and p['unit']=='millimeter'and p['engine']=='occ'and p['engineRevision']==ENGINE
 assert all(box[x]==0 for x in ['x','y','z'])and box['featureId']==binding['box']['featureId']and shell['featureId']==binding['shell']['featureId']and shell['producerFeatureId']==box['featureId']and shell['target']==binding['box']['outputId']and shell['direction']=='inward'
 # Equality to corroborated public builder descriptor; never parse opaque ID.
 assert binding['removedFace']['role']=='Z_MAX'and binding['removedFace']['geometry']=='plane'and binding['removedFace']['originFeatureId']==box['featureId']and shell['removedFaceIds']==[binding['removedFace']['id']]
 dimensions={k:box[k]for k in ['width','depth','height']};dimensions['thickness']=shell['thickness'];assert all(type(x)in [int,float]and math.isfinite(x)and x>0 for x in dimensions.values());assert 2*shell['thickness']<min(box['width'],box['depth'])and shell['thickness']<box['height']
 m=native['manufacturing'];assert m['version']==1 and m['unit']=='millimeter'and m['revision'].startswith('sha256-')and len(m['revision'])==71
 assert m['materials']==[{'id':'pla','name':'PLA'}]and m['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'}]and len(m['objects'])==len(m['bindings'])==1
 part=m['objects'][0];alias=m['bindings'][0];assert part['id']=='shell'and part['name']=='Open-top enclosure'and len(part['regions'])==1
 region=part['regions'][0];assert region['id']=='main'and region['bodyId']==alias['id']and alias['featureId']==shell['featureId']and alias['operationType']=='WORKER_SOLID_SHELL_V1'and region['materialId']=='pla'and region['appearanceId']=='blue'and region['transform']==IDENTITY
 return {'dimensions':dimensions,'metadata':m,'part':part,'history':history,'producer':shell,'bodyId':binding['shell']['outputId']}

def identity(e):
 if 'transform'in e.attrib:assert [float(x)for x in e.attrib['transform'].split()]==IDENTITY

def artifact(file,truth):
 raw=file.read_bytes();assert 0<len(raw)<=67108864
 with zipfile.ZipFile(io.BytesIO(raw))as z:
  assert len(z.namelist())==5 and set(z.namelist())=={'[Content_Types].xml','_rels/','_rels/.rels','3D/','3D/3dmodel.model'}and sum(x.file_size for x in z.infolist())<=64*1024*1024 and z.testzip()is None
  rel=ET.fromstring(z.read('_rels/.rels'));assert len(rel)==1 and rel[0].attrib['Target']=='/3D/3dmodel.model'and rel[0].attrib['Type']=='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
  ct=ET.fromstring(z.read('[Content_Types].xml'));assert any(x.attrib.get('Extension')=='model'and x.attrib.get('ContentType')=='application/vnd.ms-package.3dmanufacturing-3dmodel+xml'for x in ct)
  xml=z.read('3D/3dmodel.model');assert len(xml)<=48*1024*1024;namespaces=dict(x for _,x in ET.iterparse(io.BytesIO(xml),events=['start-ns']));assert namespaces['codi']=='https://ksu.codes/3mf/metadata/2026'
  model=ET.fromstring(xml);assert model.attrib['unit']=='millimeter';rows=model.findall('m:metadata',NS);assert len(rows)==2;md={x.attrib['name']:x.text for x in rows};assert set(md)=={'codi:SourceRevision','codi:ManufacturingBindings'}and md['codi:SourceRevision']==truth['metadata']['revision'][7:]
  provenance=json.loads(md['codi:ManufacturingBindings']);assert provenance['version']==1 and provenance['revision']==md['codi:SourceRevision']and len(provenance['parts'])==len(provenance['materialPairs'])==1
  part=provenance['parts'][0];assert part['id']==truth['part']['id']and part['name']==truth['part']['name']and len(part['regions'])==1;region=part['regions'][0];assert region['id']=='main'and region['bodyId']==truth['bodyId']and region['featureId']==truth['producer']['featureId']and region['engine']=='occ'and region['engineRevision']==ENGINE and region['materialId']=='pla'and region['appearanceId']=='blue'
  pair=provenance['materialPairs'][0];assert pair['materialId']=='pla'and pair['appearanceId']=='blue'and pair['index']==region['materialIndex']==0
  resources=model.find('m:resources',NS);assert len(resources)==4;ids=[int(x.attrib['id'])for x in resources];assert len(set(ids))==4 and min(ids)>0
  objects={int(x.attrib['id']):x for x in resources.findall('m:object',NS)};assert len(objects)==3 and all(x.attrib['type']=='model'for x in objects.values());mats=resources.findall('m:basematerials',NS);assert len(mats)==1 and int(mats[0].attrib['id'])==pair['resourceId']==region['materialResourceId']and len(mats[0])==1 and mats[0][0].attrib=={'name':'PLA','displaycolor':'#3366FF'}
  build=model.find('m:build',NS);assert len(build)==1 and int(build[0].attrib['objectid'])==part['buildResourceId'];identity(build[0]);group=objects[part['buildResourceId']];assert group.attrib['name']==part['name']and group.find('m:mesh',NS)is None;refs=group.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['componentResourceId'];identity(refs[0])
  component=objects[region['componentResourceId']];assert component.attrib['name']=='main'and component.find('m:mesh',NS)is None;refs=component.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['meshResourceId'];identity(refs[0]);obj=objects[region['meshResourceId']];assert obj.attrib['name']=='main'and int(obj.attrib['pid'])==pair['resourceId']and int(obj.attrib['pindex'])==0 and obj.find('m:components',NS)is None
  item=obj.find('m:mesh',NS);vr=item.find('m:vertices',NS);tr=item.find('m:triangles',NS);assert all(set(x.attrib)=={'x','y','z'}for x in vr)and all(set(x.attrib)=={'v1','v2','v3'}for x in tr)
  vertices=[tuple(float(x.attrib[k])for k in ['x','y','z'])for x in vr];triangles=[tuple(int(x.attrib[k])for k in ['v1','v2','v3'])for x in tr]
 return {'file':file.name,'bytes':len(raw),'sha256':sha(raw),'provenance':provenance,'geometry':mesh(vertices,triangles,truth['dimensions'])}

def main(folder,repo):
 receiptRaw=(folder/'receipt.json').read_bytes();r=json.loads(receiptRaw);assert r['status']=='PASS'and r['ownedContextClosed']and r['sharedBrowserDisconnectedOnly']and r['syntheticGeometry']is False and r['syntheticStorage']is False and r['filesystemRace']is False and r['sourcePins']==r['sourcePinsAfter']and r['engineRevision']==ENGINE
 # Source custody uses the frozen producer commit, not today's working tree or
 # runtime Desktop revision (which may legitimately differ from the driver).
 commit=r['driverSourceCommit'];assert len(commit)==40 and all(c in '0123456789abcdef'for c in commit)
 for name,digest in r['sourcePins'].items():
  target=posixpath.normpath('test/agent-cad-corpus/shell-manufacturing/'+name);assert not target.startswith('../');body=subprocess.check_output(['git','-C',str(repo),'show',commit+':'+target]);assert sha(body)==digest,(name,commit)
 pinrows=[x for x in r['rows']if x['label']=='Exact composed outer and inner byte pins'];assert len(pinrows)==3
 for row in pinrows:assert row['outer']['sha256']==r['pins']['outer']['sha256']and {x['name']:x['sha256']for x in row['files']}==r['pins']['files']
 natives={};saved={};bindings=r['binding']
 for entry in r['saved']:
  raw=(folder/entry['savedFile']).read_bytes();assert len(raw)==entry['bytes']and sha(raw)==entry['sha256'];natives[entry['label']]=source(json.loads(raw),bindings);saved[entry['label']]={'sha256':sha(raw),'bytes':len(raw)};assert natives[entry['label']]['dimensions']==entry['dimensions']
 assert set(natives)=={'initial-source','initial-reopened-source','edited-source','reopened-source'}
 assert saved['initial-source']==saved['initial-reopened-source']and saved['edited-source']==saved['reopened-source']
 initial=natives['initial-source'];edited=natives['edited-source'];assert initial['dimensions']=={'width':100,'depth':50,'height':20,'thickness':2}and edited['dimensions']=={'width':120,'depth':60,'height':25,'thickness':3}
 changed=json.loads(json.dumps(initial['history']));changed[0]['params'].update(width=120,depth=60,height=25);changed[1]['params']['thickness']=3;assert changed==edited['history']
 results=[]
 for label,truth in [('initial',initial),('edited',edited),('reopened',natives['reopened-source'])]:
  row=next(x for x in r['rows']if x['label']==label+' public shell 3MF export');value=artifact(folder/(label+'.3mf'),truth);assert value['sha256']==row['sha256']and value['bytes']==row['bytes']and row['authoredStatePreserved']
  c=row['result'];assert c['path']==row['file']and c['persistence']=='browser'and c['committed']is True and c['dirty']is False and c['serverStatus']=='not-verified'and isinstance(c['version'],str)and c['version'];value['commit']=c;results.append(value)
 assert results[1]['provenance']==results[2]['provenance']and results[1]['geometry']['canonicalTrianglesSha256']==results[2]['geometry']['canonicalTrianglesSha256']
 print(json.dumps({'status':'PASS','scope':'Independent complete box-shell exported artifact, saved intent, ZIP/XML/material identity and measurable planar mesh oracle; no fresh Native execution, general-shell, slicer, physical-print or multi-region interface claim','receiptSha256':sha(receiptRaw),'driverSourceCommit':commit,'runtimePins':r['pins'],'nativeFiles':saved,'exports':results,'tolerances':{'coordinateMm':COORD,'boundsMm':BOUNDS,'volumeMm3':VOLUME,'faceAreaMm2':AREA,'winding':WINDING},'editedReopenedCanonicalMeshEqual':True},indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
