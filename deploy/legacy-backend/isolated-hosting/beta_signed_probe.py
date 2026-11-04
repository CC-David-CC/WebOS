"""Signed registered-account Files probe. Protected launcher supplies pinned JOSE/policy.

No CLI, no production credential creation, no logs. Recovery uses read_known;
acceptance mutation is isolated to a dedicated account and journaled first.
"""
import base64,hashlib,http.client,json,os,re,secrets,stat,tempfile,time,uuid
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
PROOF='codi-request+jws';USE='codi-gateway-use+jws';CERT='codi-identity+jwt';AUTH='/api/v1/gateway/authorize';CHALLENGE='/api/v1/gateway/challenge'
class ProbeError(RuntimeError):
 def __init__(self,message,*,status=None,path=None):super().__init__(message);self.status=status;self.path=path
class ProbeUncertain(ProbeError):pass
def load_probe_config(path):
 path=Path(path);parent=path.parent.lstat()
 if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=os.geteuid() or stat.S_IMODE(parent.st_mode)!=0o700:raise ValueError('private probe directory required')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_nlink!=1 or not 0<a.st_size<=8192:raise ValueError('private probe configuration required')
  raw=os.read(fd,8193);z=os.fstat(fd)
  if len(raw)!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('probe configuration changed')
 finally:os.close(fd)
 value=json.loads(raw)
 if not isinstance(value,dict) or set(value)!={'username','password','subject','path','sha256'} or any(not isinstance(value[k],str) or not value[k] or len(value[k])>256 for k in value) or not re.fullmatch('[0-9a-f]{64}',value['sha256']):raise ValueError('invalid probe configuration')
 return value
class Probe:
 def __init__(self,*,origin,issuer_port,gateway_port,policy,jose,username,password,expected_subject):
  if policy.get('issuer')!=origin or policy.get('mode')!='server' or not isinstance(policy.get('authorityKeys'),list):raise ValueError('Pinned issuer policy required')
  self.origin=origin;self.host=origin.split('://',1)[1];self.issuer=issuer_port;self.gateway=gateway_port;self.policy=policy;self.jose=jose;self.username=username;self.password=password;self.subject=expected_subject;self.key=ec.generate_private_key(ec.SECP256R1());self.sid=str(uuid.uuid4());self.session=None
 def _post(self,port,path,value,token=None,raw=None):
  body=raw if raw is not None else self.jose.dumps(value);headers={'Host':self.host,'Origin':self.origin,'Content-Type':'application/json'}
  if token:headers['Authorization']=token
  c=http.client.HTTPConnection('127.0.0.1',port,timeout=10)
  try:
   c.request('POST',path,body=body.encode(),headers=headers);r=c.getresponse();data=r.read(1048577)
   if len(data)>1048576:raise ProbeError('oversized probe response')
   if r.status!=200:raise ProbeError('signed probe request failed: HTTP '+str(r.status),status=r.status,path=path)
   value=self.jose.loads(data)
   if not isinstance(value,dict):raise ProbeError('invalid probe response')
   return value
  except (OSError,http.client.HTTPException) as e:raise ProbeError('probe transport unavailable') from e
  finally:c.close()
 def _envelope(self,path,value,*,sid=None,gateway_challenge=False):
  challenge=self._post(self.issuer,CHALLENGE if gateway_challenge else '/api/v1/challenge',{'key':self.jose.public_jwk(self.key),'path':path});raw=self.jose.dumps(value);now=int(time.time());proof={'v':1,'nonce':challenge['nonce'],'iss':sid or self.sid,'aud':self.origin,'method':'POST','path':path,'iat':now,'exp':now+60,'request_sha256':self.jose.digest(raw)}
  return {'request':raw,'proof':self.jose.sign(proof,self.key,PROOF)}
 def enter(self,operation='signin'):
  if operation not in ('signin','register'):raise ValueError('invalid operation')
  request=self._envelope('/api/v1/auth',{'username':self.username,'password':self.password,'operation':operation});session=self._post(self.issuer,'/api/v1/auth',request);identity=session['identity'];header,_,_,_=self.jose.inspect(identity['certificate'],CERT,16384);keys=[x for x in self.policy['authorityKeys'] if x.get('kid')==header.get('kid')]
  if len(keys)!=1:raise ProbeError('unknown issuer authority')
  claims=self.jose.verify(identity['certificate'],keys[0]['jwk'],CERT,16384);now=int(time.time())
  if claims.get('v')!=1 or claims.get('iss')!=self.origin or claims.get('aud')!=self.policy.get('audience') or claims.get('kind')!='registered' or (self.subject is not None and claims.get('sub')!=self.subject) or not isinstance(claims.get('sub'),str) or claims.get('sid')!=identity.get('sid') or identity.get('key')!=self.jose.public_jwk(self.key) or claims.get('cnf',{}).get('jwk')!=self.jose.public_jwk(self.key) or any(claims.get(k)!=identity.get(k) for k in ('sid','sub','name','kind')) or type(claims.get('iat')) is not int or type(claims.get('exp')) is not int or claims['iat']>now+30 or not now<claims['exp']<=claims['iat']+900:raise ProbeError('issuer identity binding mismatch')
  if self.subject is None:
   if operation!='register':raise ProbeError('pinned probe account subject required')
   self.subject=identity['sub']
  self.sid=identity['sid'];self.session=session;return identity['sub']
 def close(self):
  if self.session is None:return
  try:
   request=self._envelope('/api/v1/logout',{},sid=self.sid);self._post(self.issuer,'/api/v1/logout',request,token='Codi '+self.session['session_token'])
  finally:self.session=None;self.password=''
 def rpc(self,operation,path,**fields):
  if self.session is None:raise ProbeError('probe session required')
  raw=self.jose.dumps({'resource':'my-files','operation':operation,'path':path,**fields});digest=self.jose.digest(raw);ch=self._post(self.gateway,'/gateway/challenge',{'key':self.jose.public_jwk(self.key),'request_sha256':digest});envelope=self._envelope(AUTH,{'nonce':ch['nonce'],'request_sha256':ch['request_sha256']},sid=self.sid,gateway_challenge=True);grant=self._post(self.issuer,AUTH,envelope,token='Codi '+self.session['session_token']);now=int(time.time());proof={'v':1,'iss':self.sid,'aud':self.origin+'/gateway','nonce':ch['nonce'],'grant_sha256':self.jose.digest(grant['confirmation']),'request_sha256':ch['request_sha256'],'method':'POST','path':'/gateway/use','iat':now,'exp':now+25};authorization='Codi-File '+grant['confirmation']+' '+self.jose.sign(proof,self.key,USE)
  try:return self._post(self.gateway,'/gateway/use',{},token=authorization,raw=raw)
  except ProbeError as e:
   if operation in ('create','delete'):raise ProbeUncertain('mutation result unknown; retain acceptance journal') from e
   raise
 def read_known(self,path,expected_sha):
  if not re.fullmatch('[0-9a-f]{64}',expected_sha):raise ValueError('exact probe digest required')
  result=self.rpc('read',path);data=base64.b64decode(result['data'],validate=True);digest=hashlib.sha256(data).hexdigest()
  if len(data)!=result['bytes'] or digest!=result['sha256'] or digest!=expected_sha:raise ProbeError('probe content mismatch')
  return {'sha256':digest,'bytes':len(data)}
 def acceptance(self,journal_dir):
  root=Path(journal_dir);st=root.lstat()
  if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.geteuid() or stat.S_IMODE(st.st_mode)!=0o700:raise ValueError('private acceptance journal directory required')
  path='codi-health-'+secrets.token_hex(16)+'.txt';payload=secrets.token_bytes(32);digest=hashlib.sha256(payload).hexdigest();journal=root/'signed-probe-acceptance.json'
  if journal.exists() or journal.is_symlink():raise ValueError('prior probe acceptance needs reconciliation')
  def save(phase):
   raw=(json.dumps({'version':1,'phase':phase,'path':path,'sha256':digest},sort_keys=True)+'\n').encode();fd,name=tempfile.mkstemp(prefix='.probe-',dir=root)
   try:
    with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(name,journal);d=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
   finally:
    if os.path.exists(name):os.unlink(name)
  save('create-intent');created=self.rpc('create',path,data=base64.b64encode(payload).decode())
  if created.get('sha256')!=digest:raise ProbeError('created probe digest mismatch')
  self.read_known(path,digest);save('delete-intent');self.rpc('delete',path,previousSHA256=digest)
  try:self.rpc('read',path)
  except ProbeError as error:
   if error.status!=404 or error.path!='/gateway/use':raise
  else:raise ProbeError('deleted probe remains visible')
  journal.unlink();d=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
  return {'createdAndDeleted':True,'bytes':len(payload)}

def provision_private(root, *, origin, issuer_port, gateway_port, policy, jose):
 """Provision once in isolated/private state. Ambiguous work stays journaled."""
 root=Path(root);st=root.lstat()
 if not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.geteuid() or stat.S_IMODE(st.st_mode)!=0o700:raise ValueError('private probe directory required')
 config=root/'probe.json';journal=root/'probe-provision.json'
 if config.exists() or config.is_symlink() or journal.exists() or journal.is_symlink():raise ValueError('existing probe or unresolved provisioning')
 def save(path,value):
  fd,name=tempfile.mkstemp(prefix='.probe-private-',dir=root)
  try:
   with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),0o600);f.write((json.dumps(value,sort_keys=True)+'\n').encode());f.flush();os.fsync(f.fileno())
   os.replace(name,path);d=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
  finally:
   if os.path.exists(name):os.unlink(name)
 username='codihealth'+secrets.token_hex(6);password=secrets.token_hex(16);known=b'Codi beta Files health probe v1\n';digest=hashlib.sha256(known).hexdigest();path='codi-health-known.txt'
 state={'version':1,'phase':'register-intent','username':username,'password':password,'path':path,'sha256':digest}
 save(journal,state)
 probe=Probe(origin=origin,issuer_port=issuer_port,gateway_port=gateway_port,policy=policy,jose=jose,username=username,password=password,expected_subject=None)
 try:
  subject=probe.enter('register');state.update(phase='create-intent',subject=subject);save(journal,state)
  created=probe.rpc('create',path,data=base64.b64encode(known).decode())
  if created.get('sha256')!=digest:raise ProbeError('created known probe digest mismatch')
  probe.read_known(path,digest);save(config,{'username':username,'password':password,'subject':subject,'path':path,'sha256':digest})
  journal.unlink();d=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
  return subject
 finally:
  if probe.session is not None:
   try:probe.close()
   except ProbeError:pass
