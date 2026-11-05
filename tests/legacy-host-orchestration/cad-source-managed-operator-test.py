#!/usr/bin/env python3
"""Focused operator schema/render controls; no services or production files."""
import importlib.util,pathlib,types
import os
p=pathlib.Path(os.environ.get('CODI_SOURCE_OPERATOR','/tmp/codi-cad-source-managed-operator-v6'))/'file_service/operator.py'
s=importlib.util.spec_from_file_location('operator_candidate',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
gw='a626ef11bf57a039529abc806a4b39a5881f470557d49f8c715a742c06b5ae08';pin='e304a1c451a380d21caebb306e47803a4b5de8a098d31cdaa3d60241367551a6'
c={'version':'codi-files-managed/1','instance':'codi-files-ksu','user':'codi-gateway','uid':42,'gid':42,'release':'/srv/fixture/gateway','manifestSHA256':gw,'python':'/srv/fixture/venv/bin/python','unitDir':'/etc/systemd/system','stateRoot':'/srv/fixture/state','dataRoot':'/srv/fixture/data','origin':'https://example.test','basePath':'','port':8140,'issuerPolicySHA256':'a'*64,'socketProxy':'/usr/lib/systemd/systemd-socket-proxyd','socketProxySHA256':'b'*64,'cadSourceRoot':'/srv/codi-connected/cad-sources/'+pin,'cadSourceManifestSHA256':pin}
manager=m.Manager('/srv/fixture/config');manager.policy=lambda c:None
m.account=lambda user:types.SimpleNamespace(pw_uid=42,pw_gid=42)
m.protected=lambda p,**kw:pathlib.Path(p)
m.verify_worker=lambda *args:None;m.verify_python=lambda *args:None
m.verify_cad_sources=lambda c:None
# Avoid reading the real systemd proxy while keeping the ordinary validation path.
class Proxy:
 def __str__(self):return '/usr/lib/systemd/systemd-socket-proxyd'
 def read_bytes(self):return b'proxy'
m.protected=lambda p,**kw:Proxy() if str(p)=='/usr/lib/systemd/systemd-socket-proxyd' else pathlib.Path(p)
m.digest=lambda b:'b'*64 if b==b'proxy' else __import__('hashlib').sha256(b).hexdigest()
manager.validate(c)
unit=manager.units(c)['codi-files-ksu.service'].decode()
assert '"--cad-source-root" "'+c['cadSourceRoot']+'"' in unit
assert '"--cad-source-manifest-sha256" "'+pin+'"' in unit
for change in ({'cadSourceManifestSHA256':None},{'manifestSHA256':'dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'},{'cadSourceRoot':None}):
 bad=dict(c)
 for k,v in change.items():
  if v is None:bad.pop(k)
  else:bad[k]=v
 try:manager.validate(bad)
 except ValueError:pass
 else:raise AssertionError('bad config accepted: '+str(change))
print('PASS paired config and rendered command; mocked host prerequisites')
