#!/usr/bin/env python3
"""Bind current app sources to real repeat-close, desktop and bundler evidence."""
import hashlib
import json
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parent.parent
records={}
def read(name):
    raw=(ROOT/'.build/checks'/name).read_bytes();records[name]=hashlib.sha256(raw).hexdigest();value=json.loads(raw);assert value['status']=='PASS',name;return value
stress=read('public-app-lifecycle-stress-result.json');desktop=read('public-app-desktop-result.json');build=read('public-app-build-result.json')
assert stress['cyclesPerApp']==26 and stress['ordinaryOpensAndCloses']==182 and len(stress['apps'])==7
assert len(stress['checks'])==13 and len(desktop['checks'])==8 and len(build['checks'])==29
assert any('26 closed Linux shell PIDs' in c for c in stress['checks'])
for sample in stress['samples']:assert sample['resources']==stress['samples'][0]['resources'] and sample['budget']==stress['samples'][0]['budget']
for proof in [stress,desktop,build]:
    for name,pin in proof['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,name
for proof in [stress,desktop]:
    for name,pin in proof['appSourcesSHA256'].items():assert hashlib.sha256((ROOT.parent/'served_apps_public'/name/'index.mjs').read_bytes()).hexdigest()==pin,name
catalog=json.loads((ROOT/'assets/desktop/apps.json').read_text());assert catalog['hostAPI']==2
for app in catalog['apps']:
    folder=(ROOT/app['path']).parent
    for name,record in app['files'].items():
        raw=(folder/name).read_bytes();assert record=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
public={}
for name,pin in [('app.js','9e9cb6ecc22e3886c8cb6af6593035880d4f88facba4ab6a2dbdb6169c547bd2'),('assets/terminal-initramfs.cpio.gz','670aca33bf51ffacec21eb0340a8c7f55356d5c9298ca9b55288d955fb5a7d9b')]:
    with urllib.request.urlopen('https://ksu.codes/hidden/'+name,timeout=20) as response:raw=response.read(4194305)
    assert len(raw)<=4194304 and hashlib.sha256(raw).hexdigest()==pin;public[name]=pin
result={'status':'PASS','scope':__doc__,'receiptSHA256':records,'totalChecks':50,'opensAndCloses':182,'cyclesPerApp':26,'lateOperationsCovered':['guest text read','Files write finishing after Close','PGN selection before asynchronous file read','already-running PGN worker'],'resourceSamples':stress['samples'],'catalogSHA256':hashlib.sha256((ROOT/'assets/desktop/apps.json').read_bytes()).hexdigest(),'liveAssetsSHA256':public,'liveChanged':False,'xtermRealTerminalMigrated':False,'physicalAndroidTested':False,'unboundedLifetimeOrHeapLeakProof':False,'connectedPeerChurnCovered':False,'registeredPrivateFileChurnCovered':False,'fullGoalComplete':False}
(ROOT/'.build/checks/public-app-lifecycle-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':50,'ordinaryOpensAndCloses':182,'liveChanged':False}))
