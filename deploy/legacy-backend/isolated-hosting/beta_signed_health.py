"""Lock-bound signed read health; protected launcher must supply verified dependencies.

This is not a launcher. In particular its caller must pin code, JOSE, issuer,
gateway, policy and every credential-directory ancestor under host custody.
"""
import hashlib,http.client,json
from beta_signed_probe import Probe,ProbeError,load_probe_config

class SignedHealth:
 def __init__(self,*,check_lock,check_custody,origin,issuer_port,gateway_port,policy,policy_sha256,credential_path,jose):
  if not callable(check_lock) or not callable(check_custody):raise ValueError('lock and custody checks required')
  if hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=policy_sha256:raise ValueError('policy pin mismatch')
  self.check_lock=check_lock;self.check_custody=check_custody;self.origin=origin;self.issuer=issuer_port;self.gateway=gateway_port;self.policy=policy;self.pin=policy_sha256;self.credentials=credential_path;self.jose=jose
 def __call__(self):
  self.check_lock();self.check_custody();self.check_lock()
  if hashlib.sha256(json.dumps(self.policy,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=self.pin:raise ValueError('policy changed')
  c=http.client.HTTPConnection('127.0.0.1',self.issuer,timeout=10)
  try:
   c.request('GET','/config.json',headers={'Host':self.origin.split('://',1)[1]});r=c.getresponse();body=r.read(1048577)
   if r.status!=200 or len(body)>1048576:raise ProbeError('issuer configuration unavailable')
   if json.loads(body).get('identity')!=self.policy:raise ProbeError('issuer identity differs from pinned policy')
  finally:c.close()
  cfg=load_probe_config(self.credentials);self.check_lock();self.check_custody();self.check_lock()
  p=Probe(origin=self.origin,issuer_port=self.issuer,gateway_port=self.gateway,policy=self.policy,jose=self.jose,username=cfg['username'],password=cfg['password'],expected_subject=cfg['subject'])
  try:
   p.enter();result=p.read_known(cfg['path'],cfg['sha256']);self.check_lock();self.check_custody();self.check_lock();return result
  finally:
   if p.session is not None:p.close()
