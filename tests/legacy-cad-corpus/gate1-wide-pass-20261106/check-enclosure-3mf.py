#!/usr/bin/env python3
"""Independent ZIP/XML mesh oracle; specific public V1 recipe, not STEP."""
import sys,json,math
from collections import Counter
from xml.etree import ElementTree as E
from zipfile import ZipFile
N={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
near=lambda a,b:math.isclose(a,b,abs_tol=1e-6,rel_tol=1e-9)
with ZipFile(sys.argv[1]) as z:
 assert z.testzip() is None
 assert {'[Content_Types].xml','_rels/.rels','3D/3dmodel.model'}<=set(z.namelist())
 root=E.fromstring(z.read('3D/3dmodel.model'))
assert root.get('unit')=='millimeter'
objs={o.get('id'):o for o in root.findall('./c:resources/c:object',N)}
expected={'region-BODY':([0,0,0],[60,40,30],60*40*30-56*36*28),'region-LID':([0,0,27],[60,40,32],60*40*2+55.4*35.4*3)}
rows=[]
for o in objs.values():
 mesh=o.find('c:mesh',N)
 if mesh is None:continue
 name=o.get('name');assert name in expected,name
 vs=[tuple(float(v.get(k)) for k in ('x','y','z')) for v in mesh.findall('./c:vertices/c:vertex',N)]
 ts=[tuple(int(t.get(k)) for k in ('v1','v2','v3')) for t in mesh.findall('./c:triangles/c:triangle',N)]
 edges=Counter();orientation=Counter();vol=0
 for a,b,c in ts:
  assert len({a,b,c})==3 and all(0<=i<len(vs) for i in (a,b,c))
  for x,y in ((a,b),(b,c),(c,a)):edges[tuple(sorted((x,y)))]+=1;orientation[(x,y)]+=1
  x,y,z=vs[a],vs[b],vs[c];vol+=(x[0]*(y[1]*z[2]-y[2]*z[1])+x[1]*(y[2]*z[0]-y[0]*z[2])+x[2]*(y[0]*z[1]-y[1]*z[0]))/6
 assert all(n==2 for n in edges.values())
 assert all(orientation[(a,b)]==orientation[(b,a)] for a,b in edges)
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];elo,ehi,ev=expected[name]
 assert all(near(a,b) for a,b in zip(lo+hi,elo+ehi)),(name,lo,hi)
 assert near(vol,ev),(name,vol,ev)
 rows.append({'name':name,'triangles':len(ts),'volume':vol,'bounds':{'min':lo,'max':hi},'closedOrientedMesh':True})
assert {r['name'] for r in rows}==set(expected)
items=root.findall('./c:build/c:item',N);assert len(items)==2
for node in root.findall('.//c:component',N)+items:assert node.get('transform') in (None,'1 0 0 0 1 0 0 0 1 0 0 0')
print(json.dumps({'status':'PASS','unit':root.get('unit'),'buildItems':len(items),'meshes':rows,'scope':'Specific enclosure handoff, not STEP or generic plate3MF'},indent=2))
