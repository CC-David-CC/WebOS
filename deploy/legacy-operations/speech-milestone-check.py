#!/usr/bin/env python3
"""Bind local/public voice behavior to the installed immutable speech assets."""
import hashlib
import importlib.util
import json
from preview_native_proof import validate_native
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT / '.build/checks'
names = ['general-voice-result.json', 'general-voice-public-result.json',
         'speech-activation-result.json', 'preview-touch-live-health-result.json',
         'touch-milestone-result.json']
receipts = {name: json.loads((CHECKS / name).read_text()) for name in names}
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for name, receipt in receipts.items():
    assert receipt['status'] == 'PASS', name
    for source, expected in receipt.get('sha256', {}).items():
        assert digest(ROOT / source) == expected, source
local, public, activation, health, touch = [receipts[name] for name in names]
assert public['url'] == 'https://ksu.codes/hidden/'
assert not public['audioUploaded'] and public['physicalMicrophoneNotTested']
flags = ['preloadBeforeAnyVoiceGesture', 'preloadNeverOpensMicrophone',
         'actualLocalWhisperWasmInference', 'dictationTargetsIndependentShell', 'touchTapStartsAndStops', 'recordingIconChanges', 'keyboardSuppressedByDefaultAndExplicitToggleWorks', 'draggableOverlayDoesNotStartRecording', 'floatingOverlayFitsResizedViewport',
         'priorFocusAndEditorSelectionPreserved', 'terminalAndEditorActualDictation',
         'anotherAppCancellationDiscardsText', 'noAutomaticEnterOrSend',
         'workspaceRetainsAppDomDraftAndCursor', 'applicationsTerminalOpensAdditionalWindow',
         'phoneRollUpRestored', 'minimizedTaskCountAndRunningIndicator',
         'workspaceAppIconsAndCountsIndependent', 'workspacePinsIndependent', 'localTaskPickerAndMinimizeRestore', 'workspacesOnlyInTopBar', 'distinctApplicationIcons', 'gpuNeverAccessed']
for receipt in [local, public]:
    for flag in flags:
        assert receipt[flag], flag
    assert receipt['sha256'] == local['sha256']
key = activation['speechManifestSHA256']
spec = importlib.util.spec_from_file_location('speech_export', ROOT / 'scripts/export-speech.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
bundle = exporter.verify(ROOT / '.build/speech-bundles/whisper-tiny-en-20261023-r3')
assert bundle['manifestSHA256'] == health['speechManifestSHA256'] == key
assert bundle['files'] == activation['speechFiles']
for source in ['client.mjs', 'worker.mjs']:
    assert bundle['files'][source]['sha256'] == local['sha256']['assets/speech/' + source]
frontend=json.loads((CHECKS/'touch-frontend-activation-result.json').read_text())
assert frontend['status']=='PASS' and frontend['frontendManifestSHA256']==health['frontendManifestSHA256']
assert {name:value['sha256'] for name,value in frontend['frontendFiles'].items()} == {name: local['sha256'][name] for name in ['app.js', 'style.css', 'terminal.js', 'assets/terminal-initramfs.cpio.gz']}
assert activation['indexAndGuestCookieUnchanged'] and activation['nativeConfigUnchanged']
native_upgrade=validate_native(ROOT,health,activation)
hosting=frontend if health['hostingSHA256']=={'generator':frontend['generatorSHA256'],'manifest':frontend['manifestSHA256'],'activeCaddy':frontend['activeCaddySHA256']} else json.loads((CHECKS/'shared-ingress-apply-result.json').read_text())
assert hosting['status']=='PASS' and health['hostingSHA256'] == {'generator': hosting['generatorSHA256'],
                                 'manifest': hosting['manifestSHA256'],
                                 'activeCaddy': hosting['activeCaddySHA256']}
assert len(health['siteResults']) == 9 and set(health['siteResults'].values()) == {'PASS'}
assert touch['speechActivationReceiptSHA256'] == digest(CHECKS / 'speech-activation-result.json')
result = {'status': 'PASS', 'scope': 'Actual local/public Chrome tap-to-start/stop voice in terminal/editor, CPU model preload, app targeting, cancellation and workspace/task preservation; no physical phone accuracy/latency claim',
          'publicSpeechManifestSHA256': key, 'sourceCommit': activation['sourceCommit'],
          'receipts': {name: digest(CHECKS / name) for name in names},
          'audioUploaded': False, 'physicalPhoneMicrophoneVerified': False,
          'prototypePreserved': True, 'nativeRelease': health['onlineRoleRelease'],
          'fullObjectiveComplete': False, 'frontendSourceCommit':frontend['sourceCommit'], 'frontendActivationReceiptSHA256':digest(CHECKS/'touch-frontend-activation-result.json'), 'nativeProofCheckerSHA256':digest(ROOT/'scripts/preview_native_proof.py'),'checkerSHA256': digest(Path(__file__))}
(CHECKS / 'speech-milestone-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
