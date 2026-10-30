"""Stopped-service mount edits through pinned backend operators.

Each helper runs in its own interpreter so the sealed guest package never shares
the native guest_service namespace. A line protocol holds the existing backend
operator locks from planning through edits/start. EOF releases locks, never
restores state. The outer native journal owns recovery across helper deaths.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import stat
import sys

VERSION = 'codi-mount-backend-plan/1'
MAXIMUM = 1048576


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def protected(path, mode=None):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Absolute protected path required')
    for p in [path, *path.parents]:
        info = p.lstat()
        if p.is_symlink() or info.st_uid or info.st_mode & 0o022:
            raise ValueError('Backend inputs must remain protected root files')
    info = path.stat()
    if mode is not None and (not stat.S_ISREG(info.st_mode) or
                             stat.S_IMODE(info.st_mode) != mode or info.st_nlink != 1):
        raise ValueError('Unexpected backend input permissions/type')
    return path


def read(path, mode, maximum=MAXIMUM):
    path = protected(path, mode)
    if path.stat().st_size > maximum:
        raise ValueError('Backend input exceeds bound')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), 'rb') as f:
        raw = f.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError('Backend input exceeds bound')
    return raw


def seal(folder, manifest, pin, maximum=MAXIMUM):
    folder = protected(folder)
    if not re.fullmatch('[0-9a-f]{64}', pin):
        raise ValueError('Exact operator digest required')
    raw = read(folder / manifest, 0o644)
    if sha(raw) != pin:
        raise ValueError('Backend operator pin differs')
    metadata = json.loads(raw)
    files = metadata['files']
    if {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()} != set(files) | {manifest}:
        raise ValueError('Unexpected backend operator files')
    for name, record in files.items():
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('Invalid operator member path')
        data = read(folder / name, 0o644, maximum)
        if record != {'bytes': len(data), 'sha256': sha(data)}:
            raise ValueError('Backend operator bytes changed')


def context_pair(before, base, policy):
    if not isinstance(base, str) or (base and not re.fullmatch(r'/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*', base)):
        raise ValueError('Explicit mount prefix required')
    old = before['issuerPolicy']
    if not isinstance(policy, dict) or policy.get('apiBase') != base + '/api/v1' or old.get('apiBase') != before['basePath'] + '/api/v1':
        raise ValueError('Issuer API context differs')
    if {k: v for k, v in old.items() if k != 'apiBase'} != {k: v for k, v in policy.items() if k != 'apiBase'}:
        raise ValueError('Mount edits cannot replace issuer trust')


class Backend:
    def __init__(self, kind, folder, operator, pin, config_pin):
        self.kind, self.folder = kind, protected(folder)
        if not re.fullmatch('[0-9a-f]{64}', config_pin):
            raise ValueError('Exact original backend configuration pin required')
        self.config_pin = config_pin
        manifest = 'file-operator.json' if kind == 'files' else 'guest-operator.json'
        seal(Path(operator), manifest, pin)
        sys.path.insert(0, str(operator))
        self.module = importlib.import_module('file_service.operator' if kind == 'files' else 'guest_service.operator')
        self.manager = self.module.Manager(folder) if kind == 'files' else self.module.Manager(folder, operator)

    def current(self):
        return self.manager.load()

    def derive(self, before, policy_before, base, policy):
        """Derive an exact write allowlist; no caller-selected output paths."""
        context_pair({**before, 'issuerPolicy': policy_before}, base, policy)
        after = deepcopy(before)
        after['basePath'] = base
        files = {}

        def output(path, old, new, mode=0o644):
            if not isinstance(old, bytes) or not isinstance(new, bytes):
                raise ValueError('Exact metadata bytes required')
            files[str(path)] = {'before': old.decode(), 'after': new.decode(), 'mode': mode}

        if self.kind == 'files':
            after['issuerPolicySHA256'] = sha(encoded(policy))
            output(self.folder / 'issuer-policy.json', encoded(policy_before), encoded(policy))
            before_units, after_units = self.manager.units(before), self.manager.units(after)
        else:
            after['issuerPolicy'] = deepcopy(policy)
            self.manager.validate_plan(before)
            self.manager.validate_plan(after)
            if self.manager.rules(before) != self.manager.rules(after):
                raise ValueError('Mount edit cannot change owned guest kernel policy')
            for role in ['anonymous', 'registered']:
                output(self.folder / (role + '.json'), encoded(self.manager.worker_settings(before, role)),
                       encoded(self.manager.worker_settings(after, role)))
            before_units, after_units = self.manager.rendered(before), self.manager.rendered(after)
        if set(before_units) != set(after_units):
            raise ValueError('Mount edit cannot change backend unit names')
        for name in before_units:
            output(Path(before['unitDir']) / name, before_units[name], after_units[name])
        output(self.folder / 'managed.json', encoded(before), encoded(after), 0o600)
        return {'version': VERSION, 'kind': self.kind, 'before': before, 'after': after,
                'policyBefore': policy_before, 'policyAfter': policy, 'files': files}

    def prepare(self, base, policy):
        if sha(read(self.folder / 'managed.json', 0o600)) != self.config_pin:
            raise ValueError('Backend configuration differs from native pin')
        before = self.current()
        old_policy = json.loads(self.manager.policy(before)) if self.kind == 'files' else before['issuerPolicy']
        plan = self.derive(before, old_policy, base, policy)
        # Installed versions may use a different harmless JSON encoding. Pin its
        # exact preimage; generated settings/units still must match the operator.
        for path, record in plan['files'].items():
            raw = read(path, record['mode'])
            if path == str(self.folder / 'managed.json') or path == str(self.folder / 'issuer-policy.json'):
                if json.loads(raw) != json.loads(record['before']):
                    raise ValueError('Backend metadata differs from prepared context')
                record['before'] = raw.decode()
            elif raw.decode() != record['before']:
                raise ValueError('Backend derived preimage differs')
        return plan

    def validate(self, plan):
        if plan.get('version') != VERSION or plan.get('kind') != self.kind:
            raise ValueError('Wrong backend plan')
        expected = self.derive(plan['before'], plan['policyBefore'], plan['after']['basePath'], plan['policyAfter'])
        # Only encoding of the two captured JSON preimages may differ.
        for path in [self.folder / 'managed.json', self.folder / 'issuer-policy.json']:
            path = str(path)
            if path in expected['files']:
                if json.loads(expected['files'][path]['before']) != json.loads(plan['files'][path]['before']):
                    raise ValueError('Unexpected backend preimage')
                expected['files'][path]['before'] = plan['files'][path]['before']
        if expected != plan:
            raise ValueError('Mount plan changes an unrelated backend field or output')
        if sha(plan['files'][str(self.folder / 'managed.json')]['before'].encode()) != self.config_pin:
            raise ValueError('Backend preimage differs from original native configuration pin')
        if self.kind == 'files':
            if sha(plan['files'][str(self.folder / 'issuer-policy.json')]['before'].encode()) != plan['before']['issuerPolicySHA256']:
                raise ValueError('Original file policy pin differs')
        elif plan['before']['issuerPolicy'] != plan['policyBefore']:
            raise ValueError('Original guest identity policy differs')
        return expected

    def apply(self, plan):
        self.validate(plan)
        if self.kind == 'files':
            self.manager.inactive(plan['before'])
        else:
            self.manager.frontend_down(plan['before'])
            self.manager.all_down(plan['before'])
            if any(p.exists() for p in [self.manager.active, self.manager.pending, self.manager.fault]) or self.module.table(plan['before']) is not None:
                raise ValueError('Stop/recover guest protection before mount edits')
        # Inspect every preimage before the first edit. Interruption recovery
        # accepts only journaled old/new bytes, never arbitrary mixed settings.
        for path, record in plan['files'].items():
            if read(path, record['mode']).decode() not in [record['before'], record['after']]:
                raise ValueError('Backend output changed outside this mount transition')
        for path, record in plan['files'].items():
            if read(path, record['mode']).decode() != record['after']:
                self.module.atomic(path, record['after'].encode(), record['mode'])
        self.module.systemctl('daemon-reload')
        if self.current() != plan['after']:
            raise ValueError('Applied backend differs from prepared mount')
        return {'status': 'applied', 'kind': self.kind, 'configSHA256': sha(encoded(plan['after']))}

    def dispatch(self, request):
        action = request.get('action')
        if action == 'prepare':
            return self.prepare(request['basePath'], request['issuerPolicy'])
        if action == 'validate':
            self.validate(request['plan'])
            return {'status': 'validated'}
        if action == 'stop':
            plan = request.get('plan')
            if plan is not None:
                self.validate(plan)
                for path, record in plan['files'].items():
                    if read(path, record['mode']).decode() not in [record['before'], record['after']]:
                        raise ValueError('Backend metadata changed outside the journal')
                if self.kind == 'files':
                    self.module.systemctl('stop', *reversed(self.manager.names(plan['before'])))
                    self.manager.inactive(plan['before'])
                    return {'status': 'stopped', 'privateDataPreserved': True}
                self.manager.frontend_down(plan['before'])
                if not any(p.exists() for p in [self.manager.active, self.manager.pending, self.manager.fault]) and self.module.table(plan['before']) is None:
                    self.manager.all_down(plan['before'])
                    return {'status': 'already-stopped', 'usageAndCredentialsPreserved': True}
            if self.kind == 'guest':
                self.manager.recover()
            return self.manager.stop()
        if action == 'apply':
            return self.apply(request['plan'])
        if action == 'start':
            return self.manager.start()
        raise ValueError('Explicit backend action required')


def serve(args):
    if os.geteuid() != 0:
        raise ValueError('Root mount coordinator required')
    backend = Backend(args.kind, args.config_dir, args.operator, args.operator_sha256, args.config_sha256)
    with backend.manager.locked():
        while True:
            line = sys.stdin.readline(MAXIMUM + 1)
            if not line:
                break
            if len(line.encode()) > MAXIMUM:
                raise ValueError('Bounded backend request required')
            try:
                result = {'ok': True, 'value': backend.dispatch(json.loads(line))}
            except Exception as error:
                result = {'ok': False, 'error': type(error).__name__ + ': ' + str(error)}
            raw = json.dumps(result, separators=(',', ':'))
            if len(raw.encode()) > MAXIMUM:
                raise ValueError('Bounded backend response required')
            print(raw, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=['files', 'guest'], required=True)
    parser.add_argument('--config-dir', type=Path, required=True)
    parser.add_argument('--operator', type=Path, required=True)
    parser.add_argument('--operator-sha256', required=True)
    parser.add_argument('--config-sha256', required=True)
    serve(parser.parse_args())
