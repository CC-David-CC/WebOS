#!/usr/bin/env python3
"""Real live three-desktop cleanup continues after one close-report failure.

The first Chrome in final teardown is actually closed, then its supervisor response is
deliberately lost. Remaining browsers and QA account must still be cleaned up.
This is same-network ordinary TLS, not outside-WAN acceptance.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(release):
    suite=module('cleanup_fault_native',ROOT/'scripts/reader-directory-native-check.py')
    public=module('cleanup_fault_public',ROOT/'scripts/hosted-peer-public-check.py')
    original=suite.driver.call;closed=[];injected=False
    def call(path,data=None,method=None):
        nonlocal injected
        if path=='/session':
            caps=data['capabilities']['alwaysMatch'];args=caps['goog:chromeOptions']['args'];marker='--ignore-certificate-errors-spki-list='+public.MARKER
            assert args.count(marker)==1;args.remove(marker);assert not any('ignore-certificate' in v for v in args);caps['acceptInsecureCerts']=False
        value=original(path,data,method)
        if method=='DELETE' and path.startswith('/session/'):
            closed.append(path)
            # The first DELETE is the scenario's deliberate intermediary loss.
            # The second is final teardown, where cleanup must continue.
            if len(closed)==2:injected=True;raise RuntimeError('Owned injected lost browser-close response')
        return value
    suite.driver.call=call;suite.vm.remote=public.public_remote
    result={'status':'FAIL','scope':__doc__,'wholeGoalComplete':False}
    try:
        observed=suite.run(release);result['observedSuite']=observed
        assert observed['status']=='FAIL' and not observed.get('error'),observed.get('error')
        assert len(observed['checks'])==11 and len(closed)==3 and len(set(closed))==3
        assert observed['ownedBrowserContextsClosed']==2 and observed['ownedAccountPolicy']['disabled']
        assert observed['cleanupErrors']==[{'stage':'browser-close','error':'Owned injected lost browser-close response'}]
        assert original('/sessions')==[]
        result.update(status='PASS',actualOwnedBrowsersClosed=3,reportedFailureRetained=True,qaDisabledDespiteCleanupFailure=True,ordinaryTLS=True,publicWANTested=False)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v.get(k) for k in ['status','actualOwnedBrowsersClosed','qaDisabledDespiteCleanupFailure','error']}));raise SystemExit(0 if v['status']=='PASS' else 1)
