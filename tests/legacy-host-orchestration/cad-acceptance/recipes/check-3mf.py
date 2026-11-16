"""Reuse the independently qualified geometry/group/interface oracle.

Only its fixed material-name/color expectation is changed to the exact README
recipe; all geometric/volume/winding/manifold/grouping assertions stay intact.
"""
import argparse,hashlib,json,types
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--oracle',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
raw=a.oracle.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='74e350b7163d030b40d381fd3d617aa54906bfc4aa031920ede022dddded625a'
old="[('PLA','#D24B4B'),('PETG','#4B78D2'),('TPU','#FFFFFF')]"
new="[('PLA','#3366CC'),('PLA','#3366CC'),('TPU','#FFFFFF')]"
source=raw.decode();assert source.count(old)==1;source=source.replace(old,new)
module=types.ModuleType('exact_recipe_3mf_oracle');exec(compile(source,str(a.oracle),'exec'),module.__dict__)
module.check(a.model,100)
with ZipFile(a.model) as archive:root=ET.fromstring(archive.read('3D/3dmodel.model'))
ns={'c':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
mesh_count=0
for mesh in root.findall('./c:resources/c:object/c:mesh',ns):
 edges=Counter()
 for tri in mesh.findall('./c:triangles/c:triangle',ns):
  x,y,z=(int(tri.get(k)) for k in ('v1','v2','v3'))
  for edge in ((x,y),(y,z),(z,x)):edges[edge]+=1
 assert all(count==1 and edges[(b,a)]==1 for (a,b),count in edges.items())
 mesh_count+=1
assert mesh_count==3
result={'status':'PASS','scope':'Independent ZIP/XML original geometry/group/interface oracle with one exact predeclared material expectation substitution, plus directed closed-edge winding check','oracleSHA256':sha(raw),'adaptedOracleSHA256':sha(source.encode()),'onlySubstitution':{'before':old,'after':new},'modelSHA256':sha(a.model.read_bytes()),'modelBytes':a.model.stat().st_size,'width':100,'objects':2,'regions':3,'triangles':84,'allThreeMeshesConsistentDirectedEdgeWinding':True,'pairedLabelInterfaceAreaSquareMillimeters':920}
a.receipt.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
