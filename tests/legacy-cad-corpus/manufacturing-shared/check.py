#!/usr/bin/env python3
"""Independent persisted-file and frozen-driver checker, not a new browser run."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;folder=root/'evidence-r1'
r=json.loads((folder/'receipt.json').read_text());assert r['status']=='PASS'
assert r['ownedContextClosed'] and r['sharedBrowserDisconnectedOnly']
assert r['syntheticGeometry'] is False and r['syntheticStorage'] is False
assert r['filesystemRace'] is False and r['crossAccountProbes'] is False
assert r['driverPinsAfter']==r['driverPins']
for name,pin in r['driverPins'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==pin,name
rows=r['rows'];assert len(rows)==11
find=lambda label:next(row for row in rows if row['label']==label)
assert find('Repeated assignment is a token-preserving no-op')['receipt']['changed'] is False
assignment=find('Public generic material assignment');assert assignment['assignment']['authoredUndo'] and assignment['assignment']['changed']
a=(folder/'material-plate.jsketcher.json').read_bytes();b=(folder/'reopened-material-plate.jsketcher.json').read_bytes();assert a==b
value=json.loads(a);assert value['format']=='codi-jsketcher-project' and value['version']==2 and value['unit']=='millimeter'
history=value['project']['model']['history'];assert [op['type'] for op in history]==['PLANE','WORKER_SELECTED_PROFILE_EXTRUDE_V2','WORKER_THROUGH_HOLES_V1']
assert history[1]['params']['depth']==20 and history[2]['params']['diameter']==10
for op in history[1:]:assert op['params']['engineRevision']=='sha256:32eec74e3019d9e2d767c9016f05aa3daa49441c6102423a269d67b9c7f02a08:abbf2aa02a6f2101c600aa1eedd20fa80ab2db206e677ca860d9c5103cdfbfcc'
m=value['manufacturing'];assert m==assignment['metadata']
assert m['materials']==[{'id':'pla','name':'PLA'}]
assert m['appearances']==[{'id':'blue','name':'Blue','color':'#3366ff'}]
assert m['bindings']==[{'featureId':history[2]['params']['featureId'],'id':'worker-body-3','operationType':'WORKER_THROUGH_HOLES_V1'}]
assert m['objects']==[{'id':'plate','name':'Mounting plate','regions':[{'id':'main','bodyId':'worker-body-3','materialId':'pla','appearanceId':'blue','transform':[1,0,0,0,1,0,0,0,1,0,0,0]}]}]
for label in ['material-plate normal native Save and server sync','reopened-material-plate normal native Save and server sync']:
 row=find(label);assert row['sha256']==hashlib.sha256(a).hexdigest() and row['bytes']==len(a)
print(json.dumps({'status':'PASS','bytes':len(a),'sourceAndMaterialIdentitiesRetained':True,'reopenedBytesIdentical':True,'scope':'recorded signed workflow/frozen driver and independent native file checks; not new Native execution or 3MF qualification'},indent=2))
