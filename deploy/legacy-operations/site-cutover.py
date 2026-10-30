#!/usr/bin/env python3
"""Explicit apply/recover for a pinned immutable desktop/website cutover tool."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True


def protected(path):
    for p in [path, *path.parents]:
        info = p.lstat()
        if p.is_symlink() or info.st_uid or info.st_mode & 0o022:
            raise ValueError('Protected root-owned operator/plan path required')


def raw(path, limit=16777216):
    protected(path)
    with os.fdopen(os.open(path, os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK), 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('Bounded regular single-link input required')
        value = stream.read(info.st_size+1)
        if len(value) != info.st_size:
            raise ValueError('Input changed during read')
        return value


def seal(folder, filename, pin, expected_version):
    for path in [folder, *folder.rglob('*')]:
        protected(path)
    value = raw(folder/filename)
    if hashlib.sha256(value).hexdigest() != pin:
        raise ValueError('Operator manifest digest differs')
    metadata = json.loads(value)
    if set(metadata) != {'version', 'files'} or metadata['version'] != expected_version:
        raise ValueError('Unknown operator manifest')
    if {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()} != set(metadata['files'])|{filename}:
        raise ValueError('Incomplete/unlisted operator files')
    for n, record in metadata['files'].items():
        if Path(n).is_absolute() or '..' in Path(n).parts:
            raise ValueError('Relative operator paths required')
        value = raw(folder/n)
        if record != {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()}:
            raise ValueError('Operator file differs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'apply', 'recover'])
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--plan-sha256', required=True)
    parser.add_argument('--operator-sha256', required=True)
    args = parser.parse_args()
    if os.geteuid() or not all(re.fullmatch('[0-9a-f]{64}', n) for n in [args.plan_sha256, args.operator_sha256]):
        parser.error('Root and exact operator/plan SHA256 pins required')
    root = Path(__file__).absolute().parent.parent
    seal(root, 'site-cutover-operator.json', args.operator_sha256, 'codi-site-cutover-operator/1')
    plan_raw = raw(args.plan)
    if stat.S_IMODE(args.plan.stat().st_mode) != 0o600:
        parser.error('Keep the on-server plan private with mode0600')
    if hashlib.sha256(plan_raw).hexdigest() != args.plan_sha256:
        parser.error('Plan differs from its reviewed pin')
    plan = json.loads(plan_raw)
    operator = Path(plan['mountOperator'])
    seal(operator, 'mount-operator.json', plan['mountOperatorSHA256'], 'codi-mount-operator/1')
    if Path(plan['rolloutTool']) != root/'scripts/native-rollout.py':
        parser.error('Use this sealed bundle’s rollout controller')
    sys.path[:0] = [str(root), str(operator), plan['nativeRelease']]
    from mount_operator.backends import seal as seal_native
    seal_native(Path(plan['nativeRelease']), 'connected-release.json', plan['nativeSHA256'], 134217728)
    from mount_operator.coordinator import load_operator
    from site_cutover.coordinator import run
    from site_cutover.managed import Managed
    op = load_operator(Path(plan['nativeRelease']), plan['nativeSHA256'])
    driver = Managed(plan, op)
    with driver.locked():
        # Managed Caddy/systemd commands may write directly to fd1. Keep all
        # operator logs on stderr so stdout remains one parseable receipt.
        sys.stdout.flush()
        original_stdout = os.dup(1)
        try:
            os.dup2(2, 1)
            result = run(driver, args.action)
        finally:
            sys.stdout.flush()
            os.dup2(original_stdout, 1)
            os.close(original_stdout)
    print(json.dumps(result, indent=2))
