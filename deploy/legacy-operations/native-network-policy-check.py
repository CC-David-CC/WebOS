#!/usr/bin/env python3
"""Native network transition fault/order tests with durable fixture journals.

External operator/kernel/systemd effects are modeled here; actual installed
worker/credential/browser proofs are separate. No live services are changed.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service import network_management as network,files_management,turn_management,maintenance
from guest_service.runtime import metadata
spec=importlib.util.spec_from_file_location('native_network_operator',ROOT/'scripts/manage-services.py');native=importlib.util.module_from_spec(spec);sys.modules[spec.name]=native;spec.loader.exec_module(native)

class Crash(BaseException):pass

class Op:
    ROLES=('issuer','steward','guest')
    def __init__(self,folder):
        self.folder=folder;folder.mkdir();self.config_path=folder/'managed.json';self.events=[];self.crash=None;self.failure=None;self.kernel=False;self.workers=False;self.unknown=False;self.serial=20
        self.roles={'issuer':11,'guest':12,'steward':13,'issuer-bootstrap':0}
        self.before={'version':'codi-managed-instance/4','maintenance':1,'instance':'codi-fixture','authorityClass':'development','release':'/srv/native12','python':'/srv/venv/bin/python','manifestSHA256':'a'*64,'stateRoot':str(folder/'state'),'unitDir':str(folder/'units'),'origin':'https://fixture.invalid','basePath':'/hidden','ports':{'issuer':8118,'steward':8119,'guest':8132},'turn':None,'userFiles':{'configFile':'/etc/files/managed.json','configSHA256':'1'*64,'operatorRelease':'/srv/files/operator','operatorManifestSHA256':'2'*64}}
        self.value={'configFile':'/etc/guest/managed.json','configSHA256':'3'*64,'operatorRelease':'/srv/guest/operator','operatorManifestSHA256':'4'*64,'frontendFile':'/etc/guest/frontend.json','frontendSHA256':'5'*64,'policySHA256':'6'*64}
        self.config_path.write_text(json.dumps(self.before));(folder/'units').mkdir();(folder/'state').mkdir();(folder/'state/public').mkdir()
        self.identity={'mode':'server','issuer':'https://fixture.invalid'};(folder/'state/public/origin-discovery.json').write_text(json.dumps({'identity':self.identity}))
        self.data=folder/'state/preserved-account-file-and-counter';self.data.write_bytes(b'account-key-files-and-usage-must-survive')
    def event(self,name):
        self.events.append(name)
        if name==self.crash:self.crash=None;raise Crash(name)
        if name==self.failure:self.failure=None;raise ValueError('Injected readiness failure '+name)
    def current(self):return json.loads(self.config_path.read_text())
    def path(self,value):return Path(value)
    def read_owned(self,file,*args):
        if str(file)==self.value['frontendFile']:return network.encoded({})
        return Path(file).read_bytes()
    def atomic(self,file,raw,mode=0o600):
        file=Path(file);file.write_bytes(raw);file.chmod(mode)
        if file.name=='maintenance.json':self.event('journal:'+json.loads(raw)['phase'])
        elif file==self.config_path:self.event('config:'+('on' if json.loads(raw).get('guestNetwork') else 'off'))
    def unit(self,config,role):return config['instance']+'-'+role+'.service'
    def installed(self,config):
        if config.get('guestNetwork') and config['release']=='/srv/native11':raise ValueError('Disable guest policy before rolling code back below profile12')
        self.event('installed:'+('on' if config.get('guestNetwork') else 'off'))
    def render(self,config,role):return network.encoded({'role':role,'network':bool(config.get('guestNetwork'))})
    def issuer_config(self,config):return {'identity':self.identity,**({'guestNetwork':metadata(config['basePath'],config['guestNetwork']['policySHA256'])} if config.get('guestNetwork') else {})}
    def ready(self,config,roles):
        for role in roles:self.event('ready:'+role+':'+('on' if config.get('guestNetwork') else 'off'))
    def systemctl(self,action,*args):
        if action in ('daemon-reload','reset-failed'):return ''
        role=next(role for role in self.roles if args[0]==self.unit(self.before,role))
        if action=='show':
            state='active' if self.roles[role] else 'inactive'
            if '--value' in args:return state
            return 'MainPID='+str(self.roles[role])+'\nActiveState='+state
        if action=='start':
            if role=='guest':
                desired=bool(self.current().get('guestNetwork'));assert self.kernel==desired,'Wrong firewall state before frontend starts'
                if desired:assert self.workers,'Frontend started before private workers'
            self.event('start:'+role+':'+('on' if self.current().get('guestNetwork') else 'off'));self.serial+=1;self.roles[role]=self.serial
        return ''
    def stop(self,config,roles):
        for role in roles:self.roles[role]=0;self.event('stop:'+role)
        if 'guest' in roles and config.get('guestNetwork'):network.stop_backend(self,config)

class Binding:
    def __init__(self,op,config,value):self.op=op;self.config=config;self.value=value;self.descriptor={}
    def ensure_descriptor(self):self.op.event('descriptor:prepared')
    def healthy(self):assert self.op.kernel and self.op.workers;return {}
    def run(self,action):
        self.op.event('backend:'+action)
        if action=='status':return {'status':'inspected','active':self.op.kernel,'guardFault':False,'kernelMatches':self.op.kernel,'bootEnabled':False,'units':{}}
        if action=='start':
            if self.op.kernel and self.op.workers:return {'status':'already-started'}
            assert not self.op.roles['guest'],'Filtering a running legacy frontend'
            self.op.kernel=True;self.op.event('kernel:installed');self.op.workers=True;self.op.event('workers:started')
        if action=='stop':
            assert not self.op.roles['guest'],'Removing filtering while frontend runs'
            if self.op.unknown:raise ValueError('Unknown firewall retained')
            self.op.workers=False;self.op.event('workers:stopped');self.op.kernel=False;self.op.event('kernel:removed')
        return {'status':action}

class Transitions(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-network-order-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.op=Op(self.root/'fixture')
        for target,value in [('Binding',Binding)]:self.enterContext(patch.object(network,target,value))
        self.enterContext(patch.object(maintenance,'guard',lambda *a:None));self.enterContext(patch.object(maintenance,'guard_epoch',lambda *a:None));self.enterContext(patch.object(network.deployment,'syntax',lambda *a:None))
    def enable(self):return network.configure(self.op,self.op.current(),self.op.config_path,self.op.value)
    def disable(self):return network.configure(self.op,self.op.current(),self.op.config_path,None)
    def preserved(self):self.assertEqual(self.op.data.read_bytes(),b'account-key-files-and-usage-must-survive');self.assertEqual(self.op.roles['steward'],13)
    def test_enable_stops_legacy_before_filter_and_preserves_other_services(self):
        self.assertEqual(self.enable()['status'],'network-configured');self.assertEqual(self.op.current()['version'],network.VERSION);self.assertTrue(self.op.kernel and self.op.workers)
        self.assertLess(self.op.events.index('stop:guest'),self.op.events.index('kernel:installed'));self.assertLess(self.op.events.index('workers:started'),self.op.events.index('start:guest:on'));self.preserved()
    def test_disable_removes_kernel_before_old_same_uid_nat_can_start(self):
        self.enable();self.op.events=[];self.assertEqual(self.disable()['status'],'network-configured');self.assertFalse(self.op.kernel or self.op.workers);self.assertEqual(self.op.current(),self.op.before)
        self.assertLess(self.op.events.index('stop:guest'),self.op.events.index('kernel:removed'));self.assertLess(self.op.events.index('kernel:removed'),self.op.events.index('start:guest:off'));self.preserved()
    def test_noop_does_not_restart_or_reset(self):
        self.enable();before=copy.deepcopy(self.op.roles);self.assertEqual(self.enable()['status'],'network-already-current');self.assertEqual(before,self.op.roles)
        self.disable();before=copy.deepcopy(self.op.roles);self.assertEqual(self.disable()['status'],'network-already-current');self.assertEqual(before,self.op.roles);self.preserved()
    def test_enable_preflight_refuses_already_active_backend_without_stopping_frontend(self):
        self.op.kernel=True;before=copy.deepcopy(self.op.roles)
        with self.assertRaisesRegex(ValueError,'cleanly stopped'):self.enable()
        self.assertEqual(before,self.op.roles);self.assertFalse(network.slot(self.op.config_path,'maintenance.json').exists())
    def test_worker_or_native_readiness_failure_rolls_back_without_resetting_data(self):
        for i,event in enumerate(['kernel:installed','workers:started','ready:issuer:on','ready:guest:on']):
            with self.subTest(event=event):
                self.op=Op(self.root/('failed-'+str(i)));self.op.failure=event;self.assertEqual(self.enable()['status'],'network-failed-rolled-back');self.assertEqual(self.op.current(),self.op.before);self.assertFalse(self.op.kernel or self.op.workers);self.assertGreater(self.op.roles['guest'],0);self.preserved()
    def test_disable_legacy_failure_restores_controlled_backend(self):
        self.enable();self.op.failure='ready:guest:off';self.assertEqual(self.disable()['status'],'network-failed-rolled-back');self.assertTrue(self.op.kernel and self.op.workers);self.assertEqual(self.op.current()['version'],network.VERSION);self.preserved()
    def test_interruption_at_each_enable_boundary_recovers_old_mode(self):
        for i,event in enumerate(['journal:prepared','journal:stopping','journal:switching','config:on','journal:starting','kernel:installed','workers:started','start:issuer:on','start:guest:on']):
            with self.subTest(event=event):
                self.op=Op(self.root/('crash-'+str(i)));self.op.crash=event
                with self.assertRaises(Crash):self.enable()
                self.assertTrue(network.slot(self.op.config_path,'maintenance.json').exists());result=network.recover(self.op,self.op.current(),self.op.config_path)
                self.assertEqual(result['status'],'interrupted-network-rolled-back');self.assertEqual(self.op.current(),self.op.before);self.assertFalse(self.op.kernel or self.op.workers);self.preserved()
    def test_interrupted_disable_recovers_registered_policy(self):
        self.enable();self.op.crash='config:off'
        with self.assertRaises(Crash):self.disable()
        self.assertEqual(network.recover(self.op,self.op.current(),self.op.config_path)['status'],'interrupted-network-rolled-back');self.assertTrue(self.op.kernel and self.op.workers);self.preserved()
    def test_commit_point_retains_new_mode_when_clearing_journal_fails(self):
        with patch.object(network,'clear',side_effect=OSError('disk failure')):
            with self.assertRaisesRegex(ValueError,'committed'):self.enable()
        pids=copy.deepcopy(self.op.roles);self.op.events=[]
        self.assertEqual(network.recover(self.op,self.op.current(),self.op.config_path)['status'],'committed-network-recovered');self.assertTrue(self.op.kernel and self.op.workers);self.assertEqual(self.op.roles,pids);self.assertNotIn('stop:guest',self.op.events);self.preserved()
    def test_committed_disable_recovery_never_reinstates_old_policy(self):
        self.enable()
        with patch.object(network,'clear',side_effect=OSError('disk failure')):
            with self.assertRaisesRegex(ValueError,'committed'):self.disable()
        self.assertEqual(network.recover(self.op,self.op.current(),self.op.config_path)['status'],'committed-network-recovered');self.assertFalse(self.op.kernel or self.op.workers);self.assertEqual(self.op.current(),self.op.before);self.preserved()
    def test_unknown_firewall_blocks_old_relay_restart_and_retains_journal(self):
        self.enable();self.op.unknown=True
        with self.assertRaisesRegex(ValueError,'rollback incomplete'):self.disable()
        self.assertEqual(self.op.roles['guest'],0);self.assertTrue(self.op.kernel);self.assertTrue(network.slot(self.op.config_path,'maintenance.json').exists());self.preserved()
    def test_configuring_stopped_roles_does_not_start_them(self):
        self.op.roles['issuer']=self.op.roles['guest']=0;self.enable();self.assertFalse(self.op.kernel or self.op.workers);self.assertEqual(self.op.roles['guest'],0);self.assertEqual(self.op.roles['issuer'],0);self.preserved()
    def test_issuer_only_transition_does_not_activate_worker_policy(self):
        self.op.roles['guest']=0;self.enable();self.assertFalse(self.op.kernel);self.assertGreater(self.op.roles['issuer'],0);self.preserved()
    def test_pending_native_journal_blocks_another_transition(self):
        self.op.crash='journal:prepared'
        with self.assertRaises(Crash):self.enable()
        with self.assertRaises(ValueError):self.enable()
    def test_schema2_enable_adds_disabled_turn_and_disable_remains_downgrade_compatible(self):
        config=self.op.current();config.pop('turn');config.pop('userFiles');config['version']='codi-managed-instance/2';self.op.config_path.write_text(json.dumps(config));self.enable();self.assertIsNone(self.op.current()['turn']);self.disable();self.assertEqual(self.op.current()['version'],'codi-managed-instance/3');self.assertNotIn('userFiles',self.op.current());self.preserved()
    def test_guest_transition_cannot_modify_unrelated_fields_or_swap_live_backend(self):
        before=self.op.current();after={**before,'version':network.VERSION,'guestNetwork':self.op.value}
        for key in ['origin','basePath','ports','stateRoot','release','python','userFiles','turn']:
            changed=copy.deepcopy(after);changed[key]='changed'
            with self.subTest(key=key),self.assertRaises(ValueError):network.validate_pair(self.op,before,before,changed)
        changed=copy.deepcopy(after);changed['guestNetwork']['policySHA256']='7'*64
        with self.assertRaises(ValueError):network.validate_pair(self.op,after,after,changed)
    def test_files_enable_disable_retains_schema5_and_network_pins(self):
        self.enable();before=self.op.current();after={k:v for k,v in before.items() if k!='userFiles'};files_management.validate_pair(self.op,before,before,after);files_management.validate_pair(self.op,after,after,before);self.assertEqual(after['guestNetwork'],before['guestNetwork'])
    def test_turn_change_retains_schema5_and_files_and_network(self):
        self.enable();before=self.op.current();turn_management.validate_pair(self.op,before,before,copy.deepcopy(before))
        changed=copy.deepcopy(before);changed['guestNetwork']['policySHA256']='8'*64
        with self.assertRaises(ValueError):turn_management.validate_pair(self.op,before,before,changed)
    def test_data_restore_requires_worker_policy_stopped(self):
        self.enable()
        with self.assertRaises(ValueError):network.require_stopped(self.op,self.op.current())
        self.op.stop(self.op.current(),['guest']);network.require_stopped(self.op,self.op.current())
    def test_actual_profile11_cannot_accept_enabled_schema5(self):
        config={**self.op.before,'version':network.VERSION,'release':str(ROOT/'.build/releases/connected-files-r2'),'guestNetwork':self.op.value};config.pop('userFiles')
        with patch.object(native,'path',side_effect=Path),self.assertRaisesRegex(ValueError,'below profile12'):native.installed(config)

if __name__=='__main__':
    names=['origin_service/network_management.py','origin_service/deployment.py','origin_service/files_management.py','origin_service/turn_management.py','origin_service/maintenance.py','origin_service/release.py','scripts/manage-services.py','scripts/native-network-policy-check.py']
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names};result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Transitions))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','scope':__doc__,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'sha256':hashes,'installedLifecycleVerified':False,'kernelEffectsModeled':True,'liveChanged':False}
    output=ROOT/'.build/checks/native-network-policy-result.json'
    if output.exists():output.rename(output.with_name('native-network-policy-before-'+str(time.time_ns())+'.json'))
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
