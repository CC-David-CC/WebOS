"""Private, explicit backup/recovery for the managed native service layout.

Caller holds the operator's per-instance lock. No network listener or timer.
Recovery preserves issuer/root identities, rotates the delegated service key and
quarantines recovered registered credentials. Code rollback must not restore data.
"""
import hashlib,json,os,secrets,shutil,sqlite3,stat,time
from pathlib import Path
from urllib.parse import quote
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from steward.protocol import jose
from steward.provision import verified_seed
from steward.root_authority import RootAuthority
from steward.publisher import PublisherState
from steward.server import StewardServer

PRIVATE='operator/staging/steward-private/provisioned'
FILES={
 'issuer/state/issuer.pem':('issuer',0o600),
 'issuer/state/accounts.sqlite3':('issuer',0o600),
 'steward/service.pem':('steward',0o600),
 'steward/provision.json':('steward',0o600),
 'steward/ledger/publisher.sqlite3':('steward',0o600),
 'operator/issuer-config.json':('root',0o600),
 'operator/root/root.pem':('root',0o600),
 'operator/root/authority.sqlite3':('root',0o600),
 PRIVATE+'/service.pem':('root',0o600),
 PRIVATE+'/provision.json':('root',0o600),
 PRIVATE+'/origin-discovery.json':('root',0o600),
 PRIVATE+'/ledger/publisher.sqlite3':('root',0o600),
 'public/origin-discovery.json':('root',0o444),
}
MAXIMUM=134217728
def digest(raw):return hashlib.sha256(raw).hexdigest()
def control(config_path,name):return Path(config_path).parent/name
def sync_directory(path):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def sync_tree(root):
 for directory in sorted([root,*(path for path in root.rglob('*') if path.is_dir())],key=lambda path:len(path.parts),reverse=True):sync_directory(directory)
def ro_db(path):
 for suffix in ['-journal','-wal','-shm']:
  file=Path(str(path)+suffix)
  if file.exists() or file.is_symlink():raise ValueError('Unclean SQLite sidecar requires explicit recovery before backup')
 db=sqlite3.connect('file:'+quote(str(path),safe='/')+'?mode=ro',uri=True,timeout=2)
 if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:db.close();raise ValueError('SQLite integrity check failed')
 return db
def binding(root):
 """Validate related keys/policies/ledgers, including expired signed backups."""
 root=Path(root);authority=RootAuthority(root/'operator/root');provision=authority.provision();inspected=jose.inspect(provision['seed'],'codi-seed/1',32768)[1]
 seed=verified_seed(provision['seed'],provision['root_key'],provision['realm'],inspected['iat'])
 policy=jose.loads((root/'public/origin-discovery.json').read_bytes());identity=policy['identity'];key=serialization.load_pem_private_key((root/'issuer/state/issuer.pem').read_bytes(),password=None)
 issuer_id=jose.thumbprint(jose.public_jwk(key))
 if identity!=provision['identity_policy'] or issuer_id!=jose.thumbprint(identity['authorityKeys'][0]['jwk']) or policy['pin']['rootKey']!=provision['root_key'] or policy['pin']['realm']!=provision['realm'] or policy['scope']!=seed['stewards'][0]['scopes'][0]:raise ValueError('Recovery issuer/root/policy binding mismatch')
 service=serialization.load_pem_private_key((root/'steward/service.pem').read_bytes(),password=None)
 if jose.thumbprint(jose.public_jwk(service))!=seed['stewards'][0]['key_id']:raise ValueError('Recovery service key mismatch')
 if jose.loads((root/'steward/provision.json').read_bytes())!=provision or jose.loads((root/PRIVATE/'provision.json').read_bytes())!=provision:raise ValueError('Export the committed root policy before taking a coherent backup')
 if (root/PRIVATE/'service.pem').read_bytes()!=(root/'steward/service.pem').read_bytes() or (root/PRIVATE/'origin-discovery.json').read_bytes()!=(root/'public/origin-discovery.json').read_bytes():raise ValueError('Recovery staged policy/key binding mismatch')
 accounts=ro_db(root/'issuer/state/accounts.sqlite3')
 try:
  if accounts.execute('SELECT version FROM account_policy_metadata').fetchall()!=[(1,)]:raise ValueError('Recovery account policy schema')
  if accounts.execute('SELECT count(*) FROM accounts LEFT JOIN account_policy USING(subject) WHERE account_policy.subject IS NULL').fetchone()[0]:raise ValueError('Recovery account policy missing')
  count=accounts.execute('SELECT count(*) FROM accounts').fetchone()[0]
 finally:accounts.close()
 publisher=ro_db(root/'steward/ledger/publisher.sqlite3')
 try:
  row=publisher.execute('SELECT binding,seed_revision,revision,token,frozen FROM publisher WHERE id=1').fetchone()
  if row is None or row[4] or row[1]!=seed['revision'] or type(row[2]) is not int or row[2]<1:raise ValueError('Recovery publisher state unavailable')
  descriptor=jose.verify(row[3],seed['stewards'][0]['public_key'],'codi-steward/1',8192)
  if descriptor['revision']!=row[2] or descriptor['key_id']!=seed['stewards'][0]['key_id'] or descriptor['endpoint']!=provision['endpoint']:raise ValueError('Recovery publisher token binding')
 finally:publisher.close()
 for file in [root/'operator/root/authority.sqlite3',root/PRIVATE/'ledger/publisher.sqlite3']:
  db=ro_db(file);db.close()
 return {'issuerKeyId':issuer_id,'rootKeyId':jose.thumbprint(provision['root_key']),'realm':provision['realm'],'rootRevision':seed['revision'],'publisherRevision':row[2],'serviceKeyId':seed['stewards'][0]['key_id'],'accounts':count}
def fence(op,config,config_path,value):
 target=control(config_path,'recovery-fence.json')
 stable={name:value[name] for name in ['issuerKeyId','rootKeyId','realm']}
 if target.exists():
  saved=json.loads(op.read_owned(target,0,0o600))
  if saved['instance']!=config['instance'] or any(saved[name]!=item for name,item in stable.items()):raise ValueError('External recovery fence binding changed')
  return saved
 return {'version':'codi-recovery-fence/1','instance':config['instance'],**stable,'rootFloor':value['rootRevision'],'backups':{}}
def adopt(op,config,config_path):
 if config['version']=='codi-managed-instance/1':
  config={**config,'version':'codi-managed-instance/2','maintenance':1}
  op.atomic(config_path,json.dumps(config,indent=2).encode()+b'\n')
 return config
def require_clean(op,config_path):
 if control(config_path,'maintenance.json').exists():raise ValueError('Interrupted recovery is pending; complete recover-operation before starting or signing')
def reserve(op,config,config_path):
 """Write-ahead root epoch reservation before an ordinary root renewal."""
 require_clean(op,config_path);root=Path(config['stateRoot']);authority=RootAuthority(root/'operator/root');seed=jose.inspect(authority.provision()['seed'],'codi-seed/1',32768)[1]
 target=control(config_path,'recovery-fence.json')
 if target.exists():
  saved=json.loads(op.read_owned(target,0,0o600))
  if saved['rootFloor']>seed['revision']+1:raise ValueError('Root state is behind its recovery fence')
  saved['rootFloor']=max(saved['rootFloor'],seed['revision']+1);op.atomic(target,jose.dumps(saved).encode())
def guard(op,config,config_path):
 require_clean(op,config_path);guard_epoch(op,config,config_path)
def guard_epoch(op,config,config_path):
 target=control(config_path,'recovery-fence.json')
 if target.exists():
  saved=jose.loads(op.read_owned(target,0,0o600));root=RootAuthority(Path(config['stateRoot'])/'operator/root');revision=jose.inspect(root.provision()['seed'],'codi-seed/1',32768)[1]['revision']
  if revision<saved['rootFloor']:raise ValueError('Root state is behind the independent recovery fence; renew or recover explicitly')
def backup(op,config,config_path,output):
 require_clean(op,config_path)
 for role in ['issuer','steward','issuer-bootstrap']:op.inactive(config,role)
 # Guest networking has no writable identity/authority state. Keep its live
 # sockets/cookie while checkpointing, but reject a modified guest sandbox.
 guest=dict(line.split('=',1) for line in op.systemctl('show',op.unit(config,'guest'),'-p','MainPID','-p','User','-p','ProtectSystem','-p','NoNewPrivileges','-p','CapabilityBoundingSet','-p','ReadWritePaths','-p','DropInPaths').splitlines())
 if int(guest.get('MainPID','0')):
  if guest['User']!='codi-guest' or guest['ProtectSystem']!='strict' or guest['NoNewPrivileges']!='yes' or any(guest[key] for key in ['CapabilityBoundingSet','ReadWritePaths','DropInPaths']):raise ValueError('Review guest isolation before checkpointing while it runs')
  if op.read_owned(Path(config['unitDir'])/op.unit(config,'guest'),0,0o644)!=op.render(config,'guest'):raise ValueError('Guest unit differs from its pinned sandbox')
 state=Path(config['stateRoot']);output=op.path(output)
 for other in [state,Path(config['release']),Path(config['python']).parent.parent]:
  if output.is_relative_to(other) or other.is_relative_to(output):raise ValueError('Backup must be outside source, environment and state')
 if output.exists() or output.is_symlink():raise ValueError('Backup destination already exists')
 parent=op.path(output.parent)
 if stat.S_IMODE(parent.stat().st_mode)!=0o700:raise ValueError('Backup parent must be root-owned 0700')
 _,people=op.installed(config);temporary=parent/('.backup-'+secrets.token_hex(8));temporary.mkdir(mode=0o700)
 try:
  records={}
  for name,(role,mode) in FILES.items():
   uid=0 if role=='root' else people[role]['uid'];raw=op.read_owned(state/name,uid,mode,MAXIMUM);target=temporary/'state'/name;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
   for directory in target.parents:
    if directory==temporary:break
    directory.chmod(0o700)
   op.atomic(target,raw);records[name]={'owner':role,'mode':mode,'bytes':len(raw),'sha256':digest(raw)}
  value=binding(temporary/'state');saved=fence(op,config,config_path,value)
  if value['rootRevision']<saved['rootFloor']:raise ValueError('Backup root epoch is behind its independent fence')
  config=adopt(op,config,config_path)
  manifest={'version':'codi-managed-backup/1','created':int(time.time()),'config':config,'binding':value,'files':records};raw=jose.dumps(manifest).encode();op.atomic(temporary/'backup.json',raw)
  sync_tree(temporary);os.rename(temporary,output);sync_directory(parent);saved['rootFloor']=max(saved['rootFloor'],value['rootRevision']);saved['backups'][str(output)]=digest(raw);op.atomic(control(config_path,'recovery-fence.json'),jose.dumps(saved).encode())
  return {'status':'backed-up','directory':str(output),'manifestSHA256':digest(raw),'files':len(records),'binding':value,'credentialsIncluded':True,'configVersion':config['version'],'guestRelayKeptRunning':bool(int(guest.get('MainPID','0')))}
 finally:
  if temporary.exists():shutil.rmtree(temporary)
def verify_backup(op,output,expected):
 output=op.path(output)
 if stat.S_IMODE(output.stat().st_mode)!=0o700:raise ValueError('Backup directory must be 0700')
 raw=op.read_owned(output/'backup.json',0,0o600);manifest=jose.loads(raw)
 if digest(raw)!=expected or set(manifest)!={'version','created','config','binding','files'} or manifest['version']!='codi-managed-backup/1' or set(manifest['files'])!=set(FILES):raise ValueError('Backup digest/schema mismatch')
 found=set()
 for file in output.rglob('*'):
  info=file.lstat()
  if file.is_symlink() or info.st_uid!=0 or (stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode)!=0o700):raise ValueError('Unsafe backup ownership/type')
  if file.is_dir():continue
  name=str(file.relative_to(output))
  if name=='backup.json':continue
  if not name.startswith('state/') or name[6:] not in FILES:raise ValueError('Unexpected backup file')
  relative=name[6:];record=manifest['files'][relative];data=op.read_owned(file,0,0o600,MAXIMUM)
  if record!={'owner':FILES[relative][0],'mode':FILES[relative][1],'bytes':len(data),'sha256':digest(data)}:raise ValueError('Changed backup data')
  found.add(relative)
 if found!=set(FILES) or binding(output/'state')!=manifest['binding']:raise ValueError('Incomplete/incoherent backup')
 return manifest
def restore(op,config,config_path,output,expected,root_floor,seconds):
 require_clean(op,config_path)
 if root_floor is not None and (type(root_floor) is not int or not 1<=root_floor<2**53-1):raise ValueError('Trusted recovery root floor must be a bounded positive integer')
 for role in [*op.ROLES,'issuer-bootstrap']:op.inactive(config,role)
 if config.get('guestNetwork'):
  from origin_service import network_management
  network_management.require_stopped(op,config)
 manifest=verify_backup(op,output,expected);old=manifest['config']
 for name in ['instance','origin','basePath','ports','stateRoot']:
  if config[name]!=old[name]:raise ValueError('Recovery target differs; explicit identity/mount migration required')
 value=manifest['binding'];saved=fence(op,config,config_path,value)
 if control(config_path,'recovery-fence.json').exists():
  if saved['backups'].get(str(Path(output)))!=expected:raise ValueError('Backup is not registered in this recovery fence')
 elif root_floor is None:raise ValueError('Lost recovery fence requires an explicit trusted root revision floor')
 floor=max(saved['rootFloor'],value['rootRevision'],root_floor or 1)
 state=Path(config['stateRoot']);staged=state.parent/('.recovery-'+secrets.token_hex(8));quarantine=state.parent/('.quarantine-'+secrets.token_hex(8));_,people=op.installed(config)
 staged.mkdir(mode=0o700)
 try:
  for name,(role,mode) in FILES.items():
   target=staged/name;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700);op.atomic(target,op.read_owned(Path(output)/'state'/name,0,0o600,MAXIMUM),mode)
  for directory in staged.rglob('*'):
   if directory.is_dir():directory.chmod(0o700)
  # Recover account identities while requiring explicit credential revalidation.
  db=sqlite3.connect(staged/'issuer/state/accounts.sqlite3')
  try:
   db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE')
   if db.execute('SELECT count(*) FROM account_policy WHERE generation>=9223372036854775807 OR generation<0').fetchone()[0]:raise ValueError('Recovered account generation exhausted')
   db.execute('UPDATE account_policy SET disabled=1,generation=generation+1');db.commit()
  finally:db.close()
  service=ec.generate_private_key(ec.SECP256R1());authority=RootAuthority(staged/'operator/root');provision=authority.recover(seconds,floor,service);revision=jose.inspect(provision['seed'],'codi-seed/1',32768)[1]['revision']
  key=service.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  for name in ['steward/service.pem',PRIVATE+'/service.pem']:op.atomic(staged/name,key)
  for name in ['steward/provision.json',PRIVATE+'/provision.json']:op.atomic(staged/name,jose.dumps(provision).encode())
  # The fresh scoped key has a fresh ledger; no existing-key floor is reset.
  for name in ['steward/ledger',PRIVATE+'/ledger']:shutil.rmtree(staged/name);PublisherState.initialize(staged/name)
  publisher=PublisherState(staged/'steward/ledger');server=StewardServer(**provision,service_key=service,publisher_state=publisher);bundle=server.bundle()
  (staged/'public/steward').mkdir(mode=0o755);op.atomic(staged/'public/steward/bundle.json',jose.dumps(bundle).encode(),0o644)
  restored=binding(staged)
  if restored['issuerKeyId']!=value['issuerKeyId'] or restored['rootKeyId']!=value['rootKeyId'] or restored['rootRevision']<=floor or restored['serviceKeyId']==value['serviceKeyId']:raise ValueError('Recovered authority invariant')
  for role in ['issuer','steward']:
   for file in [staged/role,*(staged/role).rglob('*')]:os.chown(file,people[role]['uid'],people[role]['gid'])
  (staged/'public').chmod(0o755);os.chown(staged/'public/steward',people['steward']['uid'],people['steward']['gid']);os.chown(staged/'public/steward/bundle.json',people['steward']['uid'],people['steward']['gid'])
  journal={'version':'codi-maintenance/1','action':'restore','state':str(state),'staged':str(staged),'quarantine':str(quarantine),'rootRevision':revision,'backupPath':str(output),'backupDigest':expected,'restored':restored}
  sync_tree(staged);sync_directory(staged.parent)
  op.atomic(control(config_path,'maintenance.json'),jose.dumps(journal).encode())
  saved['rootFloor']=revision;op.atomic(control(config_path,'recovery-fence.json'),jose.dumps(saved).encode())
  return recover_operation(op,config,config_path)
 except BaseException:
  if staged.exists() and not control(config_path,'maintenance.json').exists():shutil.rmtree(staged)
  raise
def recover_operation(op,config,config_path):
 initial=jose.loads(op.read_owned(control(config_path,'maintenance.json'),0,0o600))
 if initial.get('version')=='codi-network-transition/1':
  from origin_service import network_management
  return network_management.recover(op,config,config_path)
 if initial.get('version')=='codi-files-transition/1':
  from origin_service import files_management
  return files_management.recover(op,config,config_path)
 if initial.get('version')=='codi-turn-transition/1':
  from origin_service import turn_management
  return turn_management.recover(op,config,config_path)
 if initial.get('version')=='codi-code-transition/1':
  from origin_service import deployment
  return deployment.recover(op,config,config_path)
 for role in [*op.ROLES,'issuer-bootstrap']:op.inactive(config,role)
 target=control(config_path,'maintenance.json');journal=jose.loads(op.read_owned(target,0,0o600))
 if journal['version']!='codi-maintenance/1' or journal['action']!='restore' or journal['state']!=config['stateRoot']:raise ValueError('Invalid recovery journal')
 state=Path(journal['state']);staged=Path(journal['staged']);quarantine=Path(journal['quarantine'])
 if staged.parent!=state.parent or quarantine.parent!=state.parent or not staged.name.startswith('.recovery-') or not quarantine.name.startswith('.quarantine-'):raise ValueError('Unsafe recovery journal paths')
 for directory in [state,staged,quarantine]:
  if directory.is_symlink():raise ValueError('Symlink in recovery journal state')
  if directory.exists() and (not directory.is_dir() or directory.stat().st_uid!=0 or directory.stat().st_mode&0o022):raise ValueError('Unsafe recovery directory ownership/type')
 fence_file=control(config_path,'recovery-fence.json')
 if fence_file.exists():saved=jose.loads(op.read_owned(fence_file,0,0o600))
 else:saved={'version':'codi-recovery-fence/1','instance':config['instance'],**{name:journal['restored'][name] for name in ['issuerKeyId','rootKeyId','realm']},'rootFloor':journal['rootRevision'],'backups':{journal['backupPath']:journal['backupDigest']}}
 if saved['rootFloor']>journal['rootRevision']:raise ValueError('Recovery intent is behind the independent fence; preserve all state')
 saved['rootFloor']=journal['rootRevision'];op.atomic(fence_file,jose.dumps(saved).encode())
 if staged.exists():
  if state.exists():
   if quarantine.exists():raise ValueError('Ambiguous recovery directories; preserve all state')
   state.chmod(0o700);sync_directory(state)
   os.rename(state,quarantine);sync_directory(state.parent)
  os.rename(staged,state)
 if quarantine.exists():quarantine.chmod(0o700);sync_directory(quarantine)
 if not state.exists() or staged.exists():raise ValueError('Interrupted recovery requires preserved staged state; do not reinitialize')
 state.chmod(0o755)
 # Check identity after the directory swap. Both online roles remain stopped.
 root=RootAuthority(state/'operator/root');seed=jose.inspect(root.provision()['seed'],'codi-seed/1',32768)[1]
 if seed['revision']!=journal['rootRevision']:raise ValueError('Recovered root epoch mismatch')
 sync_directory(state);sync_directory(state.parent)
 target.unlink();sync_directory(target.parent);return {'status':'restored','binding':journal['restored'],'quarantinedOldState':str(quarantine),'accountsRequireCredentialReset':True,'servicesStarted':False}
