#!/usr/bin/env python3
"""Install an official pinned test browser only inside the existing private VM.

No host/browser installation, production changes, port exposure or credentials
are involved. The VM must already be QMP-confirmed running. Runtime files stay
private; only public download provenance is returned.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('ice_browser_vm',ROOT/'scripts/prepare-native-network-vm.py')
vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
INSIDE=r'''
import hashlib,json,os,pathlib,pwd,shutil,subprocess,urllib.request,zipfile
P=pathlib.Path
assert os.geteuid()==0 and P('/var/lib/codi-fixture-ready').is_file()
version='156.0.8078.47'
root=P('/opt/codi-ice-browser')/version
root.mkdir(parents=True,exist_ok=True)
records={}
for product,folder in [('chrome','chrome-linux64'),('chromedriver','chromedriver-linux64')]:
 url='https://storage.googleapis.com/chrome-for-testing-public/'+version+'/linux64/'+folder+'.zip'
 archive=root/(folder+'.zip')
 if not archive.exists():
  with urllib.request.urlopen(url,timeout=45) as source,archive.with_suffix('.part').open('wb') as dest:shutil.copyfileobj(source,dest)
  archive.with_suffix('.part').replace(archive)
 assert 5_000_000<archive.stat().st_size<300_000_000
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  for info in z.infolist():
   name=P(info.filename)
   assert not name.is_absolute() and '..' not in name.parts and name.parts[0]==folder
   assert (info.external_attr>>16)&0o170000!=0o120000
  if not (root/folder/product).exists():z.extractall(root)
  for info in z.infolist():
   extracted=root/info.filename
   if extracted.is_file() and (info.external_attr>>16)&0o111:extracted.chmod(0o755)
 binary=root/folder/product;binary.chmod(0o755)
 records[product]={'url':url,'archiveBytes':archive.stat().st_size,'archiveSHA256':hashlib.sha256(archive.read_bytes()).hexdigest(),'binarySHA256':hashlib.sha256(binary.read_bytes()).hexdigest()}
# Ubuntu dependencies come from the VM's signed distribution repositories.
packages=['libnss3','libatk1.0-0t64','libatk-bridge2.0-0t64','libcups2t64','libdrm2','libxkbcommon0','libxcomposite1','libxdamage1','libxfixes3','libxrandr2','libgbm1','libasound2t64','fonts-liberation']
env=dict(os.environ,DEBIAN_FRONTEND='noninteractive')
subprocess.run(['apt-get','update','-qq'],check=True,env=env,timeout=180,stdout=subprocess.DEVNULL)
subprocess.run(['apt-get','install','-y','--no-install-recommends',*packages],check=True,env=env,timeout=240,stdout=subprocess.DEVNULL)
for product,folder in [('chrome','chrome-linux64'),('chromedriver','chromedriver-linux64')]:
 actual=subprocess.check_output([str(root/folder/product),'--version'],text=True).strip()
 assert version in actual;records[product]['versionOutput']=actual
try:user=pwd.getpwnam('codi-ice-browser')
except KeyError:
 subprocess.run(['useradd','--system','--create-home','--home-dir','/var/lib/codi-ice-browser','--shell','/usr/sbin/nologin','codi-ice-browser'],check=True)
 user=pwd.getpwnam('codi-ice-browser')
assert user.pw_uid!=0 and user.pw_dir=='/var/lib/codi-ice-browser' and user.pw_shell=='/usr/sbin/nologin'
home=P(user.pw_dir);home.chmod(0o700)
receipt={'status':'PASS','scope':'Pinned official Chrome for Testing and signed Ubuntu dependencies installed only in the retained private VM','browserVersion':version,'browserUID':user.pw_uid,'browserGID':user.pw_gid,'browser':str(root/'chrome-linux64/chrome'),'driver':str(root/'chromedriver-linux64/chromedriver'),'downloads':records,'hostPackagesChanged':False,'webhostChanged':False}
(P('/srv/codi-network-fixture')/'ice-browser-installed.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
'''

if __name__=='__main__':
    vm.status()
    result=subprocess.run([*vm.ssh_args(),'/usr/bin/python3 -I -B -c '+shlex.quote(INSIDE)],check=True,capture_output=True,text=True,timeout=600)
    if result.stderr:print(result.stderr[-2000:])
    value=json.loads(result.stdout)
    value['sha256']={'scripts/setup-ice-browser-vm.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'.build/checks/ice-browser-vm-setup-result.json').write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value,indent=2))
