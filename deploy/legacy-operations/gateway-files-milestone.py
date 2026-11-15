#!/usr/bin/env python3
"""Bind the private file candidate, executed worker and distinct local UI evidence."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker-release',type=Path,required=True);args=parser.parse_args()
    worker=args.worker_release.resolve();key=sha(worker/'files-service.json');manifest=json.loads((worker/'files-service.json').read_text())
    expected={*('gateway_service/'+n for n in ['__init__.py','auth.py','policy.py','user_store.py','http.py','transfers.py','client.mjs']),
              'codiserver-server-v0.3.0/codiauth/__init__.py','codiserver-server-v0.3.0/codiauth/jose.py','scripts/serve-user-files.py','requirements.lock'}
    assert manifest['version']=='codi-private-file-service/1' and set(manifest['files'])==expected
    assert {str(p.relative_to(worker)) for p in worker.rglob('*') if p.is_file()}==expected|{'files-service.json'}
    for name,value in manifest['files'].items():
        assert not (worker/name).is_symlink()
        assert value=={'bytes':(worker/name).stat().st_size,'sha256':sha(worker/name)}
        assert (worker/name).read_bytes()==(ROOT/name).read_bytes(),name
    counts={'user-storage-result.json':31,'origin-lifecycle-result.json':90,'gateway-auth-result.json':26,
            'gateway-transfer-result.json':8,'gateway-http-result.json':11}
    names=[*counts,'gateway-browser-result.json','gateway-files-ui-result.json','touch-preview-result.json','gateway-live-preservation-result.json']
    reports={name:json.loads((CHECKS/name).read_text()) for name in names}
    for name,report in reports.items():
        assert report['status']=='PASS',name
        if name in counts:assert report['tests']==counts[name],name
        for source,expected_sha in report.get('sha256',{}).items():assert sha(ROOT/source)==expected_sha,(name,source)
    browser=reports['gateway-browser-result.json'];ui=reports['gateway-files-ui-result.json']
    assert browser['executedWorkerManifestSHA256']==ui['workerManifestSHA256']==key
    assert len(browser['witnesses'])==len(ui['witnesses'])==2
    for witness in browser['witnesses']:
        assert witness['real8MiBBinaryRoundtrip']==8*1024*1024
        assert witness['guestReadsRestoredServerFile'] and witness['actualGatewayProcessRestart']['actualProcessChanged']
        assert witness['anotherAccountCannotReadFile'] and witness['serverRejectsLoggedOutToken']
    for witness in ui['witnesses']:
        assert witness['actualEditorSaveAndRead'] and witness['versionConflictPreservesDraft']
        assert witness['serverToGuestExplicitCopy'] and witness['guestToServerExplicitSave']
        assert witness['lateResponseCannotPopulateOtherAccount'] and witness['otherAccountUIIsolation']
        assert witness['serverFileSurvivesBrowserReload'] and witness['mobileViewportAndTrustedTouchSave']
    live=reports['gateway-live-preservation-result.json']
    assert live['frontendManifestSHA256']=='179a5b5677686c3b2f131aede94639f0f9f0c6c6882a5e83370d8d9f6fc639e9'
    assert live['prototypeBytesPreserved'] and not live['servicesRestarted'] and not live['accountsModified']
    result={'status':'PASS','scope':'Local private file worker, identity/ACL/storage/traffic boundaries and current Files/editor UI; no live activation or independent WAN claim',
            'workerManifestSHA256':key,'workerFiles':len(expected),'tests':counts,
            'receiptSHA256':{name:sha(CHECKS/name) for name in names},
            'frontendSourceSHA256':{name:sha(ROOT/name) for name in ['app.js','desktop-apps.js','style.css']},
            'issuerCandidateSHA256':{name:sha(ROOT/name) for name in ['origin_service/lifecycle.py','origin_service/gateway_authority.py']},
            'limitations':{'fileServiceInstalled':False,'fileAPIRoutedOnLiveSite':False,'liveFilesPersistToServer':False,
                           'guestNetworkIdentityRuleInstalled':False,'serverVolumeAutomaticallyMountedInGuest':False,
                           'issuerSessionsSurviveRestart':False,'independentWANVerified':False,'physicalAndroidVerified':False},
            'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'gateway-files-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
