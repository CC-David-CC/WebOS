"""Write-ahead, single-epoch live-renewal coordination.

Backends must hold the managed lock for the entire operation and independently
enforce custody, pins, signed state, service identity and publisher floor.
This module is not an installed service or an unattended signer.
"""
from origin_service.expired_root_recovery import RecoveryJournal
from origin_service.expired_root_steps import make_checkpoint
from steward.protocol import jose


class LiveRenewalJournal(RecoveryJournal):
    @staticmethod
    def validate(record):
        required = {'version', 'baseline', 'checkpoint', 'configSHA256',
                    'releaseSHA256', 'publisherRevision', 'seconds', 'renewalWindow'}
        if not isinstance(record, dict) or set(record) != required or record['version'] != 'codi-live-root-renewal/1':
            raise ValueError('Invalid live renewal journal')
        projected = {k: record[k] for k in ('checkpoint', 'configSHA256', 'releaseSHA256', 'publisherRevision', 'seconds')}
        projected['version'] = 'codi-expired-root-recovery/1'
        RecoveryJournal.validate(projected)
        window = record['renewalWindow']
        if type(window) is not int or not 1 <= window < record['seconds']:
            raise ValueError('Renewal window must be shorter than the new lifetime')
        if not isinstance(record['baseline'], str) or len(record['baseline']) > 12000:
            raise ValueError('Bounded serialized baseline required')
        if make_checkpoint(jose.loads(record['baseline'])) != record['checkpoint']:
            raise ValueError('Signed baseline differs from checkpoint')
        return record


def execute(backend, journal, *, resume=False, phase=lambda name: None):
    """Advance at most one epoch or resume a previously journaled epoch.

    backend methods must re-read and verify state immediately before mutation;
    receipt must be idempotent. Any failure leaves the journal in place.
    """
    with backend.locked():
        if resume:
            record = journal.load()
        else:
            record = journal.validate(backend.initial())
            action = backend.decide(record)
            if action == 'wait':
                return {'status': 'not-due', 'rootRevision': record['checkpoint']['baseRevision']}
            if action != 'renew-once':
                raise ValueError('New renewal requires coherent running authority')
            journal.create(record)
            phase('prepared')
        for _ in range(4):
            action = backend.decide(record)
            if action == 'verify-running':
                backend.verify(record)
                phase('verified')
                backend.receipt(record)
                phase('receipt')
                journal.remove(record)
                return {'status': 'renewed', 'rootRevision': record['checkpoint']['baseRevision'] + 1}
            methods = {'renew-once': 'renew', 'export-committed': 'export', 'start-steward': 'start'}
            if action not in methods:
                raise ValueError('Journaled renewal is no longer actionable')
            phase('before-' + action)
            getattr(backend, methods[action])(record)
            phase('after-' + action)
        raise ValueError('Renewal did not converge within bounded steps')
