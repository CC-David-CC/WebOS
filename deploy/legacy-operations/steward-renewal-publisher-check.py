#!/usr/bin/env python3
"""Test publisher timer reconciliation in a disposable root-owned directory."""
import hashlib,importlib.util,json,os,sys,tempfile,types
from pathlib import Path
sys.dont_write_bytecode=True;ROOT=Path(__file__).resolve().parents[1];assert os.geteuid()==0
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/publish-steward-account-v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
new=(ROOT/'.build/codi-ksu-live-root-renew-new.service').read_bytes();old=p.render_renewal_unit(new,p.OLD);assert hashlib.sha256(old).hexdigest()==p.TIMER_PINS[p.OLD][1];assert p.render_renewal_unit(old,p.NEW)==new
checks=['old/new pinned unit conversion round trip'];events=[]
with tempfile.TemporaryDirectory(prefix='codi-renew-publisher-',dir='/run') as t:
 unit=Path(t)/'codi-ksu-live-root-renew.service';unit.write_bytes(old);unit.chmod(0o644);control=Path(t)/'managed.json';control.write_text('{}');p.TIMER_UNIT=unit
 c={'manifestSHA256':p.OLD};fake=types.SimpleNamespace(CONTROL=control,run=lambda args:(events.append(list(map(str,args))) or ('active' if 'is-active' in args else '')));real_sha=p.sha;p.sha=lambda path:p.TIMER_PINS[c['manifestSHA256']][0] if path==control else real_sha(path)
 assert not p.ensure_renewal(fake,c,False)['changed'];checks.append('matching pins accepted without writes')
 c['manifestSHA256']=p.NEW
 try:p.ensure_renewal(fake,c,False)
 except AssertionError:checks.append('stale pins refuse normal operation')
 else:raise AssertionError('stale pin accepted')
 assert p.ensure_renewal(fake,c,True)['changed'] and unit.read_bytes()==new;checks.append('upgrade or recovery repins new unit')
 c['manifestSHA256']=p.OLD;assert p.ensure_renewal(fake,c,True)['changed'] and unit.read_bytes()==old;checks.append('rollback or recovery repins old unit')
 unit.write_bytes(old+b'\n# unexpected\n')
 try:p.ensure_renewal(fake,c,True)
 except AssertionError:checks.append('unknown unit is refused')
 else:raise AssertionError('unknown unit accepted')
 assert sum('daemon-reload' in e for e in events)==2;checks.append('each actual repin reloads units once')
print(json.dumps({'status':'PASS','checks':checks,'scope':'Disposable root-owned real file operations with fake systemd; no live service, native transition, or power-loss proof.'},indent=2))
