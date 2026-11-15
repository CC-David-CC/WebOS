#!/usr/bin/env python3
"""Exercise a labeled ten-second public warning; never restart live services."""
import base64
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('public_maintenance_browser',ROOT/'scripts/touch-preview-check.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers);call,wait=helpers.call,helpers.wait
PYTHON='/srv/codi-connected/venvs/517179c/bin/python';NATIVE=None;EXPECTED=None
def remote(command):return subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n',*command],check=True,capture_output=True,text=True,timeout=45).stdout
def snapshot():
    code="""import hashlib,json,subprocess
from pathlib import Path
p=Path('/etc/codi-connected/ksu/managed.json');c=json.loads(p.read_text());assert c['version']=='codi-managed-instance/5' and c['manifestSHA256']==EXPECTED
assert hashlib.sha256((Path(c['release'])/'connected-release.json').read_bytes()).hexdigest()==EXPECTED
print(json.dumps({'release':c['release'],'configSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'pids':{r:int(subprocess.check_output(['systemctl','show','codi-ksu-hidden-'+r+'.service','-p','MainPID','--value'],text=True)) for r in ['issuer','steward','guest']}}))
""".replace('EXPECTED',repr(EXPECTED))
    return json.loads(remote(['/usr/bin/python3','-I','-B','-c',shlex.quote(code)]))
def publish(phase):
    argv=[PYTHON,'-I','-B',NATIVE+'/scripts/desktop-maintenance.py','--directory','/var/lib/codi-connected/ksu/public',phase,'--in-seconds','10' if phase=='scheduled' else '0','--duration','300','--message','Maintenance warning test: please save your work. This short exercise will briefly lock the desktop; the server will remain online.']
    result=json.loads(remote([shlex.join(argv)]));assert not result['servicesRestarted'] and not result['workSaved'];return result
def run():
    global NATIVE
    before=snapshot();sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];announced=False
    NATIVE=before['release']
    def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    try:
        call('/session/'+sid+'/url',{'url':'https://ksu.codes/hidden/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked'),150)
        js('window.d=[...surfaces.values()][0];d.launch("text")');wait(lambda:js('return !!document.querySelector(".guest-editor")'),20)
        js('window.keepVM=v86Instance;window.keepFS=v86Instance.fs9p;window.keepSID=currentSession.id;window.keepEditor=document.querySelector(".guest-editor");keepEditor.value="Public maintenance demo draft";keepEditor.dispatchEvent(new Event("input",{bubbles:true}));keepEditor.focus();keepEditor.setSelectionRange(4,9)')
        result=publish('scheduled');announced=True
        wait(lambda:js('return !document.querySelector("#desktop-recovery").hidden&&document.querySelector("#desktop-recovery").textContent.includes("Maintenance warning test")'),7)
        assert js('return document.querySelector("#desktop-recovery").textContent.includes("Nothing is automatically saved")')
        js('document.querySelector("#desktop-recovery button").click()')
        assert js('return !document.querySelector("#maintenance-banner").hidden&&!desktopLab.lifecycle.blocked')
        wait(lambda:js('return desktopLab.lifecycle.blocked'),13)
        assert js('return document.querySelector("#previews").inert&&document.querySelector("#voice-control").inert&&!document.querySelector("#desktop-recovery").hidden')
        raw=call('/session/'+sid+'/screenshot');image=ROOT/'.build/checks/public-maintenance-lock.png';image.write_bytes(base64.b64decode(raw))
        js('document.querySelector("[aria-label=Applications]").click()');assert js('return !document.querySelector(".menu-pane")')
        publish('cancelled');announced=False;wait(lambda:js('return !desktopLab.lifecycle.blocked'),10)
        assert js('return v86Instance===keepVM&&v86Instance.fs9p===keepFS&&currentSession.id===keepSID&&keepEditor.isConnected&&keepEditor.value==="Public maintenance demo draft"&&keepEditor.selectionStart===4&&keepEditor.selectionEnd===9')
        assert snapshot()==before
        return {'status':'PASS','scope':__doc__,'url':'https://ksu.codes/hidden/','defaultCertificateTrust':True,'certificateExceptionUsed':False,'countdownSeconds':10,'clearlyLabeledTest':True,'forcedPopupAndBanner':True,'desktopAndVoiceInertAtDeadline':True,'appControlsBlocked':True,'sameLinuxFilesystemSessionDraftAndCursorRetained':True,'liveServicesRestarted':False,'workAutomaticallySaved':False,'beforeAndAfter':before,'screenshot':str(image),'physicalAndroidVerified':False}
    finally:
        if announced:publish('cancelled')
        try:js('desktopLifecycle?.stop();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--release-dir',type=Path,default=ROOT/'.build/releases/connected-routed-r8');args=parser.parse_args()
    EXPECTED=hashlib.sha256((args.release_dir/'connected-release.json').read_bytes()).hexdigest()
    with urllib.request.urlopen('https://ksu.codes/hidden/index.html',timeout=20) as response:assert response.read()==(args.release_dir/'index.html').read_bytes()
    result={'status':'FAIL','scope':__doc__}
    try:result.update(run())
    finally:
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/public-maintenance-check.py','scripts/desktop-maintenance.py','assets/desktop/lifecycle.mjs','app.js']};output=ROOT/'.build/checks/public-maintenance-result.json'
        if output.exists():output.rename(output.with_name('public-maintenance-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
