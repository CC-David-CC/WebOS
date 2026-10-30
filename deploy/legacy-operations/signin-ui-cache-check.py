#!/usr/bin/env python3
"""Verify coherent API1 security UI/cache against the installed retained VM."""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import time
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-signin-r7'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
if __name__=='__main__':
    report={'status':'FAIL','liveWebhostChanged':False}
    try:
        vm=module('signin_cache_vm',ROOT/'scripts/prepare-native-network-vm.py');vm.status()
        runtime=module('signin_cache_runtime',ROOT/'scripts/upgrade-signin-native-vm.py').runtime()
        pin=hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest();assert runtime['manifestSHA256']==pin
        raw=subprocess.run([*vm.ssh_args(),'cat /srv/codi-network-fixture/installed-result.json'],capture_output=True,text=True,check=True,timeout=30).stdout;installed=json.loads(raw)
        cache=module('signin_cache_browser',ROOT/'scripts/device-cache-browser-check.py');cache.ROOT=RELEASE
        result=cache.browser(SimpleNamespace(origin=installed['publicOrigin'],base='/hidden',chromeArgs=['--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]))
        assert result['status']=='PASS';report.update(result,scope=__doc__,nativeManifestSHA256=pin,fixtureCertificatePinUsed=True,defaultPublicTLSVerified=False)
    finally:
        report['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();report['browserSourceSHA256']=hashlib.sha256((ROOT/'scripts/device-cache-browser-check.py').read_bytes()).hexdigest()
        out=ROOT/'.build/checks/signin-ui-cache-result.json'
        if out.exists():out.rename(out.with_name('signin-ui-cache-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
