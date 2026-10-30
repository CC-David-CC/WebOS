#!/usr/bin/env python3
"""Root-only composition of existing native binding and room-code transactions.

The backend is a separately usable checkpoint: finish/recover it before updating
frontend/native code. Uncommitted recovery selects the original worker/binding;
committed recovery keeps the new worker/binding. Never restore user data or mint
an authority. The caller holds the hosting controller lock on production.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import time

OPERATOR_FILES={'file_service/__init__.py','file_service/operator.py','room_service/__init__.py','room_service/operator.py','scripts/manage-hosted-rooms.py'}
VERSION='codi-reader-backend-transition/1'
PHASES=['prepared','unbound','worker','bound','committed']

def require(ok,message):
    if not ok:raise ValueError(message)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def protected(path):
    path=Path(path);require(path.is_absolute() and '..' not in path.parts,'Absolute protected path required')
    for p in [path,*path.parents]:
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'Root-owned immutable path required')
    return path

def graph(folder,manifest,pin,roster=None):
    folder=protected(folder);p=protected(folder/manifest);require(p.stat().st_size<=4*1048576,'Bounded manifest required');raw=p.read_bytes();require(digest(raw)==pin,'Immutable artifact pin differs')
    m=json.loads(raw);require(isinstance(m,dict) and isinstance(m.get('files'),dict),'Artifact records required');files=m['files']
    if roster is not None:require(set(files)==roster and m.get('version')=='codi-hosted-room-operator/1','Closed format1 operator graph required')
    require({str(p.relative_to(folder))for p in folder.rglob('*')if not p.is_dir()}==set(files)|{manifest},'Artifact has missing or extra files')
    for p in [folder,*folder.rglob('*')]:
        protected(p);s=p.stat();require(stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode),'Regular code graph required')
        if p.is_file():
            require(s.st_nlink==1,'No hard-linked code files')
            if p.name!=manifest:require(files[str(p.relative_to(folder))]=={'bytes':s.st_size,'sha256':digest(p.read_bytes())},'Artifact source differs')
    return m

class Transition:
    def __init__(self,control,room_config,operator,operator_pin,native,native_pin):
        require(os.geteuid()==0,'Root transition required')
        self.control=protected(control);self.room_config=protected(room_config);self.operator=Path(operator);self.native=Path(native)
        graph(self.operator,'room-operator.json',operator_pin,OPERATOR_FILES);self.native_manifest=graph(self.native,'connected-release.json',native_pin)
        self.operator_pin=operator_pin;self.native_pin=native_pin
        spec=importlib.util.spec_from_file_location('_reader_transition_operator_'+operator_pin,self.operator/'room_service/operator.py');self.op=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.op)
        self.safe=self.op.safe;self.manager=self.op.Manager(self.room_config.parent);self.journal=self.control.parent/'reader-backend-transition.json'
        self.lockfile=self.control.parent/'.reader-backend.lock'
        c=self.read_native();self.python=c['python'];self.safe.verify_python(self.python,self.native)

    def read_native(self):
        c=json.loads(self.safe.read(self.control))
        require(c.get('version')=='codi-managed-instance/5' and isinstance(c.get('instance'),str),'Managed native5 context required')
        return c

    @contextmanager
    def locked(self):
        fd=os.open(self.lockfile,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:
            self.safe.protected(self.lockfile,mode=0o600)
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise ValueError('Another reader backend transition holds the lock') from None
            yield
        finally:os.close(fd)

    def cli(self,action,*args):
        p=subprocess.run([self.python,'-I','-B',str(self.native/'scripts/manage-services.py'),action,'--config',str(self.control),*map(str,args)],capture_output=True,text=True,timeout=240)
        if p.returncode:raise ValueError('Native '+action+' refused: '+p.stderr[-2000:])
        return json.loads(p.stdout)

    def room(self):
        with self.manager.locked():c=self.manager.load();return c,self.manager.inspect(c)

    def binding(self,c,operator):
        return {'configFile':str(self.room_config),'configSHA256':digest((json.dumps(c,sort_keys=True,indent=2)+'\n').encode()),'operatorRelease':str(operator),'operatorManifestSHA256':digest((Path(operator)/'room-operator.json').read_bytes())}

    def same_native(self,j):
        current=self.read_native();stable=lambda c:{k:v for k,v in c.items()if k!='hostedRooms'}
        require(stable(current)==stable(j['native']),'Unrelated native configuration changed')
        allowed=[None,j['native'].get('hostedRooms'),self.binding(j['target'],j['bindingOperator'])]
        require(current.get('hostedRooms') in allowed,'Unrelated room binding changed')
        return current

    def pending(self,j):
        raw=(json.dumps(j,sort_keys=True,indent=2)+'\n').encode();require(len(raw)<=4*1048576,'Bounded transition journal required');self.safe.atomic(self.journal,raw)

    def validate(self,j,previous_controller=None):
        fields={'version','id','phase','created','native','before','target','baseline','bindingOperator','bindingOperatorPin','operatorPin','controllerPin'}
        require(set(j)==fields and j['version']==VERSION and re.fullmatch('[a-f0-9]{32}',j['id']) and j['phase'] in PHASES,'Invalid reader backend journal')
        require(j['operatorPin']==self.operator_pin,'Recovery operator pin differs')
        if j['controllerPin']!=self.native_pin:
            require(previous_controller is not None,'Recovery controller pin differs')
            folder,pin=previous_controller
            require(pin==j['controllerPin'],'Previous recovery controller pin differs')
            old=graph(Path(folder),'connected-release.json',pin)
            require(old['version']=='codi-connected-development/23' and self.native_manifest['version']=='codi-connected-development/24','Only explicit23-to24 history-repair recovery supported')
            allowed={'origin_service/release.py','origin_service/deployment.py','origin_service/turn_management.py','origin_service/room_management.py','scripts/manage-services.py'}
            require(set(old['files'])==set(self.native_manifest['files']) and {n for n,v in old['files'].items()if self.native_manifest['files'][n]!=v}==allowed,'Recovery controller changed unrelated code or public assets')
        self.manager.code_pair(j['before'],j['target']);self.same_native(j)
        graph(Path(j['bindingOperator']),'room-operator.json',j['bindingOperatorPin'],OPERATOR_FILES)
        # Original binding was captured only after the exact backend was verified.
        old=j['native'].get('hostedRooms');require(old and old['configFile']==str(self.room_config),'Original backend binding required')
        graph(Path(old['operatorRelease']),'room-operator.json',old['operatorManifestSHA256'],OPERATOR_FILES)
        require(old==self.binding(j['before'],old['operatorRelease']),'Original binding no longer matches retained worker configuration')

    def clean(self):
        require(not (self.control.parent/'maintenance.json').exists() and not (self.control.parent/'native-rollout.json').exists() and not (self.control.parent/'site-cutover.json').exists() and not self.manager.journal.exists(),'Recover existing native/room operation before starting')

    def checked(self,j,target,binding_operator):
        c,state=self.room();require(c==target and self.op.retained(j['baseline'],state),'Current room history or replay floor regressed')
        require(self.same_native(j).get('hostedRooms')==self.binding(c,binding_operator),'Expected exact native room binding required')
        health=self.manager.health(c);require(health['status']=='PASS','Room readiness required');self.cli('status')
        return health

    def select(self,j,target,binding_operator,phase=lambda _:None):
        self.same_native(j)
        current,_=self.room()
        if current==target and self.read_native().get('hostedRooms')==self.binding(target,binding_operator):
            return self.checked(j,target,binding_operator)
        if self.read_native().get('hostedRooms'):
            v=self.cli('configure-hosted-rooms','--disable');require(v['status']=='rooms-configured','Explicit room unbind failed')
        phase('unbound')
        c,_=self.room()
        require(c in [j['before'],j['target']],'Room config differs from both candidates')
        if c!=target:self.manager.upgrade_code(Path(target['release']),target['manifestSHA256'],self.control,phase=lambda n:phase('inner-worker:'+n))
        phase('worker')
        v=self.cli('configure-hosted-rooms','--room-config',self.room_config,'--room-operator',binding_operator)
        require(v['status'] in ['rooms-configured','rooms-already-current'],'Room rebind failed');phase('bound')
        return self.checked(j,target,binding_operator)

    def apply(self,worker,pin,binding_operator=None,binding_pin=None,*,phase=lambda _:None):
        with self.locked():
            require(not self.journal.exists(),'Pending reader backend transition requires explicit recovery');self.clean()
            native=self.read_native();before,baseline=self.room();require(native.get('hostedRooms')==self.binding(before,native.get('hostedRooms',{}).get('operatorRelease','/missing')),'Existing exact hosted binding required')
            target={**before,'release':str(Path(worker)),'manifestSHA256':pin};self.manager.code_pair(before,target)
            binding_operator=Path(binding_operator or self.operator)
            if binding_pin is None:require(binding_operator==self.operator,'Explicit alternate binding operator pin required');binding_pin=self.operator_pin
            graph(binding_operator,'room-operator.json',binding_pin,OPERATOR_FILES)
            if target==before and native['hostedRooms']==self.binding(target,binding_operator):
                return {'status':'reader-backend-already-current','servicesRestarted':False,'dataRestored':False,'manifestSHA256':pin}
            j={'version':VERSION,'id':secrets.token_hex(16),'phase':'prepared','created':int(time.time()),'native':native,'before':before,'target':target,'baseline':baseline,'bindingOperator':str(binding_operator),'bindingOperatorPin':binding_pin,'operatorPin':self.operator_pin,'controllerPin':self.native_pin}
            self.validate(j);self.pending(j);phase('prepared')
            def checkpoint(name):
                if name in PHASES:j['phase']=name;self.pending(j)
                phase(name)
            health=self.select(j,target,binding_operator,checkpoint);checkpoint('committed')
            self.journal.unlink();self.safe.sync(self.journal.parent)
            return {'status':'reader-backend-upgraded','id':j['id'],'manifestSHA256':pin,'roomHealth':health,'dataRestored':False,'rootMinted':False,'bootEnabled':False}

    def recover(self,*,phase=lambda _:None,previous_controller=None):
        with self.locked():
            j=json.loads(self.safe.read(self.journal,maximum=4*1048576));self.validate(j,previous_controller)
            # Recover each inner journal using its own established commit policy.
            if (self.control.parent/'maintenance.json').exists():
                inner=json.loads(self.safe.read(self.control.parent/'maintenance.json',maximum=4*1048576));require(inner.get('version')=='codi-hosted-rooms-transition/1','Unrelated native recovery refused');self.cli('recover-operation')
            if self.manager.journal.exists():self.manager.recover_code()
            self.clean();committed=j['phase']=='committed';target=j['target'] if committed else j['before'];binding=Path(j['bindingOperator']) if committed else Path(j['native']['hostedRooms']['operatorRelease'])
            health=self.select(j,target,binding,phase)
            self.journal.unlink();self.safe.sync(self.journal.parent)
            return {'status':'committed-reader-backend-recovered' if committed else 'interrupted-reader-backend-reverted','id':j['id'],'manifestSHA256':target['manifestSHA256'],'roomHealth':health,'dataRestored':False,'rootMinted':False,'bootEnabled':False,'originalControllerPin':j['controllerPin'],'recoveryControllerPin':self.native_pin}
