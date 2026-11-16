#!/usr/bin/env python3
"""Disposable signed-account probe across exact native issuer restart."""
import base64,hashlib,http.client,json,os,secrets,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'));sys.path.insert(0,os.environ['CODI_GATEWAY_ROOT']+'/codiserver-server-v0.3.0');from codiauth import jose
from beta_signed_probe import Probe,ProbeError,ProbeUncertain,load_probe_config,provision_private
origin='http://127.0.0.1:19771';host='127.0.0.1:19771'
def config():
 c=http.client.HTTPConnection('127.0.0.1',19772,timeout=5);c.request('GET','/config.json',headers={'Host':host});r=c.getresponse();assert r.status==200;v=json.loads(r.read());c.close();return v
before=config();private=tempfile.TemporaryDirectory(prefix='codi-provision-');os.chmod(private.name,0o700);subject=provision_private(private.name,origin=origin,issuer_port=19772,gateway_port=19771,policy=before['identity'],jose=jose);original=load_probe_config(Path(private.name)/'probe.json');username=original['username'];password=original['password'];digest=original['sha256'];known=b'Codi beta Files health probe v1\n';assert not (Path(private.name)/'probe-provision.json').exists()
# Probe account/session and files survive the real issuer process replacement.
c=http.client.HTTPConnection('127.0.0.1',19774,timeout=30);c.request('GET','/restart');r=c.getresponse();assert r.status==200;r.read();c.close();after=config();assert before['identity']==after['identity'] and after['fileStorage']['backend']=='opfs'
with tempfile.TemporaryDirectory(prefix='codi-signed-probe-journal-') as temp:
 os.chmod(temp,0o700);config_path=Path(temp)/'probe.json';config_path.write_text(json.dumps({'username':username,'password':password,'subject':subject,'path':'codi-health-known.txt','sha256':digest}));config_path.chmod(0o600);saved=load_probe_config(config_path)
 config_path.chmod(0o644)
 try:load_probe_config(config_path);raise AssertionError('public credential accepted')
 except ValueError:pass
 config_path.chmod(0o600)
 probe=Probe(origin=origin,issuer_port=19772,gateway_port=19771,policy=after['identity'],jose=jose,username=saved['username'],password=saved['password'],expected_subject=saved['subject']);assert probe.enter()==subject;assert probe.read_known(saved['path'],saved['sha256'])['sha256']==digest
 result=probe.acceptance(temp);assert result=={'createdAndDeleted':True,'bytes':32};assert not (Path(temp)/'signed-probe-acceptance.json').exists()
 # Lose the accepted create reply: no blind retry or automatic delete. The
 # private journal gives the operator the exact account-local record.
 real=probe._post;attempts=[0]
 def drop_once(port,path,*args,**kwargs):
  result=real(port,path,*args,**kwargs)
  if path=='/gateway/use' and attempts[0]==0:attempts[0]+=1;raise ProbeError('injected reply loss')
  return result
 probe._post=drop_once
 try:probe.acceptance(temp);raise AssertionError('ambiguous create reported success')
 except ProbeUncertain:pass
 finally:probe._post=real
 j=Path(temp)/'signed-probe-acceptance.json';entry=json.loads(j.read_bytes());assert entry['phase']=='create-intent' and attempts==[1];probe.read_known(entry['path'],entry['sha256']);probe.rpc('delete',entry['path'],previousSHA256=entry['sha256']);j.unlink()
 # A mismatch must fail without mutation or leaked probe bytes.
 try:probe.read_known('codi-health-known.txt','0'*64);raise AssertionError('wrong hash accepted')
 except ProbeError:pass
 probe.close()
private.cleanup()
print('PASS real signed provision/read, exact native issuer continuity, acceptance create/read/delete/absence, lost-reply journal and wrong-hash rejection')
