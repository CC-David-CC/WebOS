#!/usr/bin/env python3
"""Exact sealed inputs, byte snapshots and negative pins; no host changes."""
import importlib.util,json,sys,types
from pathlib import Path
root=Path(__file__).resolve().parents[1];ops=root/'ops';sys.path.insert(0,str(ops));import beta_files_snapshots as snapshots

def bound(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return types.SimpleNamespace(source=path.read_bytes(),module=module)
old=bound('old_snap_generator',ops/'common_live.py');new=bound('new_snap_generator',ops/'common.py');manifest=(ops/'sites_live.toml').read_bytes();candidate=Path('/tmp/codi-beta-opfs-transition-candidate/manifest.json').read_bytes();table=(root/'OPFS-ROUTE-TABLE.json').read_bytes()
def build(**kw):return snapshots.build(old=kw.get('old',old),new=kw.get('new',new),manifest=kw.get('manifest',manifest),candidate_manifest=kw.get('candidate',candidate),route_table=kw.get('table',table))
r=build();assert set(r)=={'initial','normalized','gate','candidate','initialData','normalizedData','gateData','candidateData'};assert r['initial']['manifest']==manifest and r['initial']['caddy']==r['normalized']['caddy'];assert r['gateData']['codi_beta_maintenance'] is True and r['candidateData']['codi_beta_maintenance'] is False and r['candidateData']['codi_beta_opfs']==snapshots.CANDIDATE
for kw in ({'manifest':manifest+b' '},{'candidate':candidate+b' '},{'table':table+b' '},{'old':types.SimpleNamespace(source=old.source+b' ',module=old.module)},{'new':types.SimpleNamespace(source=new.source+b' ',module=new.module)}):
 try:build(**kw);raise AssertionError('tampered pinned input accepted')
 except ValueError:pass
print('PASS exact baseline/normal/gate/v2 snapshots, 84 manifest-bound routes and rejected input drift')
