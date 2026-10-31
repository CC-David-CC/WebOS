#!/usr/bin/env python3
"""Add the release-matched Browser source archive to an existing allowlist."""
from pathlib import Path
import sys

OLD = '/codi-browser-source-0fc6bf9a7.tar.zst'
NEW = '/codi-browser-source-adece7482.tar.zst'


def derive(source):
    if source.count(OLD) != 1 or NEW in source:
        raise ValueError('Unexpected Browser source allowlist')
    return source.replace(OLD, OLD + ' ' + NEW, 1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: prepare-browser-source-update.py INPUT OUTPUT')
    Path(sys.argv[2]).write_text(derive(Path(sys.argv[1]).read_text()))
