"""Managed hosting adapter. No socket listener, user DB restore or route rewrite."""
from contextlib import contextmanager
import copy
import fcntl
import hashlib
import http.client
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import ssl
import stat
import subprocess
import sys
import time
import types

from .coordinator import encoded


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def command(args, timeout=180):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True,
                            timeout=timeout, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    if result.returncode:
        raise ValueError('Operator failed: '+result.stderr[-3000:])
    return result.stdout.strip()


def read(path, limit=134217728):
    p = Path(path)
    for q in [p, *p.parents]:
        if q.is_symlink():
            raise ValueError('Symlink in input: '+str(p))
    with os.fdopen(os.open(p, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK), 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('Regular bounded single-link input required')
        raw = stream.read(info.st_size+1)
        if len(raw) != info.st_size:
            raise ValueError('Input changed during read')
        return raw


def records(folder):
    result = {}
    for name in ['app', 'public']:
        for p in sorted((folder/name).rglob('*')):
            if p.is_dir() and not p.is_symlink():
                continue
            raw = read(p)
            result[str(p.relative_to(folder))] = {'bytes': len(raw), 'sha256': sha(raw)}
    return result


class Managed:
    hostname = 'box-webhost'
    hosting_root = Path('/home/dflanag3/webhost-sites')
    config_path = Path('/etc/codi-connected/ksu/managed.json')
    caddy_file = Path('/etc/caddy/Caddyfile')

    def __init__(self, plan, op):
        self.plan = plan
        self.op = op
        self.target_base = plan['targetBasePath']
        self.root = self.hosting_root
        self.config_path = Path(self.config_path)
        self.source = self.root/'sites/ksu.codes'
        self.ctl = None

    @contextmanager
    def locked(self):
        # A stable controller inode covers source/deploy/render/activation.
        with (self.root/'.controller.lock').open('a+b') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
            yield self

    def module(self, raw, name):
        value = types.ModuleType(name)
        value.__file__ = str(self.root/'ops/common.py')
        exec(compile(raw, value.__file__, 'exec'), value.__dict__)
        return value

    def hosting(self, which):
        value = self.plan[which]
        module = self.module(value['common.py'].encode(), 'site_'+which)
        data = module.tomllib.loads(value['sites.toml'])
        module.validate(data)
        for mode in ['prepare', 'production']:
            if module.caddy(data, mode) != value['Caddyfile.'+mode]:
                raise ValueError('Generated hosting bytes differ from the plan')
        return module, data

    def validate_plan(self):
        if os.geteuid() or socket.gethostname() != self.hostname:
            raise ValueError('Explicit root operator on the designated host required')
        required = {'version', 'sourceCommit', 'beforeConfigSHA256', 'beforeBasePath', 'targetBasePath',
                    'seconds', 'noticeSeconds', 'nativeRelease', 'nativeSHA256', 'oldNativeRelease',
                    'oldNativeSHA256', 'mountOperator', 'mountOperatorSHA256', 'rolloutTool',
                    'rolloutSHA256', 'websiteBefore', 'websiteTarget', 'websiteFiles',
                    'hostingBefore', 'hostingAfter', 'hostingDependencies'}
        if set(self.plan) != required or self.plan['version'] != 'codi-site-cutover-plan/1':
            raise ValueError('Unknown cutover plan')
        p = self.plan
        if {p['beforeBasePath'], p['targetBasePath']} != {'', '/hidden'} or type(p['seconds']) is not int or not 60 <= p['seconds'] <= 86400 or type(p['noticeSeconds']) is not int or not 0 <= p['noticeSeconds'] <= 900:
            raise ValueError('Exact inverse root/hidden mounts and bounded durations required')
        for name in ['beforeConfigSHA256', 'nativeSHA256', 'oldNativeSHA256', 'mountOperatorSHA256', 'rolloutSHA256']:
            if not re.fullmatch('[0-9a-f]{64}', p[name]):
                raise ValueError('Exact digest required')
        if not re.fullmatch('[0-9a-f]{40}', p['sourceCommit']):
            raise ValueError('Exact source commit required')
        for name in ['nativeRelease', 'oldNativeRelease', 'mountOperator', 'rolloutTool', 'websiteBefore']:
            if not re.fullmatch('/[A-Za-z0-9_./-]+', p[name]) or '..' in Path(p[name]).parts:
                raise ValueError('Simple absolute paths required')
        if p['websiteTarget'] is not None and not re.fullmatch('[A-Za-z0-9-]+', p['websiteTarget']):
            raise ValueError('Managed release ID required')
        expected = {'common.py', 'sites.toml', 'production-smoke.py', 'Caddyfile.prepare', 'Caddyfile.production'}
        for which in ['hostingBefore', 'hostingAfter']:
            if set(p[which]) != expected or any(not isinstance(b, str) or len(b.encode()) > 262144 for b in p[which].values()):
                raise ValueError('Exact bounded public hosting preimages required')
        if set(p['hostingDependencies']) != {'webctl.py', 'scaffold.py', 'hardware_hosting.py', 'cardboard_hosting.py'}:
            raise ValueError('Bind the existing hosting dependencies')
        for n, pin in p['hostingDependencies'].items():
            if sha(read(self.root/'ops'/n)) != pin:
                raise ValueError('Hosting dependency changed: '+n)
        # Generators import their verified hardware/cardboard helpers while
        # rendering. A fresh CLI has only sealed native/operator paths so far.
        sys.path.insert(0, str(self.root/'ops'))
        for n in ['common.py', 'production-smoke.py']:
            if read(self.root/'ops'/n).decode() not in [p['hostingBefore'][n], p['hostingAfter'][n]]:
                raise ValueError('Unmanaged hosting source changes: '+n)
        if read(self.root/'sites.toml').decode() not in [p['hostingBefore']['sites.toml'], p['hostingAfter']['sites.toml']]:
            raise ValueError('Unmanaged manifest changes')
        left, before = self.hosting('hostingBefore')
        right, after = self.hosting('hostingAfter')
        expected_data = copy.deepcopy(before)
        site = next(s for s in expected_data['sites'] if s['domain'] == 'ksu.codes')
        if p['targetBasePath'] == '':
            site['codi_mount'] = ''
        else:
            site.pop('codi_mount', None)
        if after != expected_data or any(left.unit(s) != right.unit(s) for s in before['sites']):
            raise ValueError('Cutover changed unrelated sites or website units')
        git = ['git', '-C', str(self.source)]
        # Source is owned by the existing hosting operator, not imported into a
        # native runtime. Read it as its owner for Git's ownership protection.
        import pwd
        owner = pwd.getpwuid(self.root.stat().st_uid).pw_name
        prefix = ['runuser', '-u', owner, '--']
        if command(prefix+git+['rev-parse', 'HEAD']) != p['sourceCommit'] or command(prefix+git+['status', '--porcelain']):
            raise ValueError('Clean exact Git source required')
        spec = importlib.util.spec_from_file_location('codi_site_webctl', self.root/'ops/webctl.py')
        ctl = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = ctl
        spec.loader.exec_module(ctl)
        self.ctl = ctl
        if ctl.ROOT != self.root:
            raise ValueError('Hosting controller root differs')
        self.site = next(s for s in before['sites'] if s['domain'] == 'ksu.codes')
        if Path(p['websiteBefore']).parent != ctl.BASE/'ksu.codes/releases':
            raise ValueError('Website baseline is outside its managed release directory')
        self.op.path(Path(p['websiteBefore']))
        if not isinstance(p['websiteFiles'], dict) or not 1 <= len(p['websiteFiles']) <= 4096:
            raise ValueError('Bounded website publish contract required')
        for n, r in p['websiteFiles'].items():
            if Path(n).is_absolute() or '..' in Path(n).parts or n.split('/')[0] not in ('app', 'public') or set(r) != {'bytes', 'sha256'} or type(r['bytes']) is not int or not 0 <= r['bytes'] <= 134217728 or not re.fullmatch('[0-9a-f]{64}', r['sha256']):
                raise ValueError('Invalid website file contract')
        if p['websiteTarget'] is None and records(self.source) != p['websiteFiles']:
            raise ValueError('Publish source differs from the reviewed website')
        if p['websiteTarget'] is not None:
            self.check_release(ctl.BASE/'ksu.codes/releases'/p['websiteTarget'])
        # Both code generations must preserve native/security implementation.
        old = Path(p['oldNativeRelease'])
        new = Path(p['nativeRelease'])
        for folder, pin in [(old, p['oldNativeSHA256']), (new, p['nativeSHA256'])]:
            self.op.path(folder)
            if self.op.verify(folder)['manifestSHA256'] != pin:
                raise ValueError('Native release differs')
        old_manifest = json.loads(read(old/'connected-release.json'))
        new_manifest = json.loads(read(new/'connected-release.json'))
        public = set(json.loads(read(old/'release.json'))['files'])
        for n in set(old_manifest['files'])-public-{'release.json'}:
            if new_manifest['files'].get(n) != old_manifest['files'][n]:
                raise ValueError('Root cutover cannot also change backend/security code')
        self.op.path(Path(p['rolloutTool']))
        if sha(read(p['rolloutTool'])) != p['rolloutSHA256']:
            raise ValueError('Pinned rollout controller differs')
        operator = Path(p['mountOperator'])
        self.op.path(operator)
        raw = read(operator/'mount-operator.json')
        if sha(raw) != p['mountOperatorSHA256']:
            raise ValueError('Mount operator differs')
        meta = json.loads(raw)
        for n, r in meta['files'].items():
            b = read(operator/n)
            self.op.path(operator/n)
            if r != {'bytes': len(b), 'sha256': sha(b)}:
                raise ValueError('Installed mount code differs')
        import mount_operator.coordinator as mount
        if Path(mount.__file__).resolve() != operator/'mount_operator/coordinator.py':
            raise ValueError('Different mount module imported')

    def current_config(self):
        return json.loads(self.op.read_owned(self.config_path, 0, 0o600))

    def current_website(self):
        path = self.ctl.BASE/'ksu.codes/current'
        if not path.is_symlink():
            raise ValueError('Expected managed website pointer')
        target = path.resolve(strict=True)
        if target.parent != self.ctl.BASE/'ksu.codes/releases':
            raise ValueError('Website pointer escaped its release directory')
        self.op.path(target)
        return target

    def check_release(self, target):
        self.op.path(target)
        if records(target) != self.plan['websiteFiles']:
            raise ValueError('Published website code differs from the plan')
        return target

    def preflight(self):
        raw = self.op.read_owned(self.config_path, 0, 0o600)
        if sha(raw) != self.plan['beforeConfigSHA256'] or json.loads(raw)['basePath'] != self.plan['beforeBasePath']:
            raise ValueError('Native preflight changed')
        for n in ['maintenance.json', 'native-rollout.json', 'guest-signin-migration.json']:
            if (self.config_path.parent/n).exists():
                raise ValueError('Existing native operation requires its own recovery')
        if self.current_website() != Path(self.plan['websiteBefore']):
            raise ValueError('Website baseline changed')
        for n in ['common.py', 'production-smoke.py']:
            if read(self.root/'ops'/n).decode() != self.plan['hostingBefore'][n]:
                raise ValueError('Hosting source baseline changed')
        if read(self.root/'sites.toml').decode() != self.plan['hostingBefore']['sites.toml'] or read(self.caddy_file).decode() != self.plan['hostingBefore']['Caddyfile.production']:
            raise ValueError('Manifest/live Caddy baseline changed')
        self.op.load(self.config_path)

    def notice(self, identifier, created):
        now = int(time.time())
        deadline = created+self.plan['noticeSeconds']
        message = ('Desktop maintenance: save server files or download temporary files now. '
                   'Unsaved browser memory is not automatically saved. After maintenance, open '
                   +self.current_config()['origin']+self.target_base+'/ to continue.')
        value = {'version': 'codi-maintenance-notice/1', 'id': identifier,
                 'phase': 'scheduled' if now < deadline else 'active', 'deadline': deadline,
                 'expiresAt': deadline+86400, 'message': message}
        if now >= value['expiresAt']:
            # Explicit recovery may happen much later; refresh an active notice
            # without starting another countdown or changing signing policy.
            value.update(phase='active', deadline=now, expiresAt=now+86400)
        self.op.atomic(Path(self.current_config()['stateRoot'])/'public/desktop-maintenance.json', encoded(value), 0o644)
        while time.time() < deadline:
            time.sleep(min(.25, max(0, deadline-time.time())))

    def ensure_code(self):
        c = self.current_config()
        p = self.plan
        if c['basePath'] != p['beforeBasePath'] or (c['release'], c['manifestSHA256']) not in [(p['oldNativeRelease'], p['oldNativeSHA256']), (p['nativeRelease'], p['nativeSHA256'])]:
            raise ValueError('Unrelated native code/mount change')
        args = [c['python'], '-I', '-B', p['rolloutTool']]
        common = ['--operator', str(Path(p['nativeRelease'])/'scripts/manage-services.py'),
                  '--operator-manifest-sha256', p['nativeSHA256'], '--config', str(self.config_path)]
        if (self.config_path.parent/'native-rollout.json').exists():
            inner = json.loads(self.op.read_owned(self.config_path.parent/'native-rollout.json', 0, 0o600, 4194304))
            if inner['after']['release'] != p['nativeRelease'] or inner['after']['basePath'] != p['beforeBasePath']:
                raise ValueError('Unrelated code rollout is pending')
            command(args+['recover']+common)
            c = self.current_config()
        if c['manifestSHA256'] == p['nativeSHA256']:
            self.op.load(self.config_path)
            return
        backup = self.config_path.parent/'cutover-checkpoints'
        self.op.directory(backup, 0o700)
        result = json.loads(command(args+['upgrade']+common+['--release', p['nativeRelease'], '--python', c['python'], '--backup-parent', str(backup)], 300))
        if result['status'] not in ('upgraded', 'already-current') or self.current_config()['manifestSHA256'] != p['nativeSHA256']:
            raise ValueError('Code rollout did not reach its target; preserve the parent journal')

    def ensure_website(self, saved):
        current = self.current_website()
        before = Path(self.plan['websiteBefore'])
        target = self.plan['websiteTarget']
        if target is not None:
            destination = self.check_release(self.ctl.BASE/'ksu.codes/releases'/target)
            if current not in (before, destination):
                raise ValueError('Unrelated website deployment')
            if current != destination:
                self.ctl.point(self.site, target)
            self.ctl.install_unit(self.site)
            self.ctl.run(['systemctl', 'restart', self.site['service']])
            self.ctl.healthy(self.site)
            self.ctl.record_release(self.site, target, before.name)
            return {'current': target, 'previous': before.name}
        if current == before:
            # Call the normal managed deployment while retaining its outer lock.
            # Pipe package/deployer logs to stderr, keeping CLI stdout JSON-only.
            original = os.dup(1)
            try:
                os.dup2(2, 1)
                self.ctl.deploy(self.site)
            finally:
                os.dup2(original, 1)
                os.close(original)
            current = self.current_website()
        self.check_release(current)
        # Adopt only exact root-owned published bytes after death between the
        # managed pointer switch and its state/parent receipt. No data is copied.
        self.ctl.install_unit(self.site)
        self.ctl.run(['systemctl', 'restart', self.site['service']])
        self.ctl.healthy(self.site)
        self.ctl.record_release(self.site, current.name, before.name)
        return {'current': current.name, 'previous': before.name}

    def check_website(self, saved):
        if not isinstance(saved, dict) or set(saved) != {'current', 'previous'} or saved['previous'] != Path(self.plan['websiteBefore']).name:
            raise ValueError('Invalid parent website receipt')
        if self.current_website().name != saved['current']:
            raise ValueError('Website changed after the cutover step')
        self.check_release(self.current_website())

    def before_mount(self):
        c = self.op.load(self.config_path)
        if c['basePath'] != self.plan['beforeBasePath'] or c['release'] != self.plan['nativeRelease'] or c['manifestSHA256'] != self.plan['nativeSHA256']:
            raise ValueError('Unexpected native code/mount before signing')

    def check_mount_journal(self, inner, before):
        if inner.get('version') != 'codi-mount-transition/1' or before is None or inner.get('before') != before or inner['after']['basePath'] != self.target_base or inner['before']['basePath'] != self.plan['beforeBasePath'] or inner['before']['release'] != self.plan['nativeRelease'] or inner['after']['release'] != self.plan['nativeRelease']:
            raise ValueError('Unrelated native mount journal; retain both operations')

    def backup_hosting(self):
        return {str(p): str(self.ctl.snapshot(p)) for p in [self.root/'ops/common.py', self.root/'ops/production-smoke.py', self.root/'sites.toml', self.caddy_file]}

    def ensure_hosting(self, event):
        target = self.plan['hostingAfter']
        for name, file in [('common.py', self.root/'ops/common.py'), ('production-smoke.py', self.root/'ops/production-smoke.py'), ('sites.toml', self.root/'sites.toml')]:
            raw = read(file).decode()
            if raw not in [self.plan['hostingBefore'][name], target[name]]:
                raise ValueError('Hosting file changed outside the transaction')
            info = file.stat()
            self.ctl.write(file, target[name], stat.S_IMODE(info.st_mode), info.st_uid, info.st_gid, False)
            event('hosting-'+name)
        module, data = self.hosting('hostingAfter')
        for n in ['load', 'dump', 'validate', 'unit', 'caddy']:
            setattr(self.ctl, n, getattr(module, n))
        self.apply_caddy(data)
        event('hosting-applied')

    def apply_caddy(self, data):
        self.ctl.caddy_apply(data, 'production')

    def fetch(self, path, method='GET'):
        conn = http.client.HTTPSConnection('ksu.codes', timeout=15)
        conn.sock = ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1', 443), 15), server_hostname='ksu.codes')
        try:
            conn.request(method, path)
            r = conn.getresponse()
            body = r.read(134217729)
            if len(body) > 134217728:
                raise ValueError('Bounded public response required')
            return r.status, {k.lower(): v for k, v in r.getheaders()}, body
        finally:
            conn.close()

    def all_sites(self):
        report = self.root/'reports/private/root-cutover-smoke.json'
        command(['/usr/bin/python3', '-B', self.root/'ops/production-smoke.py', '--address', '127.0.0.1', '--scope', 'server-loopback-root-cutover', '--output', report], 180)
        result = json.loads(read(report))
        if any(s['result'] != 'PASS' for s in result['sites'].values()):
            raise ValueError('Managed all-site smoke failed')
        return {'report': str(report), 'domains': sorted(result['sites']), 'ordinaryTLS': True}

    def verify(self):
        c = self.op.load(self.config_path)
        if c['basePath'] != self.target_base or c['manifestSHA256'] != self.plan['nativeSHA256']:
            raise ValueError('Native target differs')
        self.op.ready(c, self.op.ROLES)
        if read(self.caddy_file).decode() != self.plan['hostingAfter']['Caddyfile.production']:
            raise ValueError('Live Caddy differs from generated target')
        self.check_release(self.current_website())
        prefix = self.target_base
        status, headers, body = self.fetch(prefix+'/config.json')
        config = json.loads(body)
        if status != 200 or config['identity']['apiBase'] != prefix+'/api/v1' or config['identity']['issuer'] != c['origin']:
            raise ValueError('Public issuer mount differs')
        status, headers, body = self.fetch(prefix+'/')
        if status != 200 or sha(body) != sha(read(Path(c['release'])/'index.html')):
            raise ValueError('Desktop entry differs')
        blog_path = '/blog/' if prefix == '' else '/'
        status, _, body = self.fetch(blog_path)
        if status != 200 or sha(body) != self.plan['websiteFiles']['public/index.html']['sha256']:
            raise ValueError('Blog/homepage differs')
        prototype = json.loads(read(self.current_website()/'public/desktop/release.json'))['files']
        if len(prototype) != 133:
            raise ValueError('Prototype manifest changed')
        for n, r in prototype.items():
            status, _, body = self.fetch('/desktop/'+n)
            if status != 200 or r != {'bytes': len(body), 'sha256': sha(body)}:
                raise ValueError('Prototype bytes changed: '+n)
        from origin_service import maintenance
        binding = maintenance.binding(Path(c['stateRoot']))
        fence = json.loads(self.op.read_owned(self.config_path.parent/'recovery-fence.json', 0, 0o600))
        if fence['rootFloor'] != binding['rootRevision']:
            raise ValueError('Authority/fence differs')
        return {'prototypeFilesVerified': len(prototype), 'rootRevision': binding['rootRevision'],
                'publisherRevision': binding['publisherRevision'], 'allSites': self.all_sites(),
                'nativeManifestSHA256': c['manifestSHA256'], 'basePath': prefix,
                'publicIndexSHA256': sha(read(Path(c['release'])/'index.html'))}

    def finish(self, result):
        self.op.atomic(self.config_path.parent/'site-cutover-last.json', encoded(result))
        self.op.atomic(self.config_path.parent/('site-cutover-'+result['id']+'-result.json'), encoded(result))
        now = int(time.time())
        notice = {'version': 'codi-maintenance-notice/1', 'id': result['id'], 'phase': 'cancelled',
                  'deadline': now, 'expiresAt': now+3600, 'message': 'Maintenance complete. Reload the desktop to use its current address. Unsaved browser memory is not restored.'}
        self.op.atomic(Path(self.current_config()['stateRoot'])/'public/desktop-maintenance.json', encoded(notice), 0o644)
