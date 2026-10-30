#!/usr/bin/env python3
"""Install one isolated official Chrome-for-Testing pair for owned load tests.

Run as the normal test user. No services, firewall, router ports or global
packages are changed here. Missing OS libraries are reported for a separate
explicit package install. Retain version, HTTPS source and exact archive hashes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import urllib.request
import zipfile

INDEX='https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'


def prepare(root):
    root=Path(root).absolute();assert root.is_relative_to(Path.home()) and '..' not in root.parts
    for p in [root,*root.parents]:assert not p.is_symlink()
    root.mkdir(mode=0o700,parents=True,exist_ok=True)
    manifest=root/'browser-runtime.json'
    if manifest.exists():
        value=json.loads(manifest.read_bytes());folder=root/'browsers'/value['version']
        for name,r in value['files'].items():
            p=folder/name;assert not p.is_symlink() and r=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    else:
        with urllib.request.urlopen(INDEX,timeout=30) as response:
            raw=response.read(1048577);assert len(raw)<=1048576;index=json.loads(raw)
        stable=index['channels']['Stable'];version=stable['version'];assert re.fullmatch(r'\d+\.\d+\.\d+\.\d+',version)
        folder=root/'browsers'/version;assert not folder.exists();folder.mkdir(parents=True)
        downloads=[]
        for kind in ['chrome','chromedriver']:
            item=next(v for v in stable['downloads'][kind] if v['platform']=='linux64')
            expected='https://storage.googleapis.com/chrome-for-testing-public/'+version+'/linux64/'+kind+'-linux64.zip'
            assert item['url']==expected
            archive=root/(kind+'-'+version+'.zip');assert not archive.exists();digest=hashlib.sha256();size=0
            with urllib.request.urlopen(expected,timeout=60) as response,archive.open('xb') as output:
                while chunk:=response.read(1048576):
                    size+=len(chunk);assert size<=512*1048576;digest.update(chunk);output.write(chunk)
            with zipfile.ZipFile(archive) as package:
                entries=package.infolist();assert sum(v.file_size for v in entries)<=1024*1048576
                assert len({v.filename for v in entries})==len(entries)
                for entry in entries:
                    name=Path(entry.filename);assert not name.is_absolute() and '..' not in name.parts and name.parts[0]==kind+'-linux64'
                    mode=entry.external_attr>>16;assert not stat.S_ISLNK(mode)
                    dest=folder/name
                    if entry.is_dir():dest.mkdir(mode=0o755,parents=True,exist_ok=True);continue
                    dest.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
                    with package.open(entry) as source,dest.open('xb') as output:shutil.copyfileobj(source,output)
                    dest.chmod(0o755 if mode&0o111 else 0o644)
            downloads.append({'url':expected,'bytes':size,'sha256':digest.hexdigest()});archive.unlink()
        files={str(p.relative_to(folder)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(folder.rglob('*')) if p.is_file()}
        value={'version':version,'indexURL':INDEX,'indexSHA256':hashlib.sha256(raw).hexdigest(),'downloads':downloads,'files':files}
        manifest.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    chrome=folder/'chrome-linux64/chrome';driver=folder/'chromedriver-linux64/chromedriver'
    missing=set()
    for binary in [chrome,driver]:
        r=subprocess.run(['ldd',str(binary)],capture_output=True,text=True,timeout=30)
        missing.update(re.findall(r'^\s*(\S+)\s+=>\s+not found\s*$',r.stdout,re.M))
    result={'status':'DEPENDENCIES_REQUIRED' if missing else 'PASS','version':value['version'],'chromeBinary':str(chrome),'driverBinary':str(driver),'manifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'downloads':value['downloads'],'missingLibraries':sorted(missing),'servicesChanged':False,'packagesInstalled':False,'routerPortsChanged':False}
    if not missing:
        result['chromeVersion']=subprocess.check_output([str(chrome),'--version'],text=True,timeout=15).strip()
        result['driverVersion']=subprocess.check_output([str(driver),'--version'],text=True,timeout=15).strip()
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);a=p.parse_args();assert os.geteuid()!=0
    print(json.dumps(prepare(a.directory),indent=2))
