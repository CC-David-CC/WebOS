#!/usr/bin/env python3
"""Bind public touch/desktop checks to the exact frontend and hosting receipts."""
import hashlib,json
from preview_native_proof import validate_native
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
names=['touch-preview-result.json','touch-public-result.json','touch-frontend-activation-result.json','preview-touch-live-health-result.json']
receipts={name:json.loads((CHECKS/name).read_text()) for name in names}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,value in receipts.items():
 assert value['status']=='PASS',name
 for source,expected in value.get('sha256',{}).items():
  path=ROOT/source
  if digest(path)!=expected:
   assert source=='scripts/touch-preview-check.py';archived=CHECKS/'fixtures'/('touch-preview-'+expected+'.py');assert digest(archived)==expected
local=receipts[names[0]];public=receipts[names[1]];activation=receipts[names[2]];health=receipts[names[3]]
assert public['url']=='https://ksu.codes/hidden/' and public['servedAssetsSHA256']==local['servedAssetsSHA256']=={name:value['sha256'] for name,value in activation['frontendFiles'].items()}
assert public['bootstrapHTMLSHA256']==health.get('bootstrapHTMLSHA256',activation['bootstrapIndexSHA256'])
assert activation['indexAndGuestCookieUnchanged'] and activation['nativeConfigUnchanged']
native_upgrade=validate_native(ROOT,health,activation)
assert health['frontendManifestSHA256']==activation['frontendManifestSHA256']==digest(ROOT/'.build/frontends/touch-20261023-r12/frontend.json')
hosting=activation if health['hostingSHA256']=={'generator':activation['generatorSHA256'],'manifest':activation['manifestSHA256'],'activeCaddy':activation['activeCaddySHA256']} else json.loads((CHECKS/'shared-ingress-apply-result.json').read_text())
assert hosting['status']=='PASS' and health['hostingSHA256']=={'generator':hosting['generatorSHA256'],'manifest':hosting['manifestSHA256'],'activeCaddy':hosting['activeCaddySHA256']}
speech=json.loads((CHECKS/'speech-activation-result.json').read_text())
assert speech['status']=='PASS' and speech['speechManifestSHA256']==health['speechManifestSHA256']
assert speech['desktopSHA256']==activation['desktopSHA256'] and speech['nativePidsUnchanged']==activation['nativePidsUnchanged']
assert speech['nativeConfigUnchanged'] and speech['indexAndGuestCookieUnchanged']
for witness in public['witnesses']:
 if witness['mode']=='touch emulation':
  for flag in ['topBarWorkspaceIconAndChooserSwitchable','workspacePopupDismissesOnSelectionOutsideAndIconWithoutCloseButton','networkInfoInSessionMenu','allTerminalCommandsAtBottom','terminalPromptVisibleInKeyboardSizedViewport','manualScrollbackPreservedAndTypingResumesFollow','globalVoiceAndTerminalEnterReplaceArrowsAndHelp','nativeTerminalFieldFocused','realGuestCommand','compositionAndDeleteForwarding','dragPreservesInputDom','menuContainedAndTargets44px','singlePaneSubmenus','editorAndFocusSurviveKeyboardSizedViewportAndRotation','statusAutoDismissesAndNewMessageResetsTimer']:assert witness[flag],flag
  assert not witness['actualPhoneOsKeyboardVerified']
 else:assert witness['titleHeightUnchanged']==86 and witness['realGuestKeyboardCommand'] and witness['mouseDragAndFocusPreserveDom'] and witness['maximizeAndRestore']
assert len(health['siteResults'])==9 and set(health['siteResults'].values())=={'PASS'}
report={'status':'PASS','scope':'Exact public frontend touch emulation, real guest terminal commands, composition/delete, menus, resizing/focus, toast timer and desktop mouse/keyboard regressions; no physical phone OS-keyboard claim. Native services, prototype and all nine websites preserved.','receipts':{name:digest(CHECKS/name) for name in names},'publicFrontendManifestSHA256':activation['frontendManifestSHA256'],'liveNativeRelease':health['onlineRoleRelease'],'automatedPhysicalPhoneKeyboardVerified':False,'userReportedPhoneTouchAndTerminalTypingWork':True,'publicTurnConfigured':health.get('publicTurnListenerConfigured',False),'issuerTurnPolicyConfigured':health.get('issuerTurnPolicyConfigured',False),'fullObjectiveComplete':False,'speechActivationReceiptSHA256':digest(CHECKS/'speech-activation-result.json'),'nativeProofCheckerSHA256':digest(ROOT/'scripts/preview_native_proof.py'),'checkerSHA256':digest(Path(__file__))}
(CHECKS/'touch-milestone-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({key:value for key,value in report.items() if key!='receipts'},indent=2))
