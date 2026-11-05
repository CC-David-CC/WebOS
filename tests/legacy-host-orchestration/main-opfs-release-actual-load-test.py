#!/usr/bin/env python3
"""Actual native load/installed with real release verify; synthetic host boundaries."""
import importlib.util,json,os,pathlib,shutil,sys,tempfile
P=pathlib.Path;src=P(sys.argv[1]);broken=P(sys.argv[2]);assert os.geteuid()==0
with tempfile.TemporaryDirectory(prefix='codi-native-actual-load-',dir='/var/lib') as d:
 root=P(d);release=root/'release';shutil.copytree(src,release)
 for p in [release,*release.rglob('*')]:
  if p.is_symlink():raise ValueError('Unexpected candidate symlink')
  os.chmod(p,0o755 if p.is_dir() else 0o644)
 sys.path[:0]=[str(release),str(release/'codiserver-server-v0.3.0')];spec=importlib.util.spec_from_file_location('actual_candidate_native',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
 # The exercised load and installed/verify functions are real. Only unrelated
 # fixture-specific pip/account/guest-secret boundaries are substituted.
 op.accounts=lambda _:{};op.run=lambda args,**kw: (release/'requirements.lock').read_text() if 'freeze' in args else ''
 from origin_service import guest_cookie
 guest_cookie.validate_source=lambda *_:None
 env=root/'venv';(env/'bin').mkdir(parents=True);(env/'bin/python').symlink_to('/usr/bin/python3.12');units=root/'units';units.mkdir();state=root/'state';state.mkdir()
 config={'version':'codi-managed-instance/1','authorityClass':'development','instance':'codi-fixture','release':str(release),'python':str(env/'bin/python'),'stateRoot':str(state),'unitDir':str(units),'origin':'https://ksu.codes','basePath':'','ports':{'issuer':18118,'steward':18119,'guest':18132},'manifestSHA256':op.verify(release)['manifestSHA256']}
 configfile=root/'managed.json';configfile.write_text(json.dumps(config));os.chmod(configfile,0o600)
 for role in (*op.ROLES,'issuer-bootstrap'):
  f=units/op.unit(config,role);f.write_bytes(op.render(config,role));os.chmod(f,0o644)
 assert op.load(configfile)==config
 # The old defective candidate must fail actual release verification.
 try:op.verify(broken)
 except ValueError as e:assert 'explicit public/native file lists' in str(e)
 else:raise AssertionError('01080 missing-list control accepted')
 print('PASS actual native load/installed/closed release verify for adc; 01080 negative; pip/account/guest-secret fixture substituted')
