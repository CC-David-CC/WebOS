#!/usr/bin/env python3
"""Ordinary public TLS acceptance of current full Rooms UI or zero-seed Linux peers."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
public=module('directory_public_support',ROOT/'scripts/hosted-peer-public-check.py')
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--desktop',action='store_true');a=p.parse_args();assert not a.output.exists()
suite=module('directory_public_actual',ROOT/('scripts/reader-directory-ui-check.py'if a.desktop else'scripts/reader-directory-native-check.py'));original=suite.driver.call

def trusted(path,data=None,method=None):
 if path=='/session':
  caps=data['capabilities']['alwaysMatch'];args=caps['goog:chromeOptions']['args'];marker='--ignore-certificate-errors-spki-list='+public.MARKER;assert args.count(marker)==1;args.remove(marker);assert not any('ignore-certificate'in v for v in args);caps['acceptInsecureCerts']=False
 return original(path,data,method)
suite.driver.call=trusted;suite.vm.remote=public.public_remote
v=suite.run(a.release.resolve());v.update(scope=__doc__,suite='complete-desktop36cycles'if a.desktop else'same-network-three-Linux-peer-recovery',defaultPublicTLS=True,fixtureSPKIOnly=False,actualURL='https://ksu.codes/',productionDeploymentChanged=False,publicQADataCreated=True,publicWANTested=False,wholeGoalComplete=False,wrapperSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS'else 1)
