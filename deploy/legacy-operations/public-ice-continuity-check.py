#!/usr/bin/env python3
"""Observe the real public issuer policy restart in one disposable browser tab.

The operator runs separately. This check never restarts a service, saves private
files or reloads a tab, and its temporary Linux data is only a memory witness.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('continuity_browser', ROOT/'scripts/touch-preview-check.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
call, wait = helpers.call, helpers.wait
output = ROOT/'.build/checks/public-ice-continuity-result.json'
armed = ROOT/'.build/checks/public-ice-continuity-armed.json'
sid = None
result = {'status': 'FAIL', 'scope': __doc__}
try:
    assert not armed.exists(), 'Inspect prior witness before starting another'
    sid = call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome', 'args': ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage']}}}})['sessionId']
    def js(code, args=[]):
        return call('/session/'+sid+'/execute/sync', {'script': code, 'args': args})
    call('/session/'+sid+'/timeouts', {'script': 120000})
    call('/session/'+sid+'/url', {'url': 'https://ksu.codes/hidden/'})
    wait(lambda: js('return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked'), 150)
    assert js('return isSecureContext&&identityConfig.rtc.preference.preferred==="relay"&&currentSession.trust.level==="test-server"')
    js('window.savedVM=v86Instance;window.savedFS=v86Instance.fs9p;window.savedEpoch=desktopLab.lifecycle.epoch;window.savedSession=currentSession.id;[...surfaces.values()][0].launch("text")')
    wait(lambda: js('return !!document.querySelector(".guest-editor")'), 20)
    js('window.savedEditor=document.querySelector(".guest-editor");savedEditor.value="unsaved public restart draft";savedEditor.dispatchEvent(new Event("input",{bubbles:true}));savedEditor.focus();savedEditor.setSelectionRange(2,7)')
    js('sendTerminal(2,arguments[0])', ["export PUBLIC_ICE_KEEP=kept_shell; printf kept_file > /home/guest/public-ice-keep.txt; printf '\\nPUBLIC_ICE_ARMED\\n'\r"])
    wait(lambda: js('return serialScreen.text().includes("\\nPUBLIC_ICE_ARMED\\n")'), 30)
    armed.write_text(json.dumps({'status': 'armed', 'publicPolicyBefore': 'relay', 'browserMemoryWitnessReady': True})+'\n')
    print('Owned public Chrome tab armed for the separately managed restart', flush=True)
    until = time.monotonic()+420
    saw_blocked = False
    while time.monotonic()<until:
        state = js('return {blocked:desktopLab.lifecycle.blocked,changed:desktopLab.lifecycle.epoch!==savedEpoch,policy:identityConfig.rtc.preference.preferred,sessionChanged:currentSession.id!==savedSession}')
        saw_blocked |= state['blocked']
        if state['changed'] and state['sessionChanged'] and state['policy']=='all' and not state['blocked']:
            break
        time.sleep(.25)
    else:
        raise AssertionError('Public policy restart/recovery not observed')
    assert saw_blocked, 'Maintenance never blocked the owned desktop'
    assert js('return v86Instance===savedVM&&v86Instance.fs9p===savedFS&&savedEditor.isConnected&&savedEditor.value==="unsaved public restart draft"&&savedEditor.selectionStart===2&&savedEditor.selectionEnd===7')
    token = 'PUBLIC_ICE_'+str(time.time_ns())
    js('sendTerminal(2,arguments[0])', ['printf "\\n'+token+'=%s:" "$PUBLIC_ICE_KEEP"; cat /home/guest/public-ice-keep.txt\r'])
    wait(lambda: js('return serialScreen.text().includes(arguments[0])', ['\n'+token+'=kept_shell:kept_file']), 30)
    value = call('/session/'+sid+'/execute/async', {'script': 'const done=arguments[0];import("./network/peer.mjs").then(({PeerLink})=>{const link=new PeerLink(currentSession,identityConfig);try{link.create();done(link.pc.getConfiguration().iceTransportPolicy)}finally{link.close()}}).catch(e=>done({error:e.message}));', 'args': []})
    assert value=='all', value
    result.update(status='PASS', defaultCertificateTrust=True, actualIssuerEpochChange=True, maintenanceControlsBlocked=True, automaticRecovery=True, sameLinuxAndFilesystem=True, sameShellAndGuestFile=True, sameEditorDraftAndSelection=True, nativePolicyAfter='all', noReload=True, workAutomaticallySaved=False, realUserAccountUsed=False, independentWANVerified=False, physicalAndroidVerified=False)
finally:
    if sid:
        try: js('desktopLifecycle?.stop();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        finally: call('/session/'+sid, method='DELETE')
    armed.unlink(missing_ok=True)
    result['sha256'] = {'scripts/public-ice-continuity-check.py': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
