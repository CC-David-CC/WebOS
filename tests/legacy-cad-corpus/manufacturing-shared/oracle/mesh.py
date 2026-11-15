"""Independent measurable rectangular plate/circular-through-bores fixture math."""
import math,hashlib,json
from collections import defaultdict
COORD=1e-7;BOUNDS=1e-6;ARITHMETIC=1e-6;WINDING=1e-7
sub=lambda a,b:tuple(x-y for x,y in zip(a,b))
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
cross=lambda a,b:(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def winding(v,t,p):
 terms=[]
 for tri in t:
  a,b,c=[sub(v[i],p)for i in tri];la,lb,lc=[math.sqrt(dot(q,q))for q in[a,b,c]];terms.append(2*math.atan2(dot(a,cross(b,c)),la*lb*lc+dot(a,b)*lc+dot(b,c)*la+dot(c,a)*lb))
 return math.fsum(terms)/(4*math.pi)
def inspect(vertices,triangles,truth,witness_material):
 v,t=vertices,triangles;assert 4<=len(v)<=150000 and 4<=len(t)<=250000
 assert all(len(p)==3 and all(math.isfinite(x)and abs(x)<=1e9 for x in p)for p in v)
 edges=defaultdict(list);links=defaultdict(list);seen=set();adj=[set()for _ in t]
 for i,tri in enumerate(t):
  assert len(tri)==3 and len(set(tri))==3 and all(isinstance(x,int)and 0<=x<len(v)for x in tri);key=tuple(sorted(tri));assert key not in seen;seen.add(key)
  normal=cross(sub(v[tri[1]],v[tri[0]]),sub(v[tri[2]],v[tri[0]]));assert any(normal)and all(math.isfinite(x)for x in normal)
  for j in range(3):
   a,b=tri[j],tri[(j+1)%3];edges[tuple(sorted((a,b)))].append((a,b,i));links[a].append((b,tri[(j+2)%3]))
 assert len(links)==len(v)
 for uses in edges.values():
  assert len(uses)==2 and uses[0][:2]==uses[1][:2][::-1];a,b=uses[0][2],uses[1][2];adj[a].add(b);adj[b].add(a)
 for rows in links.values():
  g=defaultdict(list)
  for a,b in rows:g[a].append(b);g[b].append(a)
  assert all(len(x)==2 for x in g.values());todo=[next(iter(g))];visited=set()
  while todo:
   a=todo.pop()
   if a not in visited:visited.add(a);todo.extend(g[a])
  assert len(visited)==len(g)
 todo=[0];visited=set()
 while todo:
  a=todo.pop()
  if a not in visited:visited.add(a);todo.extend(adj[a])
 assert len(visited)==len(t);holes=truth['bores'];assert len(v)-len(edges)+len(t)==2-2*len(holes)
 xmin,ymin,zmin=truth['bounds']['min'];xmax,ymax,zmax=truth['bounds']['max'];depth=zmax-zmin
 lo=[min(p[i]for p in v)for i in range(3)];hi=[max(p[i]for p in v)for i in range(3)];assert all(abs(lo[i]-truth['bounds']['min'][i])<=BOUNDS and abs(hi[i]-truth['bounds']['max'][i])<=BOUNDS for i in range(3))
 rings=[{'bottom':set(),'top':set(),'maxSpan':0.,'triangles':0}for _ in holes];planes=[(0,xmin,-1),(0,xmax,1),(1,ymin,-1),(1,ymax,1)]
 for tri in t:
  q=[v[i]for i in tri];normal=cross(sub(q[1],q[0]),sub(q[2],q[0]));assert all(xmin-COORD<=p[0]<=xmax+COORD and ymin-COORD<=p[1]<=ymax+COORD and zmin-COORD<=p[2]<=zmax+COORD for p in q)
  if all(abs(p[2]-zmin)<=COORD for p in q):assert normal[2]<0;continue
  if all(abs(p[2]-zmax)<=COORD for p in q):assert normal[2]>0;continue
  outer=[(axis,s)for axis,value,s in planes if all(abs(p[axis]-value)<=COORD for p in q)]
  if outer:assert len(outer)==1 and normal[outer[0][0]]*outer[0][1]>0;continue
  matches=[i for i,(x,y,r)in enumerate(holes)if all(abs(math.hypot(p[0]-x,p[1]-y)-r)<=COORD for p in q)];assert len(matches)==1,('unexplained lateral surface',q);i=matches[0];x,y,r=holes[i];ring=rings[i];ring['triangles']+=1;assert normal[0]*sum(p[0]-x for p in q)+normal[1]*sum(p[1]-y for p in q)<0
  angles=[math.atan2(p[1]-y,p[0]-x)for p in q];span=max(min((a-b)%(2*math.pi),(b-a)%(2*math.pi))for a in angles for b in angles);assert span<=.1+1e-10;ring['maxSpan']=max(ring['maxSpan'],span)
  for index,p in zip(tri,q):
   if abs(p[2]-zmin)<=COORD:ring['bottom'].add(index)
   if abs(p[2]-zmax)<=COORD:ring['top'].add(index)
 source=truth['volume'];origin=v[0];volume=math.fsum(dot(sub(v[a],origin),cross(sub(v[b],origin),sub(v[c],origin)))/6 for a,b,c in t);assert volume>0;sag_bound=0.;loss=0.;sampling=[];same_rings=True
 for (x,y,r),ring in zip(holes,rings):
  assert ring['triangles']>0 and len(ring['bottom'])>=3 and len(ring['top'])>=3
  bottom=sorted(math.atan2(v[i][1]-y,v[i][0]-x)%(2*math.pi)for i in ring['bottom']);top=sorted(math.atan2(v[i][1]-y,v[i][0]-x)%(2*math.pi)for i in ring['top']);deltas=[(bottom[(i+1)%len(bottom)]-a)%(2*math.pi)for i,a in enumerate(bottom)];assert all(0<d<=.1+1e-10 for d in deltas);span=max(ring['maxSpan'],max(deltas));sag=r*(1-math.cos(span/2));assert sag<=.01+1e-9;sag_bound+=depth*2*math.pi*r*sag;loss+=r*r*math.fsum(d-math.sin(d)for d in deltas)/2;same_rings=same_rings and len(top)==len(bottom)and all(abs(a-b)<=1e-10 for a,b in zip(top,bottom));sampling.append({'center':[x,y],'radius':r,'bottomSamples':len(bottom),'topSamples':len(top),'maxAngularSpan':span,'maxSagMm':sag})
 assert -ARITHMETIC<=volume-source<=sag_bound+ARITHMETIC,(volume,source,sag_bound)
 polygon=source+depth*loss if same_rings else None
 if polygon is not None:assert abs(volume-polygon)<=ARITHMETIC,(volume,polygon)
 probes=[([x,y,(zmin+zmax)/2],False,'bore-center')for x,y,r in holes]+[([xmin+5,ymin+5,(zmin+zmax)/2],True,'corner-material'),([xmax+1,(ymin+ymax)/2,(zmin+zmax)/2],False,'external')]
 if len(holes)==1:probes.append(([holes[0][0]+6,holes[0][1],(zmin+zmax)/2],witness_material,'D10-to-D14-witness'))
 observed=[]
 for p,material,label in probes:
  w=winding(v,t,p);assert abs(w-int(material))<=WINDING,(p,w,material);observed.append({'point':p,'expectedMaterial':material,'meshWinding':w,'label':label})
 canonical=[]
 for tri in t:
  q=tuple(tuple(0. if x==0 else x for x in v[i])for i in tri);canonical.append(min(q,q[1:]+q[:1],q[2:]+q[:2]))
 digest=hashlib.sha256(json.dumps(sorted(canonical),separators=(',',':')).encode()).hexdigest()
 return{'vertices':len(v),'triangles':len(t),'euler':len(v)-len(edges)+len(t),'meshBounds':{'min':lo,'max':hi},'analyticVolume':source,'meshVolume':volume,'approximationResidual':volume-source,'measuredSagBound':sag_bound+ARITHMETIC,'requestedControlBound':depth*.01*2*math.pi*sum(r for x,y,r in holes)+ARITHMETIC,'prismaticPolygonVolume':polygon,'sampling':sampling,'points':observed,'canonicalOrientedTriangleSha256':digest}
