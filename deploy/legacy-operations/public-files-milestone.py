#!/usr/bin/env python3
"""Bind the exact live personal-files deployment to actual browser/boundary proof."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CHECKS=ROOT/'.build/checks'
NATIVE='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
FRONTEND='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787'
WORKER='aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def receipt(name):
    value=json.loads((CHECKS/name).read_text())
    assert value['status']=='PASS',name
    return value

def check_sources(value):
    for name,expected in value.get('sha256',{}).items():
        assert sha(ROOT/name)==expected,name

if __name__=='__main__':
    names=['native-files-milestone-result.json','files-hosting-activation-result.json','touch-frontend-activation-result.json','files-policy-activation-result.json','webhost-files-preview-health-result.json','public-files-ui-result.json','public-files-cleanup-result.json','touch-public-result.json','general-voice-public-result.json','native11-public-network-result.json','public-files-all-fixtures-result.json']
    values={name:receipt(name) for name in names}
    local,route,frontend,policy,health,files,cleanup,touch,voice,network,all_fixtures=[values[name] for name in names]
    assert local['nativeManifestSHA256']==policy['nativeManifestSHA256']==health['nativeManifestSHA256']==NATIVE
    assert local['frontendManifestSHA256']==frontend['frontendManifestSHA256']==policy['frontendManifestSHA256']==health['frontendManifestSHA256']==FRONTEND
    assert health['privateWorker']['workerManifestSHA256']==WORKER
    assert policy['nativeConfigVersion']==health['nativeConfigVersion']=='codi-managed-instance/4'
    assert policy['otherRolesAndPrivateWorkerPidsUnchanged'] and policy['indexAndGuestCookieUnchanged'] and not policy['dataRestored']
    for role in ['issuer','steward','guest']:assert health['nativePIDs'][role]==int(policy['afterPids']['codi-ksu-hidden-'+role+'.service'])
    for name,value in health['privateWorker']['processes'].items():assert value['pid']==int(policy['afterPids'][name])
    assert health['defaultPublicTLSVerified'] and health['unauthorizedFileAccessDenied'] and health['privateWorker']['anonymousFolders']==0
    assert health['privateWorker']['onlyLoopbackInterface'] and health['privateWorker']['privateDatabasesSeparated']
    assert health['prototypeSHA256']==frontend['desktopSHA256']==route['desktopSHA256']
    assert health['prototypeDeclaredFilesVerified']>40
    assert health['siteDomains']==frontend['siteDomains']==route['siteDomains'] and len(health['siteDomains'])==10
    assert health['hostingSHA256']=={'generator':frontend['generatorSHA256'],'manifest':frontend['manifestSHA256'],'activeCaddy':frontend['activeCaddySHA256']}
    assert files['defaultCertificateTrust'] and files['testFilesRemoved'] and all(v is True for k,v in files['witness'].items() if k!='url')
    assert files['witness']['actualBrowserFileImport'] and files['witness']['actualDownloadedFileMatches']
    assert files['maximumBinaryTransfer']=={'bytes':8388608,'sha256':'dacfface706d4cdf78d46f941d8879a1a6a1c1706f670f08f3f69cc3517a0712'}
    assert files['actualImportAndDownloadSHA256']==hashlib.sha256(bytes(range(256))*16).hexdigest()
    assert cleanup['allOtherAccountPoliciesUnchanged'] and cleanup['accountDatabaseIntegrity'] and all(v['disabled'] and v['testHomeEmpty'] for v in cleanup['fixtures'])
    ledger=json.loads((CHECKS/'public-files-fixtures.json').read_text());assert ledger['accountsDisabled'] and ledger['ownedFilesRemoved']
    assert sorted(v['name'] for v in cleanup['fixtures'])==sorted(ledger['names'])
    assert all_fixtures['allDisabled'] and all_fixtures['allTestHomesEmpty'] and all_fixtures['realAccountRemainsEnabled']
    for value in [files,touch,voice,network,policy,health,all_fixtures]:check_sources(value)
    for name,expected in all_fixtures['ledgerSHA256'].items():assert sha(ROOT/name)==expected
    for name,record in health['frontendFiles'].items():
        assert sha(ROOT/name)==record['sha256']
        for value in [files,touch,network]:
            if name in value['servedAssetsSHA256']:assert value['servedAssetsSHA256'][name]==record['sha256']
    assert files['servedAssetsSHA256']['desktop-apps.js']==sha(ROOT/'desktop-apps.js')
    assert files['servedAssetsSHA256']['gateway/client.mjs']==sha(ROOT/'gateway_service/client.mjs')
    assert voice['actualLocalWhisperWasmInference'] and voice['terminalAndEditorActualDictation'] and voice['touchTapStartsAndStops'] and not voice['audioUploaded'] and voice['gpuNeverAccessed']
    assert len(touch['witnesses'])==2
    assert network['defaultCertificateTrust'] and network['bidirectionalRTC'] and network['separateRoomChatAndMoves'] and network['pgnExportMatchesAcrossPeersAndExcludesChat']
    assert network['publicIceTransportPolicy']=='relay' and not network['clientForcedRelay'] and all(v['pingReplies']>=1 and v['dnsAndHttp'] for v in network['guestInternet'])
    result={'status':'PASS','scope':'Exact live /hidden native11/schema4/R15 personal-files deployment, default-trusted browser import/download/save/reload/isolation/8MiB and emulated touch, CPU voice and real RTC chat/separate chess/guest Internet; all ten sites/prototype and private worker boundaries retained',
            'nativeManifestSHA256':NATIVE,'frontendManifestSHA256':FRONTEND,'workerManifestSHA256':WORKER,
            'registeredPrivateFilesLive':True,'anonymousServerHomes':0,'testAccountsDisabled':True,'testFilesRemoved':True,
            'guestFilesAutomaticallyServerMounted':False,'privateLANShareSelected':False,'identityBoundOwnWANRuleInstalled':False,
            'physicalAndroidVerified':False,'independentWANVerified':False,'fullRoadmapComplete':False,
            'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'public-files-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
