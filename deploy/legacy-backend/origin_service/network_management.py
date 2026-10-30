"""Native guest policy transitions; external worker operator stays a subprocess.

The native lock is held by the caller. Only public frontend settings are created
here; private worker credentials, ledgers and kernel custody stay with the sealed
external operator. No account, key, file or usage state is ever restored.
"""
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import secrets
import subprocess
import time
from urllib.parse import urlsplit
import urllib.request

from origin_service import maintenance,deployment
from guest_service.runtime import VERSION as FRONTEND_VERSION,metadata,validate as validate_descriptor

VERSION='codi-managed-instance/5'
JOURNAL='codi-network-transition/1'
FIELDS={'configFile','configSHA256','operatorRelease','operatorManifestSHA256','frontendFile','frontendSHA256','policySHA256'}
OPERATOR_FILES=frozenset({*('guest_service/'+name+'.py' for name in ['__init__','authorization','egress','usage','installation','operator']),
    'codiserver-server-v0.3.0/codiauth/__init__.py','codiserver-server-v0.3.0/codiauth/jose.py','requirements.lock','scripts/manage-guest-network.py'})
BACKEND_FIELDS={'version','instance','unitDir','workerRelease','workerSHA256','operatorRelease','operatorSHA256','python','stateRoot','frontendUser','frontendUID','frontendUnit','pingGID','roles','origin','basePath','issuerPolicy','policy','policySHA256','namespacePath','namespaceInode','kernelSHA256','qemuSHA256','secretSHA256'}
ROLES=['issuer','guest']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def slot(config_path,name):return Path(config_path).parent/name
def write(op,file,value):op.atomic(file,encoded(value))

def seal(op,folder,pin):
    folder=op.path(folder);raw=op.read_owned(folder/'guest-operator.json',0,0o644)
    if sha(raw)!=pin:raise ValueError('Guest operator manifest pin changed')
    value=json.loads(raw)
    if not isinstance(value,dict) or set(value)!={'version','files'} or value['version']!='codi-guest-network-operator/1' or set(value['files'])!=OPERATOR_FILES:raise ValueError('Exact sealed guest operator required')
    found=set()
    for file in folder.rglob('*'):
        op.path(file)
        if file.is_dir():continue
        name=str(file.relative_to(folder));found.add(name)
        if name=='guest-operator.json':continue
        raw=op.read_owned(file,0,0o644,262144)
        if value['files'].get(name)!={'bytes':len(raw),'sha256':sha(raw)}:raise ValueError('Guest operator code changed')
    if found!=OPERATOR_FILES|{'guest-operator.json'}:raise ValueError('Missing or extra guest operator code')

class Binding:
    def __init__(self,op,config,value):
        self.op=op;self.config=config;self.value=value
        seal(op,Path(value['operatorRelease']),value['operatorManifestSHA256'])
        raw=op.read_owned(op.path(value['configFile']),0,0o600)
        if sha(raw)!=value['configSHA256']:raise ValueError('Guest backend configuration pin changed')
        c=json.loads(raw);self.backend=c
        if not isinstance(c,dict) or set(c)!=BACKEND_FIELDS or c['version']!='codi-guest-managed/1':raise ValueError('Exact guest backend configuration required')
        if c['operatorRelease']!=value['operatorRelease'] or c['operatorSHA256']!=value['operatorManifestSHA256'] or c['python']!=config['python']:raise ValueError('Guest backend runtime differs from native pins')
        if c['origin']!=config['origin'] or c['basePath']!=config['basePath'] or c['policySHA256']!=value['policySHA256']:raise ValueError('Guest backend origin/mount/policy differs')
        if c['instance']!='codi-net-'+config['instance'].removeprefix('codi-') or c['frontendUnit']!=op.unit(config,'guest') or c['namespacePath'] is not None:raise ValueError('Guest backend must protect this native frontend on the host')
        if c['unitDir']!=config['unitDir'] or c['frontendUser']!='codi-guest' or c['pingGID']!=1001:raise ValueError('Guest backend service binding changed')
        if config['ports']['issuer']!=8118 or config['ports']['guest']!=8132:raise ValueError('Installed guest operator currently requires issuer8118 and guest8132')
        who=pwd.getpwnam('codi-guest')
        if who.pw_uid!=c['frontendUID'] or who.pw_gid!=c['pingGID']:raise ValueError('Native guest service identity differs from worker binding')
        expected=json.loads(op.read_owned(Path(config['stateRoot'])/'public/origin-discovery.json',0,0o444))['identity']
        if c['issuerPolicy']!=expected:raise ValueError('Guest backend issuer keys differ from native public pin')
        if Path(value['frontendFile'])!=Path(value['configFile']).parent/'frontend.json':raise ValueError('Fixed frontend descriptor location required')
        self.descriptor={'version':FRONTEND_VERSION,'origin':c['origin'],'basePath':c['basePath'],'policy':c['policy'],'policySHA256':c['policySHA256'],'issuerPolicy':expected,'frontendUID':who.pw_uid,'frontendGID':who.pw_gid,'workerSockets':{role:'/run/codi-network/'+c['instance']+'/'+role+'.sock' for role in ['anonymous','registered']},'guardUnit':c['instance']+'-guard.service'}
        validate_descriptor(self.descriptor)
        if sha(encoded(self.descriptor))!=value['frontendSHA256']:raise ValueError('Derived frontend descriptor pin differs')
    def run(self,action):
        if action not in ('status','start','stop','recover'):raise ValueError('Explicit guest operator action required')
        seal(self.op,Path(self.value['operatorRelease']),self.value['operatorManifestSHA256'])
        if sha(self.op.read_owned(self.op.path(self.value['configFile']),0,0o600))!=self.value['configSHA256']:raise ValueError('Guest backend changed before execution')
        # Never import this release's guest_service into the native namespace.
        args=[self.config['python'],'-I','-B',str(Path(self.value['operatorRelease'])/'scripts/manage-guest-network.py'),action,'--config-dir',str(Path(self.value['configFile']).parent)]
        result=subprocess.run(args,capture_output=True,text=True,timeout=120,env={k:v for k,v in os.environ.items() if k not in ('NOTIFY_SOCKET','PYTHONPATH','PYTHONHOME')})
        if result.returncode:raise ValueError('Guest operator '+action+' failed: '+result.stderr[-1500:])
        if len(result.stdout)>65536:raise ValueError('Bounded guest operator response required')
        value=json.loads(result.stdout)
        if not isinstance(value,dict) or not isinstance(value.get('status'),str):raise ValueError('Malformed guest operator response')
        return value
    def ensure_descriptor(self):
        file=self.op.path(self.value['frontendFile']);raw=encoded(self.descriptor)
        if file.exists():
            if self.op.read_owned(file,0,0o644)!=raw:raise ValueError('Existing guest frontend descriptor differs; explicit migration required')
        else:self.op.atomic(file,raw,0o644)
    def healthy(self):
        value=self.run('status')
        if value.get('status')!='inspected' or not value.get('active') or value.get('guardFault') or not value.get('kernelMatches') or value.get('bootEnabled') is not False:raise ValueError('Guest backend guard/kernel not ready')
        expected={self.backend['instance']+'-guard.service',*(self.backend['instance']+'-'+role+'.'+suffix for role in ['anonymous','registered'] for suffix in ['service','socket'])}
        if set(value.get('units',{}))!=expected:raise ValueError('Guest backend unit set changed')
        for name,state in value['units'].items():
            if state['ActiveState']!='active' or state['UnitFileState']!='static' or name.endswith('.service') and int(state['MainPID'])<=0:raise ValueError('Guest backend unit not ready')
        return value

def validate(op,config,read_inputs=True):
    value=config.get('guestNetwork')
    if value is None:
        if config.get('version')==VERSION:raise ValueError('Schema5 requires an explicit guest backend')
        return
    if config.get('version')!=VERSION or not isinstance(value,dict) or set(value)!=FIELDS:raise ValueError('Exact native guest backend pins required')
    for key in ['configSHA256','operatorManifestSHA256','frontendSHA256','policySHA256']:
        if not isinstance(value[key],str) or not re.fullmatch('[0-9a-f]{64}',value[key]):raise ValueError('Exact guest backend SHA256 pins required')
    for key in ['configFile','operatorRelease','frontendFile']:
        file=op.path(value[key])
        if any(file.is_relative_to(Path(base)) for base in ['/home','/root','/tmp','/var/tmp','/run']):raise ValueError('Guest backend requires persistent protected paths')
    if not read_inputs:return
    binding=Binding(op,config,value)
    if op.read_owned(op.path(value['frontendFile']),0,0o644)!=encoded(binding.descriptor):raise ValueError('Guest frontend descriptor changed')
    result=binding.run('status')
    if result['status'] not in ('inspected','pending'):raise ValueError('Guest operator status unavailable')
    return binding

def policy(op,config,config_file,operator):
    file=op.path(config_file);folder=op.path(operator);raw=op.read_owned(file,0,0o600);backend=json.loads(raw)
    value={'configFile':str(file),'configSHA256':sha(raw),'operatorRelease':str(folder),'operatorManifestSHA256':sha(op.read_owned(folder/'guest-operator.json',0,0o644)),'frontendFile':str(file.parent/'frontend.json'),'frontendSHA256':'0'*64,'policySHA256':backend['policySHA256']}
    who=pwd.getpwnam('codi-guest')
    descriptor={'version':FRONTEND_VERSION,'origin':backend['origin'],'basePath':backend['basePath'],'policy':backend['policy'],'policySHA256':backend['policySHA256'],'issuerPolicy':backend['issuerPolicy'],'frontendUID':who.pw_uid,'frontendGID':who.pw_gid,'workerSockets':{role:'/run/codi-network/'+backend['instance']+'/'+role+'.sock' for role in ['anonymous','registered']},'guardUnit':backend['instance']+'-guard.service'}
    value['frontendSHA256']=sha(encoded(descriptor));validate(op,{**config,'version':VERSION,'guestNetwork':value},read_inputs=False)
    Binding(op,config,value)
    return value

def start_backend(op,config):
    if config.get('guestNetwork'):
        binding=validate(op,config);binding.run('recover');binding.run('start');binding.healthy()
def stop_backend(op,config):
    if config.get('guestNetwork'):
        binding=Binding(op,config,config['guestNetwork']);binding.run('recover');binding.run('stop')
def require_stopped(op,config):
    if config.get('guestNetwork'):
        binding=Binding(op,config,config['guestNetwork']);value=binding.run('status')
        if value.get('status')!='inspected' or value.get('active') or value.get('guardFault') or value.get('kernelMatches') or any(s['ActiveState'] not in ('inactive','failed') or int(s.get('MainPID','0')) for s in value['units'].values()):raise ValueError('Stop native guest and its backend before restoring account state')

def ready(op,config,roles):
    if not config.get('guestNetwork'):
        if 'issuer' in roles and op.issuer_config(config).get('guestNetwork') is not None:raise ValueError('Issuer still advertises disabled guest grants')
        return
    expected=metadata(config['basePath'],config['guestNetwork']['policySHA256'])
    if 'issuer' in roles and op.issuer_config(config).get('guestNetwork')!=expected:raise ValueError('Issuer guest policy differs from managed pins')
    if 'guest' in roles:
        validate(op,config).healthy()
        request=urllib.request.Request('http://127.0.0.1:'+str(config['ports']['guest'])+'/config.json',headers={'Host':urlsplit(config['origin']).netloc})
        with urllib.request.urlopen(request,timeout=3) as response:raw=response.read(65537)
        if len(raw)>65536:raise ValueError('Bounded guest public configuration required')
        public=json.loads(raw);network=public.get('guestNetwork',{})
        if public.get('identity')!=json.loads(op.read_owned(Path(config['stateRoot'])/'public/origin-discovery.json',0,0o444))['identity'] or network.get('authorization')!=expected['authorization'] or network.get('relayPath')!=expected['relayPath'] or network.get('durableAccountLimits') is not True:raise ValueError('Guest frontend policy differs from native pins')

def validate_pair(op,current,before,after):
    allowed={'codi-managed-instance/'+str(n) for n in [2,3,4,5]}
    if current not in (before,after) or before.get('version') not in allowed or after.get('version') not in allowed or before.get('maintenance')!=1 or after.get('maintenance')!=1:raise ValueError('Guest changes require checkpointed native metadata')
    stable=lambda c:{**{k:v for k,v in c.items() if k not in ('version','guestNetwork','turn')},'turn':c.get('turn')}
    if stable(before)!=stable(after):raise ValueError('Guest policy cannot change code, identity, files, TURN, mount or ports')
    if before.get('guestNetwork') and after.get('guestNetwork') and before['guestNetwork']!=after['guestNetwork']:raise ValueError('Disable guest policy before changing backend installation')
    for c in (before,after):validate(op,c,read_inputs=False)
def history(op,config,config_path):
    file=slot(config_path,'network-history.json')
    if not file.exists():return {'version':'codi-network-history/1','instance':config['instance'],'entries':[]}
    value=json.loads(op.read_owned(file,0,0o600))
    if set(value)!={'version','instance','entries'} or value['version']!='codi-network-history/1' or value['instance']!=config['instance'] or not isinstance(value['entries'],list) or len(value['entries'])>16:raise ValueError('Invalid guest policy history')
    return value
def committed(op,config,config_path,journal):return any(e['id']==journal['id'] and e['outcome']=='applied' for e in history(op,config,config_path)['entries'])
def record(op,config,config_path,journal,outcome):
    value=history(op,config,config_path);entry={k:journal[k] for k in ['id','before','after','activeRoles']};entry.update(outcome=outcome,completed=int(time.time()))
    value['entries']=[old for old in value['entries'] if old['id']!=entry['id']]+[entry];value['entries']=value['entries'][-16:];write(op,slot(config_path,'network-history.json'),value)
def clear(config_path):slot(config_path,'maintenance.json').unlink();maintenance.sync_directory(Path(config_path).parent)
def apply(op,config,config_path):
    for role in ROLES:op.atomic(Path(config['unitDir'])/op.unit(config,role),op.render(config,role),0o644)
    write(op,config_path,config);op.systemctl('daemon-reload')
def start(op,config,roles,config_path):
    maintenance.guard_epoch(op,config,config_path)
    if 'guest' in roles:start_backend(op,config)
    for role in roles:
        if op.systemctl('show',op.unit(config,role),'-p','ActiveState','--value').strip()=='failed':op.systemctl('reset-failed',op.unit(config,role))
        op.systemctl('start',op.unit(config,role));op.ready(config,[role])
    if 'issuer' in roles:
        expected=json.loads(op.read_owned(Path(config['stateRoot'])/'public/origin-discovery.json',0,0o444))['identity']
        if op.issuer_config(config)['identity']!=expected:raise ValueError('Issuer identity changed during guest transition')
def restore_target(op,config_path,journal,target):
    # First stop frontend regardless of which metadata reached disk. Then settle
    # the external journal and remove the owned kernel policy before legacy NAT.
    op.stop(target,['guest','issuer'])
    enabled=journal['after'] if journal['after'].get('guestNetwork') else journal['before']
    stop_backend(op,enabled)
    apply(op,target,config_path);start(op,target,journal['activeRoles'],config_path)
def revert(op,config_path,journal):
    before=journal['before'];op.installed(before);journal['phase']='rolling-back';write(op,slot(config_path,'maintenance.json'),journal)
    restore_target(op,config_path,journal,before);record(op,before,config_path,journal,'reverted');clear(config_path)
    return {'status':'network-failed-rolled-back','id':journal['id'],'dataRestored':False}
def configure(op,config,config_path,value):
    maintenance.require_clean(op,config_path);maintenance.guard(op,config,config_path)
    if value is None:
        if not config.get('guestNetwork'):return {'status':'network-already-current','enabled':False}
        after={k:v for k,v in config.items() if k!='guestNetwork'};after['version']='codi-managed-instance/4' if after.get('userFiles') else 'codi-managed-instance/3'
    else:after={**config,'version':VERSION,'turn':config.get('turn'),'guestNetwork':value}
    validate_pair(op,config,config,after)
    if after==config:validate(op,after);return {'status':'network-already-current','enabled':True}
    if value is not None:
        binding=Binding(op,after,value);status=binding.run('status')
        if status.get('status')!='inspected' or status.get('active') or status.get('guardFault') or status.get('kernelMatches'):raise ValueError('New guest backend must be cleanly stopped before native enablement')
        # Creating an unreferenced public descriptor changes no live policy.
        # Existing files are never silently overwritten, including on failure.
        binding.ensure_descriptor()
    op.installed(after);deployment.syntax(op,after,config_path)
    selected=deployment.active(op,config);roles=[role for role in ROLES if role in selected]
    journal={'version':JOURNAL,'id':secrets.token_hex(16),'phase':'prepared','before':config,'after':after,'activeRoles':roles,'created':int(time.time())}
    write(op,slot(config_path,'maintenance.json'),journal)
    try:
        journal['phase']='stopping';write(op,slot(config_path,'maintenance.json'),journal);op.stop(config,['guest','issuer'])
        journal['phase']='switching';write(op,slot(config_path,'maintenance.json'),journal);apply(op,after,config_path)
        journal['phase']='starting';write(op,slot(config_path,'maintenance.json'),journal);start(op,after,roles,config_path)
        record(op,after,config_path,journal,'applied');clear(config_path)
        return {'status':'network-configured','id':journal['id'],'enabled':value is not None,'activeRoles':roles,'stewardRestarted':False,'dataRestored':False}
    except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:
        if committed(op,after,config_path,journal):raise ValueError('Guest policy committed; finish recover-operation') from error
        try:return revert(op,config_path,journal)
        except (OSError,ValueError,subprocess.SubprocessError) as failure:raise ValueError('Guest policy rollback incomplete; retain journal and recover-operation: '+str(failure)) from failure
def recover(op,config,config_path):
    journal=json.loads(op.read_owned(slot(config_path,'maintenance.json'),0,0o600))
    if not isinstance(journal,dict) or set(journal)!={'version','id','phase','before','after','activeRoles','created'} or journal['version']!=JOURNAL or journal['phase'] not in ('prepared','stopping','switching','starting','rolling-back') or journal['activeRoles'] not in ([],['issuer'],['guest'],ROLES) or not re.fullmatch('[0-9a-f]{32}',journal['id']):raise ValueError('Invalid guest transition journal')
    validate_pair(op,config,journal['before'],journal['after'])
    if not committed(op,config,config_path,journal):
        result=revert(op,config_path,journal);result['status']='interrupted-network-rolled-back';return result
    after=journal['after'];op.installed(after)
    healthy=config==after
    if healthy:
        try:
            for role in ROLES:
                if op.read_owned(Path(after['unitDir'])/op.unit(after,role),0,0o644)!=op.render(after,role):raise ValueError('Native guest unit changed')
                fields=dict(line.split('=',1) for line in op.systemctl('show',op.unit(after,role),'-p','ActiveState','-p','MainPID').splitlines())
                if role in journal['activeRoles']:
                    if fields['ActiveState']!='active' or int(fields['MainPID'])<=0:raise ValueError('Committed native role not running')
                elif fields['ActiveState'] not in ('inactive','failed') or int(fields['MainPID']):raise ValueError('Unexpected active native role')
            op.ready(after,journal['activeRoles'])
            enabled=after if after.get('guestNetwork') else journal['before']
            if not after.get('guestNetwork') or 'guest' not in journal['activeRoles']:require_stopped(op,enabled)
        except (OSError,ValueError,KeyError,subprocess.SubprocessError):healthy=False
    if not healthy:restore_target(op,config_path,journal,after)
    clear(config_path)
    return {'status':'committed-network-recovered','id':journal['id'],'dataRestored':False}
