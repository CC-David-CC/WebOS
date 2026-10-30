#!/usr/bin/env python3
"""Actual account/guest policy or durable document workflow at the VM HTTPS root."""
import argparse,hashlib,importlib.util,json,secrets,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def run(kind):
    vm=module('root_workflow_vm',ROOT/'scripts/upgrade-signin-native-vm.py');before=vm.runtime()
    installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'))
    base=vm.remote("/usr/bin/python3 -B -c \"import json;print(json.load(open('/etc/codi-native-fixture/managed.json'))['basePath'])\"").strip();assert base==''
    if kind=='accounts':
        name='scripts/signin-native-vm-browser-check.py';suite=module('root_account_suite',ROOT/name);result=suite.browser(installed,check_ui=True,base='')
    else:
        name='scripts/document-workflow-browser-check.py';suite=module('root_document_suite',ROOT/name)
        ledger={'names':['qa_doc_'+secrets.token_hex(6) for _ in range(2)],'subjects':{},'ownedFilesRemoved':False}
        try:result=suite.browser(installed['publicOrigin'],['--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']],ledger,base='')
        finally:(ROOT/'.build/checks/mount-root-document-fixtures.json').write_text(json.dumps(ledger,indent=2)+'\n')
    assert before==vm.runtime()
    return result|{'scope':__doc__,'kind':kind,'actualRootURL':installed['publicOrigin']+'/','nativeManifestSHA256':before['manifestSHA256'],'fixtureSPKIOnly':True,'productionURLsChanged':False,'suiteSourceSHA256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=['accounts','documents']);a=p.parse_args();result={'status':'FAIL'}
    try:result.update(run(a.kind))
    finally:
        result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('mount-root-'+a.kind+'-result.json')
        if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
