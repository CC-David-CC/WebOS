#!/usr/bin/env python3
"""Rebuild a closed SDK-only update independently; delete the temporary copy."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(base,base_pin,candidate,candidate_pin):
    contract=module('network_validation_contract',base/'origin_service/release.py')
    builder=module('network_validation_builder',ROOT/'scripts/build-network-update.py')
    assert contract.verify(base)['manifestSHA256']==base_pin
    assert contract.verify(candidate)['manifestSHA256']==candidate_pin
    manifest=json.loads((candidate/'connected-release.json').read_bytes())['files'];old=json.loads((base/'connected-release.json').read_bytes())['files']
    with tempfile.TemporaryDirectory(prefix='.network-validation-',dir=ROOT/'.build/releases') as temporary:
        rebuilt=Path(temporary)/'release';assert builder.build(base,base_pin,rebuilt)['manifestSHA256']==candidate_pin
        for name in [*manifest,'connected-release.json']:assert (candidate/name).read_bytes()==(rebuilt/name).read_bytes(),name
    assert all(manifest[n]==old[n] for n in contract.V19_NATIVE)
    assert all(manifest.get(n)==r for n,r in old.items() if '/apps/' in n)
    cache=json.loads((candidate/'assets/desktop/cache-manifest.json').read_bytes())
    for name,record in cache['files'].items():assert record==manifest[name],name
    return {'status':'PASS','scope':__doc__,'baseManifestSHA256':base_pin,'manifestSHA256':candidate_pin,'verifiedFiles':len(manifest),'independentRebuildByteEqual':True,'nativeFilesUnchanged':len(contract.V19_NATIVE),'appBundlesUnchanged':True,'cacheRecordsVerified':len(cache['files']),'temporaryRebuildRemoved':True,'sourceSHA256':sha(Path(__file__)),'wholeGoalComplete':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-release',type=Path,required=True);p.add_argument('--base-manifest-sha256',required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--candidate-manifest-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
    v=run(a.base_release.resolve(),a.base_manifest_sha256,a.candidate.resolve(),a.candidate_manifest_sha256);a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
