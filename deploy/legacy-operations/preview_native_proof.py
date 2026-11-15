"""Bind historical frontend installation to a separately proven native upgrade."""
import json

def validate_native(root, health, activation):
    current = {role: str(record['pid']) for role, record in health['processes'].items()}
    if activation['nativePidsUnchanged'] == current:
        return None
    upgrade = json.loads((root / '.build/checks/native10-webhost-upgrade-result.json').read_text())
    assert upgrade['status'] == 'PASS'
    assert upgrade['beforePids'] == activation['nativePidsUnchanged']
    assert upgrade['onlineRoleRelease'] == health['onlineRoleRelease'] == upgrade['installedRelease']
    assert upgrade['rootReceiptSHA256'] == health['nativeUpgradeReceiptSHA256']
    assert upgrade['frontendManifestSHA256'] == health['frontendManifestSHA256']
    assert upgrade['rollout']['status'] == 'upgraded'
    assert upgrade['rollout']['guestCookiePreserved'] and upgrade['rollout']['keysAuthorityAndExistingAccountsPreserved']
    assert not upgrade['rollout']['dataRestored']
    assert health['persistentCookieMatchesRunningGuest']
    return upgrade
