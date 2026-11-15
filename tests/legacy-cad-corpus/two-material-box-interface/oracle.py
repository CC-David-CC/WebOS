#!/usr/bin/env python3
"""Independent whole-file/source oracle for the complete two-material box flow."""
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET
import math,json,hashlib,zipfile,io,sys,subprocess,posixpath
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
IDENTITY=[1,0,0,0,1,0,0,0,1,0,0,0]
sha=lambda b:hashlib.sha256(b).hexdigest()
sub=lambda a,b:tuple(x-y for x,y in zip(a,b))
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def winding(vertices,triangles,p):
 terms=[]
 for t in triangles:
  a,b,c=[sub(vertices[i],p)for i in t];la,lb,lc=[math.sqrt(dot(q,q))for q in[a,b,c]];terms.append(2*math.atan2(dot(a,cross(b,c)),la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb))
 return math.fsum(terms)/(4*math.pi)
def inspect_mesh(v,t,bounds):
 assert 4<=len(v)<=150000 and 4<=len(t)<=100000 and all(len(p)==3 and all(math.isfinite(x)and abs(x)<=1e9 for x in p)for p in v)
 low,high=bounds;edges=defaultdict(list);links=defaultdict(list);seen=set();adj=[set()for _ in t];areas=defaultdict(list)
 for i,tri in enumerate(t):
  assert len(tri)==len(set(tri))==3 and all(isinstance(x,int)and 0<=x<len(v)for x in tri);key=tuple(sorted(tri));assert key not in seen;seen.add(key)
  q=[v[x]for x in tri];n=cross(sub(q[1],q[0]),sub(q[2],q[0]));assert any(n)and all(low[j]<=p[j]<=high[j]for p in q for j in range(3))
  matches=[(axis,side)for axis in range(3)for side in range(2)if all(p[axis]==[low,high][side][axis]for p in q)];assert len(matches)==1;axis,side=matches[0];assert n[axis]*(1 if side else -1)>0 and all(n[j]==0 for j in range(3)if j!=axis);areas[(axis,side)].append(abs(n[axis])/2)
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
   x=todo.pop()
   if x not in visited:visited.add(x);todo.extend(graph[x])
  assert len(visited)==len(graph)
 todo=[0];visited=set()
 while todo:
  x=todo.pop()
  if x not in visited:visited.add(x);todo.extend(adj[x])
 assert len(visited)==len(t)and len(v)-len(edges)+len(t)==2
 dimensions=[high[i]-low[i]for i in range(3)];surfaceAreas={}
 for axis in range(3):
  expected=math.prod(dimensions[j]for j in range(3)if j!=axis)
  for side in range(2):assert abs(math.fsum(areas[(axis,side)])-expected)<=1e-6;surfaceAreas[str((axis,side))]=math.fsum(areas[(axis,side)])
 volume=math.fsum(dot(sub(v[a],v[0]),cross(sub(v[b],v[0]),sub(v[c],v[0])))/6 for a,b,c in t);expectedVolume=math.prod(dimensions);assert abs(volume-expectedVolume)<=1e-6
 canonical=[]
 for tri in t:
  q=tuple(tuple(0. if x==0 else x for x in v[i])for i in tri);canonical.append(min(q,q[1:]+q[:1],q[2:]+q[:2]))
 points=[]
 for p in [[20,15,5],[20,15,12],[20,15,16],[-1,15,5],[41,15,12]]:
  material=all(low[j]<p[j]<high[j]for j in range(3));observed=winding(v,t,p);assert abs(observed-int(material))<=1e-7;points.append({'point':p,'material':material,'winding':observed})
 return {'vertices':len(v),'triangles':len(t),'euler':2,'bounds':bounds,'nativeSourceBoxVolume':expectedVolume,'meshVolume':volume,'surfaceAreas':surfaceAreas,'points':points,'canonicalTrianglesSha256':sha(json.dumps(sorted(canonical),separators=(',',':')).encode())}

def derive(native,binding,engine):
 assert native['format']=='codi-jsketcher-project'and native['version']==2 and native['unit']=='millimeter'and native['project']['sketches']==[]
 history=native['project']['model']['history'];assert len(history)==2 and all(x['type']=='WORKER_SOLID_BOX_V1'for x in history)
 rows={x['params']['featureId']:x['params']for x in history};assert len(rows)==2;regions={}
 for name in ['base','cap']:
  b=binding[name];p=rows[b['featureId']];assert set(p)=={'version','unit','engine','engineRevision','featureId','x','y','z','width','depth','height'}and p['version']==1 and p['unit']=='millimeter'and p['engine']=='occ'and p['engineRevision']==engine==b['engineRevision']
  low=[p[k]for k in ['x','y','z']];dimensions=[p[k]for k in ['width','depth','height']];assert all(type(x)in[int,float]and math.isfinite(x)for x in low+dimensions)and min(dimensions)>0
  regions[name]={'producer':p,'bodyId':b['outputId'],'bounds':[low,[low[i]+dimensions[i]for i in range(3)]]}
 a,b=regions['base']['bounds'],regions['cap']['bounds'];assert a==[[0,0,0],[40,30,10]]and b[0]==[0,0,10]and b[1][:2]==[40,30]and b[1][2]in [15,18]
 assert a[1][2]==b[0][2]and all(a[0][i]==b[0][i]and a[1][i]==b[1][i]for i in[0,1]);interfaceArea=(a[1][0]-a[0][0])*(a[1][1]-a[0][1]);assert interfaceArea==1200
 m=native['manufacturing'];assert m['version']==1 and m['unit']=='millimeter'and m['revision'].startswith('sha256-')and len(m['revision'])==71
 assert m['materials']==[{'id':'pla','name':'PLA'},{'id':'petg','name':'PETG'}]and m['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'},{'id':'yellow','name':'Yellow','color':'#ffcc00'}]
 assert len(m['objects'])==1 and len(m['bindings'])==2;part=m['objects'][0];assert part['id']=='two-material'and part['name']=='Two-material block'and [x['id']for x in part['regions']]==['base','cap']
 aliases={x['id']:x for x in m['bindings']};assert len(aliases)==2
 for r in part['regions']:
  key=r['id'];actual=regions[key];alias=aliases[r['bodyId']];assert alias['featureId']==actual['producer']['featureId']and alias['operationType']=='WORKER_SOLID_BOX_V1'and r['transform']==IDENTITY and (r['materialId'],r['appearanceId'])==({'base':('pla','blue'),'cap':('petg','yellow')}[key])
 return {'history':history,'metadata':m,'part':part,'regions':regions,'interface':{'axis':2,'coordinate':10,'rectangle':[[0,0],[40,30]],'area':interfaceArea},'height':b[1][2]-10}
def identity(e):
 if'transform'in e.attrib:assert [float(x)for x in e.attrib['transform'].split()]==IDENTITY
def artifact(file,truth,engine):
 raw=file.read_bytes();assert 0<len(raw)<=67108864
 with zipfile.ZipFile(io.BytesIO(raw))as z:
  assert len(z.namelist())==5 and set(z.namelist())=={'[Content_Types].xml','_rels/','_rels/.rels','3D/','3D/3dmodel.model'}and sum(x.file_size for x in z.infolist())<=64*1024*1024 and z.testzip()is None
  rel=ET.fromstring(z.read('_rels/.rels'));assert len(rel)==1 and rel[0].attrib['Target']=='/3D/3dmodel.model'and rel[0].attrib['Type']=='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
  ct=ET.fromstring(z.read('[Content_Types].xml'));assert any(x.attrib.get('Extension')=='model'and x.attrib.get('ContentType')=='application/vnd.ms-package.3dmanufacturing-3dmodel+xml'for x in ct)
  xml=z.read('3D/3dmodel.model');assert len(xml)<=48*1024*1024;namespaces=dict(x for _,x in ET.iterparse(io.BytesIO(xml),events=['start-ns']));assert namespaces['codi']=='https://ksu.codes/3mf/metadata/2026';model=ET.fromstring(xml);assert model.attrib['unit']=='millimeter'
  md=model.findall('m:metadata',NS);assert len(md)==2;md={x.attrib['name']:x.text for x in md};assert set(md)=={'codi:SourceRevision','codi:ManufacturingBindings'}and md['codi:SourceRevision']==truth['metadata']['revision'][7:];p=json.loads(md['codi:ManufacturingBindings']);assert p['version']==1 and p['revision']==md['codi:SourceRevision']and len(p['parts'])==1 and len(p['materialPairs'])==2
  part=p['parts'][0];assert part['id']=='two-material'and part['name']=='Two-material block'and [x['id']for x in part['regions']]==['base','cap']
  resources=model.find('m:resources',NS);assert len(resources)==6;ids=[int(x.attrib['id'])for x in resources];assert len(set(ids))==6 and min(ids)>0;objects={int(x.attrib['id']):x for x in resources.findall('m:object',NS)};assert len(objects)==5 and all(x.attrib['type']=='model'for x in objects.values());materials=resources.findall('m:basematerials',NS);assert len(materials)==1 and len(materials[0])==2
  builds=model.find('m:build',NS);assert len(builds)==1 and int(builds[0].attrib['objectid'])==part['buildResourceId'];identity(builds[0]);group=objects[part['buildResourceId']];assert group.attrib['name']=='Two-material block'and group.find('m:mesh',NS)is None;references=group.find('m:components',NS);assert len(references)==2
  results=[];used={part['buildResourceId']};pairs={x['materialId']:x for x in p['materialPairs']};assert set(pairs)=={'pla','petg'}
  for i,region in enumerate(part['regions']):
   name=region['id'];source=truth['regions'][name];material,appearance,color={'base':('pla','blue','#3366FF'),'cap':('petg','yellow','#FFCC00')}[name];assert region['bodyId']==source['bodyId']and region['featureId']==source['producer']['featureId']and region['engine']=='occ'and region['engineRevision']==engine and region['materialId']==material and region['appearanceId']==appearance
   pair=pairs[material];assert pair['appearanceId']==appearance and pair['resourceId']==region['materialResourceId']==int(materials[0].attrib['id'])and pair['index']==region['materialIndex'];assert materials[0][pair['index']].attrib=={'name':{'pla':'PLA','petg':'PETG'}[material],'displaycolor':color}
   ref=references[i];assert int(ref.attrib['objectid'])==region['componentResourceId'];identity(ref);component=objects[region['componentResourceId']];assert component.attrib['name']==name and component.find('m:mesh',NS)is None;refs=component.find('m:components',NS);assert len(refs)==1 and int(refs[0].attrib['objectid'])==region['meshResourceId'];identity(refs[0]);obj=objects[region['meshResourceId']];assert obj.attrib['name']==name and int(obj.attrib['pid'])==region['materialResourceId']and int(obj.attrib['pindex'])==pair['index']and obj.find('m:components',NS)is None
   assert not used.intersection({region['componentResourceId'],region['meshResourceId']});used.update({region['componentResourceId'],region['meshResourceId']});mesh=obj.find('m:mesh',NS);vr=mesh.find('m:vertices',NS);tr=mesh.find('m:triangles',NS);assert all(set(x.attrib)=={'x','y','z'}for x in vr)and all(set(x.attrib)=={'v1','v2','v3'}for x in tr);vertices=[tuple(float(x.attrib[k])for k in['x','y','z'])for x in vr];triangles=[tuple(int(x.attrib[k])for k in['v1','v2','v3'])for x in tr]
   results.append({'regionId':name,'materialId':material,'appearanceId':appearance,'geometry':inspect_mesh(vertices,triangles,source['bounds'])})
  assert used==set(objects)
 assert results[0]['geometry']['surfaceAreas']['(2, 1)']==results[1]['geometry']['surfaceAreas']['(2, 0)']==truth['interface']['area'];total=sum(x['geometry']['meshVolume']for x in results);assert abs(total-(12000+1200*truth['height']))<=1e-6
 return {'file':file.name,'bytes':len(raw),'sha256':sha(raw),'oneBuildItem':True,'regions':results,'interface':truth['interface'],'totalVolume':total,'provenance':p}
def main(folder,repo):
 raw=(folder/'receipt.json').read_bytes();r=json.loads(raw);assert r['status']=='PASS'and r['ownedContextClosed']and r['sharedBrowserDisconnectedOnly']and r['syntheticGeometry']is False and r['syntheticStorage']is False and r['sourcePins']==r['sourcePinsAfter'];commit=r['driverSourceCommit'];assert len(commit)==40 and all(c in'0123456789abcdef'for c in commit)
 for name,digest in r['sourcePins'].items():
  target=posixpath.normpath('test/agent-cad-corpus/two-material-box-interface/'+name);assert not target.startswith('../');assert sha(subprocess.check_output(['git','-C',str(repo),'show',commit+':'+target]))==digest
 pins=[x for x in r['rows']if x['label']=='Exact composed runtime byte pins'];assert len(pins)==3
 for row in pins:assert row['outer']['sha256']==r['pins']['outer']['sha256']and {x['name']:x['sha256']for x in row['files']}==r['pins']['files']
 sources={};saved={}
 for entry in r['saved']:
  body=(folder/entry['file']).read_bytes();assert len(body)==entry['bytes']and sha(body)==entry['sha256'];saved[entry['label']]={'sha256':sha(body),'bytes':len(body)};sources[entry['label']]=derive(json.loads(body),r['binding'],r['engineRevision'])
 assert set(sources)=={'initial-source','initial-reopened-source','edited-source','post-refusals-source','reopened-source'}and saved['initial-source']==saved['initial-reopened-source']and saved['edited-source']==saved['post-refusals-source']==saved['reopened-source']
 assert sources['initial-source']['height']==5 and sources['edited-source']['height']==8;changed=json.loads(json.dumps(sources['initial-source']['history']));changed[1]['params']['height']=8;assert changed==sources['edited-source']['history']
 failures=[x for x in r['rows']if x['label'].startswith('Rejected ')and x['label'].endswith(' raw outcome')];assert len(failures)==5
 for x in failures:assert x['failure']['code']=='UNQUALIFIED_REGION_INTERFACE'and not x['failure']['committed']and not x['failure']['possiblyCommitted']and x['fileExists']is False and x['before']==x['after']
 exports=[]
 for label,source in [('initial',sources['initial-source']),('edited',sources['edited-source']),('reopened',sources['reopened-source'])]:
  row=next(x for x in r['rows']if x['label']==label+' same-part two-region 3MF');value=artifact(folder/(label+'.3mf'),source,r['engineRevision']);assert value['sha256']==row['sha256']and value['bytes']==row['bytes']and row['acceptedStatePreserved'];c=row['result'];assert c['path']==row['file']and c['persistence']=='browser'and c['committed']is True and c['dirty']is False and c['serverStatus']=='not-verified';exports.append(value)
 assert exports[1]['provenance']==exports[2]['provenance']and [x['geometry']['canonicalTrianglesSha256']for x in exports[1]['regions']]==[x['geometry']['canonicalTrianglesSha256']for x in exports[2]['regions']]
 print(json.dumps({'status':'PASS','scope':'Independent complete two-box same-object/two-material exported-artifact and saved-source oracle; no new Native execution, arbitrary interface, slicer or physical print claim','receiptSha256':sha(raw),'driverSourceCommit':commit,'runtimePins':r['pins'],'savedSources':saved,'exports':exports,'refusedInterfaces':len(failures),'editedReopenedCanonicalRegionMeshesEqual':True,'tolerances':{'coordinates':'exact integer box fixture','volumeMm3':1e-6,'faceAreaMm2':1e-6,'winding':1e-7}},indent=2))
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
