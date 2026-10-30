#!/usr/bin/env python3
"""Bind actual controlled frontend/issuer/browser/credential proofs to live state."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def load(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,digest in value.get('sha256',{}).items():assert sha(ROOT/path)==digest,(name,path)
    return value
REMOTE='''import hashlib,json,subprocess
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
file=Path('/etc/codi-guest-network/ksu/managed.json');assert sha(file)=='5bef7160dca8db409f2c5f9309d295b62ed8e87994c5c348b8ede95a9a37c8ba'
c=json.loads(file.read_bytes());operator=Path(c['operatorRelease'])
assert sha(operator/'guest-operator.json')==c['operatorSHA256']=='8411c84aab2b284418951371b2ee9822797a70599c016c375bb409cb40f641d1'
v=subprocess.run([c['python'],'-I','-B',str(operator/'scripts/manage-guest-network.py'),'status','--config-dir',str(file.parent)],check=True,capture_output=True,text=True,timeout=90)
status=json.loads(v.stdout);assert status['status']=='inspected' and not status['active'] and not status['guardFault'] and not status['kernelMatches'] and not status['bootEnabled']
for value in status['units'].values():assert value['ActiveState']=='inactive' and value.get('MainPID','0')=='0' and value['UnitFileState']=='static'
tables=subprocess.run(['/usr/sbin/nft','list','tables'],check=True,capture_output=True,text=True).stdout
assert 'table inet codi_guest_egress' not in tables
assert Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
assert Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001']
print(json.dumps({'status':'PASS','configSHA256':sha(file),'operatorStatus':status,'hostGuestEgressTableAbsent':True,'servicesRestarted':False,'privateDataRead':False}))
'''

if __name__=='__main__':
    names=['guest-controlled-frontend-result.json','guest-frontend-runtime-result.json','guest-relay-result.json','guest-authorization-result.json','connected-release-result.json','webhost-files-preview-health-result.json']
    frontend,runtime,legacy,auth,release,health=[load(name) for name in names]
    assert [(v['basePath'],v['enabled'],len(v['checks'])) for v in frontend['witnesses']]==[('',False,14),('/hidden',False,14),('',True,32),('/hidden',True,32)]
    assert not frontend['liveChanged'] and not frontend['installedCredentialTest'] and not frontend['kernelIntegration']
    for witness in frontend['witnesses']:
        assert witness['actualIssuerCLI']
        if not witness['enabled']:continue
        browser=witness['desktop']
        for key in ['actualDesktopLinuxReady','actualAccountMenu','sameVMAndFilesystem','independentShellsPreserved','workspaceAndEditorPreserved','sameNetworkSocketAcrossAccounts','registeredCookieReconnect','durableUsageEnabled','quotaDenialKeepsIdentityAndVM','quotaRestorationResumesRegisteredWire']:assert browser[key],key
        assert not browser['browserErrors']
    assert len(runtime['checks'])==16 and runtime['realSystemdCredentialMount'] and runtime['fixtureCleaned'] and not runtime['kernelPolicyApplied'] and not runtime['liveChanged']
    assert runtime['copiedSourceSHA256']=={name:sha(ROOT/name) for name in runtime['copiedSourceSHA256']}
    assert runtime['checks'][-2:]==[{'name':'actual managed guest CLI serves matching config and exact gated SDK','result':'PASS'},{'name':'actual managed CLI refuses issuer mismatch without legacy fallback','result':'DENIED'}]
    assert len(legacy['checks'])==87 and auth['tests']==28 and release['tests']==16
    for value in (auth,release):assert value['failures']==value['errors']==0
    assert health['nativeManifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0' and health['nativeConfigVersion']=='codi-managed-instance/4'
    assert health['frontendManifestSHA256']=='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787'
    assert health['defaultPublicTLSVerified'] and health['prototypeDeclaredFilesVerified']==133 and len(health['siteDomains'])==10 and not health['servicesRestarted'] and not health['personalFileContentsRead']
    for role,pid in health['nativePIDs'].items():assert pid=={'issuer':240953,'steward':239112,'guest':239113}[role]
    result=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],capture_output=True,text=True,timeout=120)
    assert result.returncode==0,result.stderr;standby=json.loads(result.stdout)
    with urllib.request.urlopen('https://ksu.codes/hidden/config.json',timeout=20) as response:
        config=json.load(response);assert config['gateway']['version']=='codi-user-files/1' and config['guestNetwork'].get('authorization') is None
    for path in ['guest-access/client.mjs','api/v1/guest-network/challenge']:
        request=urllib.request.Request('https://ksu.codes/hidden/'+path,**({'data':b'{}','method':'POST','headers':{'Origin':'https://ksu.codes','Content-Type':'application/json'}} if path.startswith('api/') else {}))
        try:
            with urllib.request.urlopen(request,timeout=20) as response:status=response.status
        except urllib.error.HTTPError as error:status=error.code
        assert status==404,(path,status)
    value={'status':'PASS','scope':__doc__,'actualIssuerCLIOffAndOnVerified':True,'actualRootAndHiddenDesktopVerified':True,'managedFrontendCredentialAndCLIEntryVerified':True,'native12OrSchema5Implemented':False,'nativeControllerTransitionVerified':False,'installedBrowserWorkerKernelWholeChainVerified':False,'privateFilesGUIWithNewNetworkVerified':False,'liveNetworkPolicyActivated':False,'independentWANVerified':False,'physicalAndroidVerified':False,'fullGoalComplete':False,'liveStandby':standby,'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'guest-controlled-frontend-milestone-result.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
