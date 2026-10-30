#!/usr/bin/env python3
"""Default-trusted Chrome cache/offline/rebuild proof for the strict live release."""
import hashlib,importlib.util,json,time,urllib.request
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-signin-r7'
if __name__=='__main__':
    report={'status':'FAIL','liveServicesChanged':False}
    try:
        with urllib.request.urlopen('https://ksu.codes/hidden/app.js',timeout=15) as response:assert hashlib.sha256(response.read()).hexdigest()==hashlib.sha256((RELEASE/'app.js').read_bytes()).hexdigest()
        with urllib.request.urlopen('https://ksu.codes/hidden/config.json',timeout=15) as response:assert json.load(response)['guestNetwork']['previewPolicy']['anonymousInternet']=='deny'
        spec=importlib.util.spec_from_file_location('public_signin_cache',ROOT/'scripts/device-cache-browser-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=RELEASE
        report.update(m.browser(SimpleNamespace(origin='https://ksu.codes',base='/hidden')),scope=__doc__,defaultCertificateTrust=True,certificateExceptionUsed=False)
    finally:
        report['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/public-signin-cache-result.json'
        if out.exists():out.rename(out.with_name('public-signin-cache-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
