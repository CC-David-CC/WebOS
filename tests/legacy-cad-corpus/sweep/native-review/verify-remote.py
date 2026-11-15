"""Read-only CODE/runtime provenance checks; run through `ssh r730 python3 -`."""
import hashlib,json,pathlib,subprocess
root=pathlib.Path('/mnt/data10tb/codi-occ-owned-sweep-main-20261107-r1')
repo='/mnt/data10tb/codi-occ-owned-sweep-20261107'
commit='c3e949db01cf646de540e8b6c52e39cd36ebfb8d'
pins=json.loads((root/'runtime-pins.json').read_bytes())
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as stream:
  for data in iter(lambda:stream.read(1048576),b''):h.update(data)
 return h.hexdigest()
record={'nativeSourceCommit':commit,'runtime':{},'sourceAtCommit':{},'rawReceiptSHA256':digest(root/'receipt-r3.json'),'scope':'read-only source/runtime hash consistency, no rebuild or native execution'}
for name,key in [('occ-portable.js','jsSha256'),('main.wasm','wasmSha256')]:
 actual=digest(root/name);assert actual==pins[key];record['runtime'][name]=actual
for name,expected in pins['sourceFiles'].items():
 actual=hashlib.sha256(subprocess.check_output(['git','-C',repo,'show',commit+':'+name])).hexdigest();assert actual==expected;record['sourceAtCommit'][name]=actual
for name in ['shape-io/selectedProfileV2.hpp','occt/src/TopAbs/TopAbs_State.hxx']:
 record['sourceAtCommit'][name]=hashlib.sha256(subprocess.check_output(['git','-C',repo,'show',commit+':'+name])).hexdigest()
assert record['rawReceiptSHA256']=='01a4fc7348672264ae6fc6fb0fd0b9da8fb1cdba138c7db5e45598eab9354f2b'
print(json.dumps(record,indent=2))
