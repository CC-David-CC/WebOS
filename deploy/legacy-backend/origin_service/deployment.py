"""Journaled code-only transitions. Account/authority state is never restored."""
import json,secrets,shutil,subprocess,time
from pathlib import Path
from origin_service import maintenance

ROLES=('issuer','steward','guest','issuer-bootstrap')
MUTABLE={'release','python','manifestSHA256'}
def slot(config_path,name):return Path(config_path).parent/name
def write(op,path,value):op.atomic(path,json.dumps(value,indent=2).encode()+b'\n')
def history(op,config,config_path):
 file=slot(config_path,'code-history.json')
 if not file.exists():return {'version':'codi-code-history/1','instance':config['instance'],'entries':[]}
 value=json.loads(op.read_owned(file,0,0o600))
 if set(value)!={'version','instance','entries'} or value['version']!='codi-code-history/1' or value['instance']!=config['instance'] or not isinstance(value['entries'],list) or len(value['entries'])>16:raise ValueError('Invalid code transition history')
 return value
def record(op,config,config_path,journal,outcome,detail=None):
 value=history(op,config,config_path);entry={key:journal[key] for key in ['id','kind','before','after','activeRoles']}
 entry.update(outcome=outcome,completed=int(time.time()))
 if 'undo' in journal:entry['undo']=journal['undo']
 if detail:entry['detail']=detail[:1500]
 value['entries']=[old for old in value['entries'] if old['id']!=entry['id']]+[entry];value['entries']=value['entries'][-16:];write(op,slot(config_path,'code-history.json'),value)
def active(op,config):
 selected=[]
 for role in ROLES:
  fields=dict(line.split('=',1) for line in op.systemctl('show',op.unit(config,role),'-p','ActiveState','-p','MainPID').splitlines())
  if role=='issuer-bootstrap' and (fields['MainPID']!='0' or fields['ActiveState'] not in ('inactive','failed')):raise ValueError('Stop bootstrap before changing code')
  if fields['ActiveState']=='active' and int(fields['MainPID'])>0:selected.append(role)
  elif fields['ActiveState'] not in ('inactive','failed'):raise ValueError('Wait for or stop transitioning unit before changing code')
 return selected
def validate_pair(op,current,before,after):
 if current not in (before,after) or set(before)!=set(after) or any(before[key]!=after[key] for key in before if key not in MUTABLE):raise ValueError('Code transition cannot migrate identity, mount, ports, ownership or state')
 if before['version'] not in ('codi-managed-instance/2','codi-managed-instance/3','codi-managed-instance/4','codi-managed-instance/5') or before['maintenance']!=1:raise ValueError('Create a coherent checkpoint before changing code')
 if Path(before['unitDir'])!=Path('/etc/systemd/system'):raise ValueError('Unexpected managed unit directory')
 prior=json.loads((Path(before['release'])/'connected-release.json').read_text())['version']
 target=json.loads((Path(after['release'])/'connected-release.json').read_text())['version']
 if (prior in ('codi-connected-development/14','codi-connected-development/15'))!=(target in ('codi-connected-development/14','codi-connected-development/15')) and (before.get('turn') or {}).get('iceTransportPolicy')=='all':raise ValueError('Configure relay-only before crossing the ICE preference code profile boundary')
def target(op,config,release,python):
 source=op.path(release);environment=Path(python);state=Path(config['stateRoot'])
 for first,second in [(state,source),(state,environment.parent.parent),(source,environment.parent.parent)]:
  if first.is_relative_to(second) or second.is_relative_to(first):raise ValueError('Code/environment/state must remain disjoint')
 if any(path.is_relative_to(Path(base)) for path in [source,environment] for base in ['/home','/root','/tmp','/var/tmp','/run']):raise ValueError('Install candidate code/environment outside homes/temp/runtime')
 after={**config,'release':str(source),'python':str(environment),'manifestSHA256':op.verify(source)['manifestSHA256']};op.installed(after)
 return after
def syntax(op,config,config_path):
 folder=slot(config_path,'.code-verify-'+secrets.token_hex(8));folder.mkdir(mode=0o700)
 try:
  files=[]
  for role in ROLES:
   file=folder/op.unit(config,role);op.atomic(file,op.render(config,role),0o644);files.append(file)
  op.run(['/usr/bin/systemd-analyze','verify',*files])
 finally:shutil.rmtree(folder)
def stop_all(op,config):op.stop(config,list(reversed(ROLES)))
def apply(op,config,config_path):
 for role in ROLES:op.atomic(Path(config['unitDir'])/op.unit(config,role),op.render(config,role),0o644)
 write(op,config_path,config);op.systemctl('daemon-reload')
def start_checked(op,config,roles,config_path):
 maintenance.guard_epoch(op,config,config_path)
 if 'guest' in roles and config.get('guestNetwork'):
  from origin_service import network_management
  network_management.start_backend(op,config)
 for role in roles:
  if op.systemctl('show',op.unit(config,role),'-p','ActiveState','--value').strip()=='failed':op.systemctl('reset-failed',op.unit(config,role))
 if roles:op.systemctl('start',*[op.unit(config,role) for role in roles]);op.ready(config,roles)
 # Mode alone is insufficient: the actual issuer policy must still match the
 # operator-installed public pin, even for a listener that returns HTTP 200.
 policy=json.loads(op.read_owned(Path(config['stateRoot'])/'public/origin-discovery.json',0,0o444));expected=policy['identity']
 if 'issuer' in roles and op.issuer_config(config)['identity']!=expected:raise ValueError('Candidate issuer identity differs from the pinned policy')
 if 'steward' in roles:
  from origin_service.discovery import DiscoverySource
  source=DiscoverySource(Path(config['stateRoot'])/'public/origin-discovery.json',Path(config['stateRoot'])/'public/steward/bundle.json',expected,config['basePath']);source.read()
def clear(op,config_path):
 slot(config_path,'maintenance.json').unlink();maintenance.sync_directory(Path(config_path).parent)
def revert(op,config_path,journal,detail):
 before=journal['before'];op.installed(before);journal['phase']='rolling-back';write(op,slot(config_path,'maintenance.json'),journal)
 stop_all(op,before);apply(op,before,config_path);start_checked(op,before,journal['activeRoles'],config_path)
 record(op,before,config_path,journal,'reverted',detail);clear(op,config_path)
 return {'status':'candidate-failed-rolled-back','id':journal['id'],'restoredRelease':before['release'],'activeRoles':journal['activeRoles'],'currentStatePreserved':True,'detail':detail[:1500]}
def transition(op,config,config_path,after,kind='upgrade',undo=None):
 maintenance.require_clean(op,config_path);maintenance.guard(op,config,config_path);validate_pair(op,config,config,after)
 if config==after:return {'status':'already-current','release':config['release'],'currentStatePreserved':True}
 op.installed(after);syntax(op,after,config_path);selected=active(op,config)
 journal={'version':'codi-code-transition/1','id':secrets.token_hex(16),'kind':kind,'phase':'prepared','before':config,'after':after,'activeRoles':selected,'created':int(time.time())}
 if undo:journal['undo']=undo
 write(op,slot(config_path,'maintenance.json'),journal)
 try:
  stop_all(op,config);journal['phase']='switching';write(op,slot(config_path,'maintenance.json'),journal);apply(op,after,config_path)
  journal['phase']='starting';write(op,slot(config_path,'maintenance.json'),journal);start_checked(op,after,selected,config_path)
  record(op,after,config_path,journal,'applied');clear(op,config_path)
  return {'status':'upgraded' if kind=='upgrade' else 'rolled-back','id':journal['id'],'release':after['release'],'activeRoles':selected,'currentStatePreserved':True}
 except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:
  # A committed history record is the success commit point. A failure clearing
  # its journal is resumed as a committed transition, not falsely called failed.
  value=history(op,after,config_path)
  if any(entry['id']==journal['id'] and entry['outcome']=='applied' for entry in value['entries']):raise ValueError('Code committed; finish recover-operation to clear its journal') from error
  try:return revert(op,config_path,journal,type(error).__name__+': '+str(error))
  except (OSError,ValueError,subprocess.SubprocessError) as failure:raise ValueError('Code rollback incomplete; state retained and journal blocks start/signing. Use recover-operation. '+str(failure)) from failure
def upgrade(op,config,config_path,release,python):return transition(op,config,config_path,target(op,config,release,python))
def rollback(op,config,config_path):
 if slot(config_path,'maintenance.json').exists():return recover(op,config,config_path,force_before=True)
 for role in ROLES:
  if op.read_owned(Path(config['unitDir'])/op.unit(config,role),0,0o644)!=op.render(config,role):raise ValueError('Review changed unit files before code rollback')
 value=history(op,config,config_path);undone={entry.get('undo') for entry in value['entries'] if entry['kind']=='rollback' and entry['outcome']=='applied'}
 # A separate policy transaction may have advanced metadata since the upgrade.
 # Select retained code while preserving every current policy/state field.
 compatible=lambda saved:{k:v for k,v in saved.items() if k not in ('version','turn','userFiles','guestNetwork')}=={k:v for k,v in config.items() if k not in ('version','turn','userFiles','guestNetwork')}
 entry=next((entry for entry in reversed(value['entries']) if entry['kind']=='upgrade' and entry['outcome']=='applied' and entry['id'] not in undone and compatible(entry['after'])),None)
 if entry is None:raise ValueError('No retained successful upgrade matches the current configuration')
 before={**config,**{key:entry['before'][key] for key in MUTABLE}}
 op.installed(before);return transition(op,config,config_path,before,'rollback',entry['id'])
def recover(op,config,config_path,force_before=False):
 journal=json.loads(op.read_owned(slot(config_path,'maintenance.json'),0,0o600))
 if journal.get('version')!='codi-code-transition/1' or journal.get('kind') not in ('upgrade','rollback') or not isinstance(journal.get('activeRoles'),list) or len(set(journal['activeRoles']))!=len(journal['activeRoles']) or any(role not in op.ROLES for role in journal['activeRoles']):raise ValueError('Not a valid code transition journal; preserve data recovery separately')
 validate_pair(op,config,journal['before'],journal['after']);value=history(op,config,config_path)
 committed=any(entry['id']==journal['id'] and entry['outcome']=='applied' for entry in value['entries'])
 if committed and not force_before:
  after=journal['after'];op.installed(after);stop_all(op,after);apply(op,after,config_path);start_checked(op,after,journal['activeRoles'],config_path);clear(op,config_path)
  return {'status':'committed-code-recovered','id':journal['id'],'release':after['release'],'currentStatePreserved':True}
 result=revert(op,config_path,journal,'Explicit recovery of interrupted code transition');result['status']='interrupted-code-rolled-back';return result
