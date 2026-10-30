"""Compose existing code/mount/hosting operators without restoring user state.

The caller holds the hosting controller lock. Each native child owns its existing
instance/backend locks and journals. The mount's committed callback applies and
verifies hosting before its maintenance slot can be cleared. A failed callback
therefore leaves the existing native start/signing guard in force.
"""
import hashlib
import json
from pathlib import Path
import secrets
import time

VERSION = 'codi-site-cutover/1'
PHASES = ['prepared', 'code', 'website', 'mount-entering', 'mount', 'hosting',
          'verified', 'committed']


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)+'\n').encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def run(driver, action, hook=lambda event: None):
    """Apply/recover one exact immutable plan. Rollback uses a new inverse plan."""
    if action not in ('plan', 'apply', 'recover'):
        raise ValueError('Explicit plan, apply or recover required')
    driver.validate_plan()
    path = Path(driver.config_path).parent/'site-cutover.json'
    op = driver.op
    plan_hash = digest(driver.plan)

    def load():
        value = json.loads(op.read_owned(path, 0, 0o600, 16777216))
        required = {'version', 'id', 'created', 'planSHA256', 'phase', 'website',
                    'mountBefore', 'mountID', 'mountResult', 'hostingBackups', 'verification'}
        if set(value) != required or value['version'] != VERSION or value['planSHA256'] != plan_hash or value['phase'] not in PHASES:
            raise ValueError('Different or invalid site cutover journal; preserve it for review')
        if not isinstance(value['id'], str) or len(value['id']) != 32 or any(c not in '0123456789abcdef' for c in value['id']):
            raise ValueError('Invalid cutover identity')
        return value

    def save(phase):
        if phase not in PHASES:
            raise ValueError('Unknown site phase')
        journal['phase'] = phase
        op.atomic(path, encoded(journal))

    def event(name):
        # Fault hooks run only after the corresponding durable operator output.
        hook(name)

    if action == 'plan':
        if path.exists():
            raise ValueError('An existing cutover needs explicit recovery')
        driver.preflight()
        return {'status': 'site-cutover-prepared-readonly', 'planSHA256': plan_hash,
                'basePath': driver.target_base, 'servicesChanged': False, 'dataRestored': False}
    if action == 'recover':
        journal = load()
    else:
        if path.exists():
            raise ValueError('An existing cutover needs explicit recovery')
        driver.preflight()
        journal = {'version': VERSION, 'id': secrets.token_hex(16), 'created': int(time.time()),
                   'planSHA256': plan_hash, 'phase': 'prepared', 'website': None,
                   'mountBefore': None, 'mountID': None, 'mountResult': None,
                   'hostingBackups': None, 'verification': None}
        save('prepared')
        event('prepared')

    def reached(phase):
        return PHASES.index(journal['phase']) >= PHASES.index(phase)

    driver.notice(journal['id'], journal['created'])
    event('notice')

    # These two steps are independently safe at the old mount. A crash between
    # them leaves a coherent old URL, and the next mount plan is made afresh.
    if not reached('code'):
        driver.ensure_code()
        save('code')
        event('code')
    if not reached('website'):
        journal['website'] = driver.ensure_website(journal['website'])
        save('website')
        event('website')
    else:
        driver.check_website(journal['website'])

    from mount_operator.coordinator import run as migrate
    native_slot = Path(driver.config_path).parent/'maintenance.json'

    def on_mount(phase):
        inner = json.loads(op.read_owned(native_slot, 0, 0o600, 4194304))
        driver.check_mount_journal(inner, journal['mountBefore'])
        if journal['mountID'] is not None and journal['mountID'] != inner['id']:
            raise ValueError('Different native mount operation; preserve both journals')
        journal['mountID'] = inner['id']
        # Initial parent identity is durable before any authority/file changes.
        save('mount')
        event('mount-'+phase)
        if phase == 'committed':
            if journal['hostingBackups'] is None:
                journal['hostingBackups'] = driver.backup_hosting()
                save('hosting')
            driver.ensure_hosting(event)
            save('hosting')
            event('hosting')
            journal['verification'] = driver.verify()
            save('verified')
            event('verified')
            # The normal native maintenance slot remains present until this
            # callback returns, even after all services/routes are ready.
            save('committed')
            event('committed')

    if native_slot.exists():
        if journal['mountBefore'] is None:
            raise ValueError('Unrelated native maintenance operation is pending')
        inner = json.loads(op.read_owned(native_slot, 0, 0o600, 4194304))
        driver.check_mount_journal(inner, journal['mountBefore'])
        if journal['mountID'] is not None and journal['mountID'] != inner['id']:
            raise ValueError('Native/parent cutover identity differs')
        result = migrate(op, driver.config_path, 'recover', hook=on_mount)
        journal['mountResult'] = result
        save('committed')
    elif reached('committed'):
        # A crash after the inner journal's unlink must not mint a second root.
        journal['verification'] = driver.verify()
        save('committed')
    else:
        if reached('mount'):
            raise ValueError('Expected native mount journal is missing; do not invent authority state')
        driver.before_mount()
        journal['mountBefore'] = driver.current_config()
        save('mount-entering')
        event('mount-entering')
        result = migrate(op, driver.config_path, 'apply', driver.target_base,
                         driver.plan['seconds'], on_mount)
        journal['mountResult'] = result
        save('committed')
    result = {'status': 'site-cutover-completed', 'id': journal['id'],
              'planSHA256': plan_hash, 'basePath': driver.target_base,
              'website': journal['website'], 'mount': journal['mountResult'],
              'verification': journal['verification'], 'hostingBackups': journal['hostingBackups'],
              'dataRestored': False, 'workSaved': False}
    # Persist the receipt before removing only our own pending operation. The
    # inverse deployment is another plan/authority revision, never a DB restore.
    driver.finish(result)
    event('receipt')
    path.unlink()
    directory = __import__('os').open(path.parent, __import__('os').O_RDONLY|__import__('os').O_DIRECTORY)
    try:
        __import__('os').fsync(directory)
    finally:
        __import__('os').close(directory)
    return result
