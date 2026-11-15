"""Classify a journaled live root renewal; this module never signs or writes.

The caller must hold the managed locks, protect the saved baseline, validate
the independent fence and publisher ledger, and enforce file/key custody.
This is source-only and is not an installed unattended signer.
"""
from origin_service.expired_root_steps import _verified, make_checkpoint, next_step


def inspect(baseline, root, staged, live, checkpoint, *, fence_revision, now,
            steward_running, ledger_verified, renewal_window):
    """Choose one action, rejecting forks, stale baselines and clock rollback.

    A journal must retain the original signed baseline and its checkpoint.
    After the root commits, only export/verification is permitted; this makes
    an interruption incapable of authorizing another signature for the epoch.
    """
    if make_checkpoint(baseline) != checkpoint:
        raise ValueError('Signed baseline differs from trusted checkpoint')
    if type(now) is not int or now < 1 or type(renewal_window) is not int or not 1 <= renewal_window <= 86400:
        raise ValueError('Bounded current time and renewal window required')
    if type(steward_running) is not bool or type(ledger_verified) is not bool:
        raise ValueError('Exact state and ledger verification flags required')
    key, realm = baseline['root_key'], baseline['realm']
    values = [_verified(item, key, realm) for item in (baseline, root, staged, live)]
    if any(binding != checkpoint['bindingHash'] or grant != checkpoint['grantHash'] for _, _, binding, grant in values):
        raise ValueError('Authority binding changed')
    claims = [value[0] for value in values]
    if any(claim['iat'] > now for claim in claims):
        raise ValueError('Authority clock moved backwards')
    original, current = claims[:2]
    base = checkpoint['baseRevision']
    if current['revision'] == base + 1 and (current['iat'] < original['iat'] or current['exp'] <= original['exp']):
        raise ValueError('Renewed authority does not advance its lifetime')
    # Reuse the conservative epoch/hash/fence ordering checks. Runtime status
    # and expiry are evaluated below for live renewal rather than recovery.
    next_step(base_revision=base, target_revision=base + 1,
              root_revision=current['revision'], fence_revision=fence_revision,
              staged_revision=claims[2]['revision'], live_revision=claims[3]['revision'],
              base_hash=checkpoint['seedHash'], root_hash=values[1][1],
              staged_hash=values[2][1], live_hash=values[3][1],
              root_expired=current['revision'] == base, steward_running=False,
              bindings_verified=True, ledger_verified=ledger_verified)
    if current['revision'] == base:
        if not steward_running or not original['iat'] <= now < original['exp']:
            raise ValueError('A running steward and unexpired authority are required')
        if original['exp'] - now > renewal_window:
            return 'wait'
        return 'renew-once'
    if now >= current['exp']:
        raise ValueError('Committed authority expired; explicit recovery required')
    if claims[2]['revision'] != current['revision'] or claims[3]['revision'] != current['revision']:
        return 'export-committed'
    return 'verify-running' if steward_running else 'start-steward'
