#!/usr/bin/env python3
"""Operate the native isolated TURN relay; public ingress is managed separately."""
import argparse
import json
import pwd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from relay_service.manager import Manager
from relay_service import certificates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['configure', 'start', 'stop', 'status', 'recover', 'bind-certificate-source', 'refresh-certificate', 'refresh-units', 'bandwidth-profile'])
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--instance')
    parser.add_argument('--hostname')
    parser.add_argument('--binary', type=Path, default=Path('/usr/bin/turnserver'))
    parser.add_argument('--certificate', type=Path)
    parser.add_argument('--private-key', type=Path)
    parser.add_argument('--port', type=int, default=13479)
    parser.add_argument('--unit-dir', default='/etc/systemd/system', choices=['/etc/systemd/system', '/run/systemd/system'])
    parser.add_argument('--source-directory', type=Path)
    parser.add_argument('--source-user', default='caddy')
    parser.add_argument('--python', type=Path)
    parser.add_argument('--bandwidth-profile', choices=['legacy', 'text-32k/1', 'text-128/1', 'text-256/1'])
    args = parser.parse_args()
    try:
        with Manager(args.directory).locked() as manager:
            if args.action == 'configure':
                if not all([args.instance, args.hostname, args.certificate, args.private_key]):
                    parser.error('Configure requires instance, hostname, certificate and private-key')
                # Source files may be owned by Caddy; bounded parsing and key/leaf
                # matching precede root-only immutable custody. Never print them.
                def bounded(p):
                    with p.open('rb') as stream:
                        raw = stream.read(262145)
                    if len(raw) > 262144:
                        raise ValueError('TLS input exceeded bound')
                    return raw
                result = manager.configure(instance=args.instance, hostname=args.hostname, binary=args.binary, cert=bounded(args.certificate), key=bounded(args.private_key), port=args.port, unit_dir=args.unit_dir)
            elif args.action == 'bandwidth-profile':
                if args.bandwidth_profile is None:
                    parser.error('Bandwidth profile change requires --bandwidth-profile')
                result = manager.bandwidth_profile(args.bandwidth_profile)
            elif args.action == 'bind-certificate-source':
                if args.source_directory is None:
                    parser.error('Certificate source binding requires --source-directory')
                result = certificates.bind(manager, args.source_directory, pwd.getpwnam(args.source_user).pw_uid)
            elif args.action == 'refresh-certificate':
                result = certificates.refresh(manager)
            elif args.action == 'refresh-units':
                if args.python is None:
                    parser.error('Refresh unit generation requires protected --python')
                result = certificates.refresh_units(manager, ROOT, args.python)
            else:
                result = getattr(manager, args.action)()
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, BlockingIOError) as error:
        parser.exit(1, 'Relay operation refused: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
