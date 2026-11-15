#!/usr/bin/env python3
"""Bind actual independent-shell browser checks to the installed R12 assets."""
import hashlib
import json
from preview_native_proof import validate_native
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT / '.build/checks'
names = ['independent-shells-result.json', 'independent-shells-public-result.json',
         'general-voice-result.json', 'general-voice-public-result.json',
         'touch-preview-result.json', 'touch-public-result.json',
         'touch-frontend-activation-result.json', 'preview-touch-live-health-result.json',
         'touch-milestone-result.json', 'speech-milestone-result.json']
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
receipts = {name: json.loads((CHECKS / name).read_text()) for name in names}
for name, value in receipts.items():
    assert value['status'] == 'PASS', name
    for source, expected in value.get('sha256', {}).items():
        assert digest(ROOT / source) == expected, (name, source)

local, public = [receipts[name] for name in names[:2]]
assert public['url'] == 'https://ksu.codes/hidden/'
assert local['sha256'] == public['sha256']
flags = ['distinctPtys', 'unprivilegedShells', 'independentCwdEnvironmentAndOutput',
         'foregroundJobsSurviveWorkspaceSwitch', 'ctrlCOnlyInterruptsTargetShell',
         'sharedGuestFiles', 'newWindowFromSingleTaskAndApplications',
         'otherWindowsRemainVisible', 'minimizeRestoreRetainsShell',
         'exitAndCloseOnlyAffectTargetShell', 'vmNotRestarted']
for receipt in [local, public]:
    assert {w['mode'] for w in receipt['witnesses']} == {'phone touch emulation', 'desktop'}
    for witness in receipt['witnesses']:
        assert witness['workspaceCounts'] == [3, 2]
        for flag in flags:
            assert witness[flag], flag
for name in names[2:4]:
    assert receipts[name]['dictationTargetsIndependentShell']

activation = receipts['touch-frontend-activation-result.json']
health = receipts['preview-touch-live-health-result.json']
bundle = ROOT / '.build/frontends/touch-20261023-r12'
key = digest(bundle / 'frontend.json')
metadata = json.loads((bundle / 'frontend.json').read_text())
assert metadata['version'] == 'codi-frontend-assets/2'
assert set(metadata['files']) == {'app.js', 'style.css', 'terminal.js', 'assets/terminal-initramfs.cpio.gz'}
assert metadata['files'] == activation['frontendFiles']
for name, record in metadata['files'].items():
    assert record == {'bytes': (ROOT / name).stat().st_size, 'sha256': digest(ROOT / name)}
    assert record['sha256'] == local['sha256'][name]
assert key == activation['frontendManifestSHA256'] == health['frontendManifestSHA256']
assert activation['indexAndGuestCookieUnchanged'] and activation['nativeConfigUnchanged']
assert health['currentWebsitePrototypeBytesPreserved']
assert health['hostingSHA256'] == {'generator': activation['generatorSHA256'],
                                 'manifest': activation['manifestSHA256'],
                                 'activeCaddy': activation['activeCaddySHA256']}
assert health['hostingActivationReceiptSHA256'] == digest(CHECKS / 'touch-frontend-activation-result.json')
native_upgrade=validate_native(ROOT,health,activation)
assert len(health['siteResults']) == 9 and set(health['siteResults'].values()) == {'PASS'}
assert health['sharedIngressConfigured']

result = {'status': 'PASS', 'scope': 'Real local/public HTTPS Chrome independent guest PTYs, shells, jobs, workspace/window lifecycle, shared files and dictation; phone touch emulation and desktop, no independent WAN or physical-phone claim',
          'frontendManifestSHA256': key, 'sourceCommit': activation['sourceCommit'],
          'liveNativeRelease': health['onlineRoleRelease'],
          'nativeServicesPrototypeAndNineSitesPreserved': True,
          'publicTurnListenerConfigured': health['publicTurnListenerConfigured'],
          'issuerTurnPolicyConfigured': health['issuerTurnPolicyConfigured'], 'fullObjectiveComplete': False,
          'receipts': {name: digest(CHECKS / name) for name in names},
          'nativeProofCheckerSHA256':digest(ROOT/'scripts/preview_native_proof.py'),'checkerSHA256': digest(Path(__file__))}
(CHECKS / 'independent-shells-milestone-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
