#!/usr/bin/env python3
"""Reuse exact f2/dd8 fixture with sealed adc issuer and short test-only TTL."""
from pathlib import Path
root=Path(__file__).resolve().parents[1];source=(root/'tests/main-opfs-signed-fixture.py').read_text()
old="'8149949e9b4d7ef878ae1e0a208943b1b32e4883e2698f4b1a433c49a4aa3055'";new="'adc693e4bfe418f950eedd5be0f70ecc7b82c6268e14ebed6eeba64e95740414'"
if source.count(old)!=1:raise ValueError('issuer pin anchor changed')
source=source.replace(old,new,1)
old="str(issuer/'scripts/serve-connected.py')";new="str(root/'tests/files-session-short-issuer.py')"
if source.count(old)!=1:raise ValueError('issuer launcher anchor changed')
source=source.replace(old,new,1)
exec(compile(source,str(root/'tests/main-opfs-signed-fixture.py'),'exec'),globals())
