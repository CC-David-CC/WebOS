"""Managed-operator adapter for a journaled, one-epoch steward recovery.

Source-only until packaged and tested against isolated installed systemd units.
All methods are called while the existing managed operator lock is held.
"""
import hashlib,time
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from steward.protocol import jose,times
from steward.root_authority import RootAuthority
from steward.provision import verified_seed
from origin_service.expired_root_steps import make_checkpoint,inspect_signed_exports,verify_publisher

def _sha(value):return hashlib.sha256(value).hexdigest()

class ManagedExpiredRoot:
 def __init__(self,op,maintenance,config_path,*,config_sha256,release_sha256,seconds=86400,clock=time.time):
  self.op=op;self.maintenance=maintenance;self.path=Path(config_path);self.config_sha256=config_sha256;self.release_sha256=release_sha256;self.seconds=seconds;self.clock=clock
  if type(seconds) is not int or not 30<=seconds<=86400:raise ValueError('Bounded root lifetime required')
  op.path(self.path);op.path(self.path.parent)
 def locked(self):return self.op.locked(self.path)
 def _config(self,record=None):
  raw=self.op.read_owned(self.path,0,0o600);c=self.op.load(self.path)
  if _sha(raw)!=self.config_sha256 or c['manifestSHA256']!=self.release_sha256:raise ValueError('Managed configuration or immutable release pin changed')
  if record and (record['configSHA256']!=self.config_sha256 or record['releaseSHA256']!=self.release_sha256 or record['seconds']!=self.seconds):raise ValueError('Journal pins or authority lifetime differ from installed service')
  self.maintenance.require_clean(self.op,self.path);return c
 def initial(self):
  c=self._config();binding=self.maintenance.binding(c['stateRoot']);fence=self.maintenance.fence(self.op,c,self.path,binding)
  if fence['rootFloor']!=binding['rootRevision']:raise ValueError('Start only from a coherent independent root fence')
  root=RootAuthority(Path(c['stateRoot'])/'operator/root').provision()
  return {'version':'codi-expired-root-recovery/1','checkpoint':make_checkpoint(root),'configSHA256':self.config_sha256,'releaseSHA256':self.release_sha256,'publisherRevision':binding['publisherRevision'],'seconds':self.seconds}
 def _snapshot(self,record):
  c=self._config(record);state=Path(c['stateRoot']);_,people=self.op.installed(c);issuer_uid=people['issuer']['uid'];steward_uid=people['steward']['uid']
  root=RootAuthority(state/'operator/root').provision();staged=jose.loads(self.op.read_owned(state/'operator/staging/steward-private/provisioned/provision.json',0,0o600));live=jose.loads(self.op.read_owned(state/'steward/provision.json',steward_uid,0o600))
  policy_raw=self.op.read_owned(state/'public/origin-discovery.json',0,0o444);staged_policy=self.op.read_owned(state/'operator/staging/steward-private/provisioned/origin-discovery.json',0,0o600)
  if policy_raw!=staged_policy:raise ValueError('Pinned discovery policy differs from staging')
  policy=jose.loads(policy_raw);identity=policy['identity'];key=serialization.load_pem_private_key(self.op.read_owned(state/'issuer/state/issuer.pem',issuer_uid,0o600),password=None);issuer_id=jose.thumbprint(jose.public_jwk(key))
  if identity!=root['identity_policy'] or issuer_id!=jose.thumbprint(identity['authorityKeys'][0]['jwk']) or policy['pin']['rootKey']!=root['root_key'] or policy['pin']['realm']!=root['realm']:raise ValueError('Issuer or root discovery binding changed')
  grant=verified_seed(root['seed'],root['root_key'],root['realm'],jose.inspect(root['seed'],'codi-seed/1',32768)[1]['iat'])['stewards']
  if len(grant)!=1 or policy['scope']!=grant[0]['scopes'][0] or policy['pin']['endpoints']!=[root['endpoint']]:raise ValueError('Discovery grant changed')
  keys=[]
  for file,uid in [(state/'operator/staging/steward-private/provisioned/service.pem',0),(state/'steward/service.pem',steward_uid)]:
   k=serialization.load_pem_private_key(self.op.read_owned(file,uid,0o600),password=None);keys.append(jose.thumbprint(jose.public_jwk(k)))
  if keys!=[grant[0]['key_id']]*2:raise ValueError('Scoped service keys differ from signed grant')
  fence=jose.loads(self.op.read_owned(self.path.parent/'recovery-fence.json',0,0o600))
  if fence.get('instance')!=c['instance'] or fence.get('issuerKeyId')!=issuer_id or fence.get('rootKeyId')!=record['checkpoint']['rootKeyId'] or fence.get('realm')!=root['realm']:raise ValueError('Independent recovery fence binding differs')
  self.op.read_owned(state/'issuer/state/accounts.sqlite3',issuer_uid,0o600,134217728);db=self.maintenance.ro_db(state/'issuer/state/accounts.sqlite3')
  try:
   if db.execute('SELECT version FROM account_policy_metadata').fetchall()!=[(1,)] or db.execute('SELECT count(*) FROM accounts LEFT JOIN account_policy USING(subject) WHERE account_policy.subject IS NULL').fetchone()[0]:raise ValueError('Account policy state unavailable')
  finally:db.close()
  self.op.read_owned(state/'steward/ledger/publisher.sqlite3',steward_uid,0o600,1048576);db=self.maintenance.ro_db(state/'steward/ledger/publisher.sqlite3')
  try:row=db.execute('SELECT binding,seed_revision,seed_hash,revision,token,frozen FROM publisher WHERE id=1').fetchone()
  finally:db.close()
  publisher=verify_publisher(row,root,live,record['checkpoint'],minimum_revision=record['publisherRevision'])
  fields=dict(line.split('=',1) for line in self.op.systemctl('show',self.op.unit(c,'steward'),'-p','ActiveState','-p','MainPID').splitlines())
  if fields['ActiveState'] not in ('active','inactive','failed') or (fields['ActiveState']=='active')!=(fields['MainPID']!='0'):raise ValueError('Steward state is changing; retry after inspection')
  action=self.classify(record,root,staged,live,fence['rootFloor'],fields['ActiveState']=='active')
  return c,root,publisher,action
 def classify(self,record,root,staged,live,fence,running):
  return inspect_signed_exports(root,staged,live,record['checkpoint'],fence_revision=fence,now=int(self.clock()),steward_running=running,ledger_verified=True)
 def decide(self,record):return self._snapshot(record)[3]
 def renew(self,record):
  c,_,_,action=self._snapshot(record)
  if action!='renew-once':raise ValueError('Authority state changed before renewal')
  self.op.inactive(c,'steward');self.op.publish(c,'renew',self.seconds,self.path)
 def export(self,record):
  c,_,_,action=self._snapshot(record)
  if action!='export-committed':raise ValueError('Authority state changed before export')
  self.op.inactive(c,'steward');self.op.publish(c,'export',None,self.path)
 def start(self,record):
  c,_,_,action=self._snapshot(record)
  if action!='start-steward':raise ValueError('Authority state changed before start')
  unit=self.op.unit(c,'steward');state=self.op.systemctl('show',unit,'-p','ActiveState','--value').strip()
  if state=='failed':self.op.systemctl('reset-failed',unit)
  elif state!='inactive':raise ValueError('Steward state changed before starting')
  self.op.systemctl('start',unit);self.op.ready(c,['steward'])
 def verify(self,record):
  c,root,publisher,action=self._snapshot(record)
  if action!='verify-running':raise ValueError('Steward is not running with current authority')
  self.op.ready(c,['steward']);deadline=time.monotonic()+30
  while True:
   public=self.op.issuer_config(c).get('discovery')
   try:
    if not public or public['seed']!=root['seed']:raise ValueError('Current public discovery seed unavailable')
    seed=verified_seed(public['seed'],root['root_key'],root['realm'],int(self.clock()));grant=seed['stewards'][0];descriptor=jose.verify(public['descriptor'],grant['public_key'],'codi-steward/1',8192);times(descriptor,int(self.clock()),300)
    limits={'lease_seconds':grant['limits']['lease_seconds'],'sample_size':min(4,grant['limits']['sample_size']),'signal_bytes':min(32768,grant['limits']['signal_bytes'])}
    if set(descriptor)!={'version','realm','key_id','revision','iat','exp','endpoint','scopes','limits'} or descriptor['version']!='codi-steward/1' or type(descriptor['revision']) is not int or descriptor['revision']<publisher['publisherRevision'] or descriptor['endpoint']!=root['endpoint'] or descriptor['realm']!=root['realm'] or descriptor['key_id']!=grant['key_id'] or descriptor['scopes']!=grant['scopes'] or descriptor['limits']!=limits or descriptor['exp']>grant['exp']:raise ValueError('Public publisher binding or revision unavailable')
    return
   except (KeyError,ValueError,TypeError):
    if time.monotonic()>=deadline:raise ValueError('Current signed public discovery was not published')
    time.sleep(.25)
 def receipt(self,record):
  target=self.path.parent/('expired-root-'+str(record['checkpoint']['baseRevision']+1)+'-receipt.json');value={'version':'codi-expired-root-receipt/1','rootRevision':record['checkpoint']['baseRevision']+1,'configSHA256':record['configSHA256'],'releaseSHA256':record['releaseSHA256'],'publisherFloor':record['publisherRevision'],'rootKeyId':record['checkpoint']['rootKeyId']};raw=(jose.dumps(value)+'\n').encode()
  if target.exists() or target.is_symlink():
   if self.op.read_owned(target,0,0o600)!=raw:raise ValueError('Existing recovery receipt differs')
  else:self.op.atomic(target,raw)
