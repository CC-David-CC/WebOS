"""Journal a forward-only native/file/guest mount and authority transition.

No account, document, key, replay ledger or usage database is copied/restored.
The existing maintenance slot blocks ordinary native starts/renewals while this
operator owns an unfinished migration. Rollback is another forward transition.
"""
from copy import deepcopy
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import secrets
import selectors
import subprocess
import sys
import time

from . import authority
from .backends import encoded, sha, MAXIMUM

VERSION = 'codi-mount-transition/1'
PHASES = ['prepared', 'stopped', 'publishers-prepared', 'reserved', 'authority',
          'publishers', 'exports', 'backends', 'configured', 'starting', 'committed']


class BackendClient:
    def __init__(self, config, kind, overlay):
        value = config['userFiles' if kind == 'files' else 'guestNetwork']
        args = [config['python'], '-I', '-B', str(overlay/'backends.py'), '--kind', kind,
                '--config-dir', str(Path(value['configFile']).parent),
                '--operator', value['operatorRelease'], '--operator-sha256', value['operatorManifestSHA256'],
                '--config-sha256', value['configSHA256']]
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})

    def call(self, action, **value):
        raw = json.dumps({'action': action, **value}, separators=(',', ':')).encode() + b'\n'
        if len(raw) > MAXIMUM:
            raise ValueError('Bounded backend request required')
        self.process.stdin.write(raw)
        self.process.stdin.flush()
        result = bytearray()
        deadline = time.monotonic() + 120
        with selectors.DefaultSelector() as poll:
            poll.register(self.process.stdout, selectors.EVENT_READ)
            while not result.endswith(b'\n'):
                remaining = deadline-time.monotonic()
                if remaining <= 0 or not poll.select(remaining):
                    raise ValueError('Backend helper deadline exceeded; retain migration journal')
                chunk = os.read(self.process.stdout.fileno(), min(65536, MAXIMUM+1-len(result)))
                if not chunk:
                    raise ValueError('Backend helper ended: '+self.process.stderr.read(2000).decode(errors='replace'))
                result.extend(chunk)
                if len(result) > MAXIMUM:
                    raise ValueError('Backend helper response exceeded bound')
        value = json.loads(result)
        if value.get('ok') is not True:
            raise ValueError('Backend '+action+' refused: '+value.get('error', 'unknown error'))
        return value['value']

    def close(self):
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)
        self.process.stdout.close()
        self.process.stderr.close()


def load_operator(release, pin):
    release = Path(release).absolute()
    if sha((release/'connected-release.json').read_bytes()) != pin:
        raise ValueError('Exact native release pin required')
    for p in [release, *release.parents, *release.rglob('*')]:
        info = p.lstat()
        if p.is_symlink() or info.st_uid or info.st_mode & 0o022:
            raise ValueError('Protected immutable native release required')
    spec = importlib.util.spec_from_file_location('codi_mount_native', release/'scripts/manage-services.py')
    op = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = op
    spec.loader.exec_module(op)
    if op.verify(release)['manifestSHA256'] != pin:
        raise ValueError('Native release verification differs')
    return op


def slot(config_path):
    return Path(config_path).parent/'maintenance.json'


def write_journal(op, config_path, journal, phase, hook):
    if phase not in PHASES:
        raise ValueError('Unknown mount phase')
    journal['phase'] = phase
    op.atomic(slot(config_path), encoded(journal))
    hook(phase)


def native_units(op, config):
    for role in [*op.ROLES, 'issuer-bootstrap']:
        name = op.unit(config, role)
        file = Path(config['unitDir'])/name
        for root in ['/etc/systemd/system', '/run/systemd/system', '/usr/lib/systemd/system']:
            other = Path(root)/name
            if (Path(root)/(name+'.d')).exists() or other != file and (other.exists() or other.is_symlink()):
                raise ValueError('Unmanaged native unit/drop-in during mount transition')
        loaded = dict(line.split('=', 1) for line in op.systemctl('show', name, '-p', 'FragmentPath', '-p', 'DropInPaths').splitlines())
        if loaded['FragmentPath'] != str(file) or loaded['DropInPaths']:
            raise ValueError('Loaded native unit differs from managed file')


def public_files(op, before, after, plan, config_path, preimages=None):
    state = Path(before['stateRoot'])
    private = state/'operator/staging/steward-private/provisioned'
    result = {}

    def original(path, owner, mode):
        if preimages is None:
            return op.read_owned(path, owner, mode, MAXIMUM)
        record = preimages[str(path)]
        if record['owner'] != owner or record['mode'] != mode:
            raise ValueError('Journaled metadata ownership/mode differs')
        return record['before'].encode()

    def put(path, raw, mode=0o600, owner=0, group=0):
        path = Path(path)
        old = original(path, owner, mode)
        result[str(path)] = {'before': old.decode(), 'after': raw.decode(), 'mode': mode,
                             'owner': owner, 'group': group}

    old = plan['before']
    new = plan['after']
    base = after['basePath']
    discovery = json.loads(original(state/'public/origin-discovery.json', 0, 0o444))
    if discovery['identity'] != old['identity_policy'] or discovery['pin']['endpoints'] != [old['endpoint']] or discovery['sourcePath'] != before['basePath']+'/discovery.json':
        raise ValueError('Original discovery context differs from authority')
    policy = deepcopy(discovery)
    policy['identity'] = new['identity_policy']
    policy['pin']['endpoints'] = [new['endpoint']]
    policy['sourcePath'] = base+'/discovery.json'
    seed = authority.validate(plan)[0]
    if discovery['pin']['realm'] != old['realm'] or discovery['pin']['rootKey'] != old['root_key'] or discovery['scope'] != seed['stewards'][0]['scopes'][0]:
        raise ValueError('Original discovery trust anchors differ')
    put(state/'public/origin-discovery.json', encoded(policy), 0o444)
    put(private/'origin-discovery.json', encoded(policy))
    if json.loads(original(private/'provision.json', 0, 0o600)) != old:
        raise ValueError('Original staged provision differs from signed authority')
    put(private/'provision.json', encoded(new))
    person = pwd.getpwnam('codi-steward')
    if json.loads(original(state/'steward/provision.json', person.pw_uid, 0o600)) != old:
        raise ValueError('Original runtime provision differs from signed authority')
    put(state/'steward/provision.json', encoded(new), owner=person.pw_uid, group=person.pw_gid)
    cached = json.loads(original(state/'operator/issuer-config.json', 0, 0o600))
    if cached['identity'] != old['identity_policy'] or cached['vm']['manifest'] != before['basePath']+'/vm/manifest.json':
        raise ValueError('Saved issuer boot metadata differs from original mount')
    cached['identity'] = new['identity_policy']
    cached['vm']['manifest'] = base+'/vm/manifest.json'
    put(state/'operator/issuer-config.json', encoded(cached))
    frontend_path = Path(before['guestNetwork']['frontendFile'])
    frontend_before = original(frontend_path, 0, 0o644)
    if sha(frontend_before) != before['guestNetwork']['frontendSHA256']:
        raise ValueError('Original frontend descriptor pin differs')
    descriptor = json.loads(frontend_before)
    if descriptor['basePath'] != before['basePath'] or descriptor['issuerPolicy'] != old['identity_policy']:
        raise ValueError('Guest frontend context differs')
    descriptor['basePath'] = base
    descriptor['issuerPolicy'] = new['identity_policy']
    raw = encoded(descriptor)
    after['guestNetwork']['frontendSHA256'] = sha(raw)
    put(frontend_path, raw, 0o644)
    for role in [*op.ROLES, 'issuer-bootstrap']:
        put(Path(before['unitDir'])/op.unit(before, role), op.render(after, role), 0o644)
    put(config_path, encoded(after))
    return result


def prepare(op, config_path, base, seconds, clients, config):
    from origin_service import maintenance, deployment
    from steward.root_authority import RootAuthority
    if json.loads(op.read_owned(config_path, 0, 0o600)) != config:
        raise ValueError('Native configuration changed during preparation')
    maintenance.guard(op, config, config_path)
    if any((config_path.parent/n).exists() for n in ['native-rollout.json', 'guest-signin-migration.json']):
        raise ValueError('Another native transition is pending')
    if config['version'] != 'codi-managed-instance/5' or not config.get('userFiles') or not config.get('guestNetwork'):
        raise ValueError('Explicit installed native/file/guest system required')
    base = op.validate_base_path(base)
    if base == config['basePath']:
        raise ValueError('Requested mount is already current')
    if deployment.active(op, config) != list(op.ROLES):
        raise ValueError('All three native roles must be ready before preparing migration')
    native_units(op, config)
    binding = maintenance.binding(Path(config['stateRoot']))
    fence = maintenance.fence(op, config, config_path, binding)
    plan = authority.prepare(RootAuthority(Path(config['stateRoot'])/'operator/root'), base,
                             seconds=seconds, minimum_revision=max(binding['rootRevision'], fence['rootFloor']))
    backend_plans = {name: client.call('prepare', basePath=base, issuerPolicy=plan['after']['identity_policy'])
                     for name, client in clients.items()}
    after = deepcopy(config)
    after['basePath'] = base
    for name, field in [('files', 'userFiles'), ('guest', 'guestNetwork')]:
        after[field]['configSHA256'] = sha(encoded(backend_plans[name]['after']))
    exports = public_files(op, config, after, plan, config_path)
    return {'version': VERSION, 'id': secrets.token_hex(16), 'created': int(time.time()),
            'phase': 'prepared', 'before': config, 'after': after, 'authority': plan,
            'backends': backend_plans, 'publicFiles': exports, 'publishers': None,
            'fenceBefore': fence, 'bindingBefore': binding}


def publisher(op, config, overlay, journal, which, action, prepared=None):
    state = Path(config['stateRoot'])
    ledger = state/('operator/staging/steward-private/provisioned/ledger' if which == 'staged' else 'steward/ledger')
    code = '''import json,sys
sys.path[:0]=sys.argv[1:3]
from mount_operator import authority as m
from steward.publisher import PublisherState
p=PublisherState(sys.argv[3]);v=json.load(sys.stdin);plan=v['authority'];prepared=v['prepared']
if v['action']=='prepare':r=m.publisher_plan(p,plan,allow_unbound=v['staged'])
else:
 row=m.publisher_row(p)
 if row in [prepared['before'],prepared['after']]:changed=m.apply_publisher(p,plan,prepared);r={'changed':changed,'alreadyPublished':False}
 else:
  old,new,_,_=m.validate(plan);m.validate_publisher_row(row,plan['after'],new,False)
  if row[3]<=prepared['before'][3]:raise ValueError('Publisher did not advance monotonically')
  r={'changed':False,'alreadyPublished':True}
print(json.dumps(r))
'''
    args = [config['python'], '-I', '-B', '-c', code, str(overlay.parent), config['release'], str(ledger)]
    if which == 'runtime':
        args = ['/usr/sbin/runuser', '-u', 'codi-steward', '--', *args]
    value = {'authority': journal['authority'], 'prepared': prepared, 'action': action, 'staged': which == 'staged'}
    result = subprocess.run(args, input=json.dumps(value), text=True, capture_output=True, timeout=30)
    if result.returncode or len(result.stdout) > MAXIMUM:
        raise ValueError('Owner-separated publisher '+action+' refused: '+result.stderr[-2000:])
    return json.loads(result.stdout)


def validate_journal(op, config_path, journal, clients):
    expected = {'version', 'id', 'created', 'phase', 'before', 'after', 'authority', 'backends',
                'publicFiles', 'publishers', 'fenceBefore', 'bindingBefore'}
    if set(journal) != expected or journal['version'] != VERSION or journal['phase'] not in PHASES:
        raise ValueError('Unknown mount journal retained for explicit review')
    before, after = journal['before'], journal['after']
    if Path(op.ROOT) != Path(before['release']):
        raise ValueError('Migration operator differs from the original native release')
    _, new, old_base, new_base = authority.validate(journal['authority'])
    if before['basePath'] != old_base or after['basePath'] != new_base:
        raise ValueError('Native mount differs from signed plan')
    stable = lambda c: {k: v for k, v in c.items() if k not in ['basePath', 'userFiles', 'guestNetwork']}
    if stable(before) != stable(after):
        raise ValueError('Mount journal changed native code/state/trust/ports')
    for name, field in [('files', 'userFiles'), ('guest', 'guestNetwork')]:
        left, right = before[field], after[field]
        allowed = ['configSHA256', 'frontendSHA256'] if name == 'guest' else ['configSHA256']
        if {k: v for k, v in left.items() if k not in allowed} != {k: v for k, v in right.items() if k not in allowed}:
            raise ValueError('Backend installation binding changed')
        plan = journal['backends'][name]
        if plan['after']['basePath'] != new_base or plan['policyAfter'] != journal['authority']['after']['identity_policy'] or sha(encoded(plan['after'])) != right['configSHA256']:
            raise ValueError('Backend mount plan differs from native signed context')
        clients[name].call('validate', plan=plan)
    if json.loads(op.read_owned(config_path, 0, 0o600)) not in [before, after]:
        raise ValueError('Native configuration changed outside migration')
    # Output paths are derived from the before/after instance, not a journal's
    # arbitrary write requests. Re-derive all after bytes and compare exactly.
    records = journal['publicFiles']
    reconstructed = deepcopy(after)
    if public_files(op, before, reconstructed, journal['authority'], config_path, records) != records or reconstructed != after:
        raise ValueError('Journaled native metadata differs from derived mount outputs')
    known = {str(config_path), str(Path(before['guestNetwork']['frontendFile']))}
    state = Path(before['stateRoot'])
    known |= {str(state/p) for p in ['public/origin-discovery.json', 'operator/issuer-config.json',
              'operator/staging/steward-private/provisioned/origin-discovery.json',
              'operator/staging/steward-private/provisioned/provision.json', 'steward/provision.json']}
    known |= {str(Path(before['unitDir'])/op.unit(before, role)) for role in [*op.ROLES, 'issuer-bootstrap']}
    if set(records) != known:
        raise ValueError('Unexpected native metadata output path')
    for path, record in records.items():
        if set(record) != {'before', 'after', 'mode', 'owner', 'group'}:
            raise ValueError('Unexpected metadata record')
        steward = path == str(state/'steward/provision.json')
        who = pwd.getpwnam('codi-steward')
        if record['owner'] != (who.pw_uid if steward else 0) or record['group'] != (who.pw_gid if steward else 0):
            raise ValueError('Metadata owner changed')
        actual = op.read_owned(path, record['owner'], record['mode'], MAXIMUM).decode()
        if actual not in [record['before'], record['after']]:
            raise ValueError('Metadata changed outside journaled preimages')
    if records[str(config_path)]['after'].encode() != encoded(after):
        raise ValueError('Native config output differs')
    for role in [*op.ROLES, 'issuer-bootstrap']:
        path = str(Path(before['unitDir'])/op.unit(before, role))
        if records[path]['after'].encode() != op.render(after, role) or records[path]['before'].encode() != op.render(before, role):
            raise ValueError('Native unit sandbox differs')
    if journal['publishers'] is not None and set(journal['publishers']) != {'staged', 'runtime'}:
        raise ValueError('Exact two publisher plans required')
    return new


def reserve(op, config_path, journal):
    from steward.protocol import jose
    file = config_path.parent/'recovery-fence.json'
    before = journal['fenceBefore']
    revision = authority.validate(journal['authority'])[1]['revision']
    after = {**before, 'rootFloor': revision}
    current = json.loads(op.read_owned(file, 0, 0o600)) if file.exists() else before
    if current not in [before, after]:
        raise ValueError('Independent recovery fence differs; do not reset its floor')
    op.atomic(file, encoded(after))


def perform(op, config_path, journal, overlay, clients, hook):
    from origin_service import maintenance
    from steward.root_authority import RootAuthority
    from origin_service.discovery import DiscoverySource
    validate_journal(op, config_path, journal, clients)
    before, after = journal['before'], journal['after']
    for role in ['guest', 'steward', 'issuer', 'issuer-bootstrap']:
        op.systemctl('stop', op.unit(before, role))
        op.inactive(before, role)
    for name in ['guest', 'files']:
        clients[name].call('stop', plan=journal['backends'][name])
    write_journal(op, config_path, journal, 'stopped', hook)
    if journal['publishers'] is None:
        journal['publishers'] = {name: publisher(op, before, overlay, journal, name, 'prepare')
                                 for name in ['staged', 'runtime']}
    write_journal(op, config_path, journal, 'publishers-prepared', hook)
    reserve(op, config_path, journal)
    write_journal(op, config_path, journal, 'reserved', hook)
    root = RootAuthority(Path(before['stateRoot'])/'operator/root')
    authority.apply(root, journal['authority'])
    write_journal(op, config_path, journal, 'authority', hook)
    for name in ['staged', 'runtime']:
        publisher(op, before, overlay, journal, name, 'apply', journal['publishers'][name])
    write_journal(op, config_path, journal, 'publishers', hook)
    # Keep native units/config until backend metadata has been safely replaced.
    late = {str(config_path), *(str(Path(before['unitDir'])/op.unit(before, role)) for role in [*op.ROLES, 'issuer-bootstrap'])}
    def apply_files(selected):
        for path, record in journal['publicFiles'].items():
            if (path in late) != selected:
                continue
            actual = op.read_owned(path, record['owner'], record['mode'], MAXIMUM).decode()
            if actual not in [record['before'], record['after']]:
                raise ValueError('Metadata preimage changed during application')
            if actual != record['after']:
                op.atomic(path, record['after'].encode(), record['mode'], record['owner'], record['group'])
    apply_files(False)
    write_journal(op, config_path, journal, 'exports', hook)
    for name in ['files', 'guest']:
        clients[name].call('apply', plan=journal['backends'][name])
    write_journal(op, config_path, journal, 'backends', hook)
    apply_files(True)
    op.systemctl('daemon-reload')
    write_journal(op, config_path, journal, 'configured', hook)
    clients['files'].call('start')
    clients['guest'].call('start')
    # Native validation uses each backend's own locks, so release the helper
    # locks only after all metadata edits and backend starts are complete.
    for client in clients.values():
        client.close()
    clients.clear()
    op.load(config_path)
    native_units(op, after)
    write_journal(op, config_path, journal, 'starting', hook)
    for role in ['steward', 'issuer', 'guest']:
        state = op.systemctl('show', op.unit(after, role), '-p', 'ActiveState', '--value').strip()
        if state == 'failed':
            op.systemctl('reset-failed', op.unit(after, role))
        op.systemctl('start', op.unit(after, role))
        if role == 'steward':
            source = DiscoverySource(Path(after['stateRoot'])/'public/origin-discovery.json',
                                     Path(after['stateRoot'])/'public/steward/bundle.json',
                                     journal['authority']['after']['identity_policy'], after['basePath'])
            deadline = time.monotonic()+20
            while True:
                try:
                    bundle = source.read()
                    if bundle['seed'] != journal['authority']['after']['seed']:
                        raise ValueError('Waiting for new signed root bundle')
                    break
                except (OSError, ValueError, KeyError):
                    if time.monotonic() >= deadline:
                        raise ValueError('New steward publication is unavailable; retain mount journal')
                    time.sleep(.1)
        op.ready(after, [role])
    op.ready(after, list(op.ROLES))
    actual = maintenance.binding(Path(after['stateRoot']))
    expected = journal['bindingBefore']
    if any(actual[n] != expected[n] for n in ['issuerKeyId', 'rootKeyId', 'realm', 'serviceKeyId', 'accounts']) or actual['rootRevision'] <= expected['rootRevision'] or actual['publisherRevision'] <= expected['publisherRevision']:
        raise ValueError('Final identity, accounts or monotonic authority binding differs')
    maintenance.guard_epoch(op, after, config_path)
    write_journal(op, config_path, journal, 'committed', hook)
    result = {'status': 'mount-migrated', 'id': journal['id'], 'beforeBasePath': before['basePath'],
              'basePath': after['basePath'], 'rootRevision': actual['rootRevision'],
              'publisherRevision': actual['publisherRevision'], 'dataRestored': False,
              'keysRealmAccountsPreserved': True, 'hostingChanged': False}
    op.atomic(config_path.parent/'mount-last-result.json', encoded(result))
    slot(config_path).unlink()
    maintenance.sync_directory(config_path.parent)
    return result


def run(op, config_path, mode, base='', seconds=86400, hook=lambda phase: None):
    config_path = Path(config_path)
    overlay = Path(__file__).parent
    with op.locked(config_path):
        pending = slot(config_path)
        if mode == 'recover':
            journal = json.loads(op.read_owned(pending, 0, 0o600, MAXIMUM))
            config = journal['before']
        else:
            if pending.exists():
                raise ValueError('An existing maintenance operation requires explicit recovery')
            config = op.load(config_path)
        with ExitStack() as stack:
            clients = {}
            for name in ['files', 'guest']:
                client = BackendClient(config, name, overlay)
                clients[name] = client
                stack.callback(client.close)
            if mode != 'recover':
                journal = prepare(op, config_path, base, seconds, clients, config)
                if mode == 'plan':
                    return {'status': 'mount-prepared-readonly', 'beforeBasePath': config['basePath'],
                            'basePath': base, 'rootRevision': authority.validate(journal['authority'])[1]['revision'],
                            'metadataFiles': len(journal['publicFiles'])+sum(len(p['files']) for p in journal['backends'].values()),
                            'servicesChanged': False, 'dataRestored': False}
                write_journal(op, config_path, journal, 'prepared', hook)
            return perform(op, config_path, journal, overlay, clients, hook)
