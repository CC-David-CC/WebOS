#!/usr/bin/env python3
"""Seal the isolated security source against the frozen native14 public tree.

Never exports the current routed-group/API2 app worktree. The base public file
map is fixed and byte-verified before a new profile15 artifact is created.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'.build/releases/connected-ice-preference-r2'
SOURCE=ROOT/'.build/signin-native-source'
BASE_SHA='8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce'

def contract():
    spec=importlib.util.spec_from_file_location('signin_release_contract',SOURCE/'origin_service/release.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def signin_ui(stage, public):
    """Update the frozen API1 frontend without importing API2/routing work."""
    def replace(name, old, new):
        path=stage/name;text=path.read_text()
        if text.count(old)!=1:raise ValueError('Frozen UI input changed: '+name)
        path.write_text(text.replace(old,new))
    name='app.js';text=(stage/name).read_text()
    start=text.index('  appendNetworkInfo(popup){\n');end=text.index('  showStatus(type,anchor)',start)
    text=text[:start]+'''  appendNetworkInfo(popup){
    const network=identityConfig?.guestNetwork,requiresSignin=network?.previewPolicy?.anonymousInternet==='deny';
    let description='Guest networking: loopback only. Try ping -c 2 127.0.0.1. External websites open in normal browser tabs.';
    if(network)description=requiresSignin&&!signedInSubject()
      ?'Sign in using Anon to enable Linux Internet: ping, DNS and web access. Local Linux and browser chat/chess remain available without signing in.'
      :(requiresSignin?'Linux Internet is enabled for signed-in accounts':'Guest Internet is configured')+' through box-webhost’s connection. Try ping -c 2 1.1.1.1.';
    popup.append(make('h4','','Network'),make('div','status-line','Browser: '+(navigator.onLine?'online':'offline')),make('p','',description));
    if(guestNetworkAdapter?.controlled!==false&&network?.durableAccountLimits)popup.append(make('p','','Preview network: '+(requiresSignin?'sign-in is required for all public ping, DNS and web connections on ports 80/443.':'public ping, DNS, and web connections on ports 80/443. Access to the host’s public address requires sign-in.')+' Private networks are blocked. Account and shared traffic limits persist across reconnects and service restarts.'));
    else if(network?.previewPolicy)popup.append(make('p','','Preview network: public ping, DNS, and web connections on ports 80/443. Each connection lasts up to 30 minutes or 64 MiB. The preview shares a 256 MiB allowance until the operator restarts it.'));
  }
'''+text[end:];(stage/name).write_text(text)
    replace('desktop-apps.js',"(networkRelay?'Guest Internet uses", "(networkRelay?(identityConfig?.guestNetwork?.previewPolicy?.anonymousInternet==='deny'?'Sign in using Anon before using Linux Internet: ping, DNS or web access. Local Linux and browser chat/chess still work anonymously.\\n':'')+'Guest Internet uses")
    # Keep the old content-addressed Help module for already-loaded catalogs.
    catalog_path=stage/'assets/desktop/apps.json';catalog=json.loads(catalog_path.read_text());assert catalog['hostAPI']==1
    help_app=next(app for app in catalog['apps'] if app['id']=='help');old=stage/help_app['path']
    text=old.read_text();before='Guest Internet is available when the network relay is running.'
    assert text.count(before)==1
    raw=text.replace(before,'Check Network under your session status for Linux Internet access rules, including sign-in requirements for ping, DNS and web access. Browser chat and chess are separate from Linux Internet.').encode()
    key=hashlib.sha256(raw).hexdigest();name='assets/desktop/apps/help/'+key+'.mjs';(stage/name).write_bytes(raw)
    public['files'][name]=c_record(stage/name)
    help_app.update(path=name,sha256=key,bytes=len(raw));catalog_path.write_text(json.dumps(catalog,indent=2)+'\n')
    # Rebuild the exact existing cache allowlist; never scan private build state.
    cache=json.loads((stage/'assets/desktop/cache-manifest.json').read_text())
    names=set(cache['files'])|{name};assert not names&{'config.json','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
    records={name:c_record(stage/name) for name in sorted(names)}
    cache['files']=records;cache['id']=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();assert template.count('__PUBLIC_CACHE_MANIFEST__')==1
    (stage/'assets/desktop/cache-manifest.json').write_text(json.dumps(cache,indent=2)+'\n')
    (stage/'assets/desktop/offline-worker.js').write_text(template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
    public['files']={name:c_record(stage/name) for name in sorted(public['files'])}
    (stage/'release.json').write_text(json.dumps(public,indent=2)+'\n')

def c_record(path):
    raw=path.read_bytes();return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}

def build(destination,with_signin_ui=False):
    c=contract();baseline=c.verify(BASE);assert baseline['manifestSHA256']==BASE_SHA
    public=json.loads((BASE/'release.json').read_text())
    destination=Path(destination).absolute()
    if destination.exists() or any(p.is_symlink() for p in [destination,*destination.parents]) or not destination.is_relative_to(ROOT/'.build/releases'):
        raise ValueError('Choose a new private release directory')
    stage=Path(tempfile.mkdtemp(prefix='.signin-export-',dir=destination.parent))
    try:
        for name in sorted(set(public['files'])|{'release.json'}):
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/name,target)
        for name in sorted(c.V15_NATIVE):
            source=SOURCE/name
            if not source.is_file() or any(p.is_symlink() for p in [source,*source.parents]):raise ValueError('Regular security source required: '+name)
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if with_signin_ui:signin_ui(stage,public)
        files={str(p.relative_to(stage)):c.record(p) for p in sorted(stage.rglob('*')) if p.is_file()}
        (stage/'connected-release.json').write_text(json.dumps({'version':'codi-connected-development/15','authorityClass':'development','mount':'configurable','guestEgress':'relay-host','files':files},indent=2)+'\n')
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        result=c.verify(stage)
        for name,record in public['files'].items():assert result and c.record(stage/name)==record
        stage.rename(destination)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return c.verify(destination)|{'baseManifestSHA256':BASE_SHA,'publicAssetsUnchanged':not with_signin_ui,'signinUICopy':with_signin_ui}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--signin-ui',action='store_true');args=p.parse_args();print(json.dumps(build(args.output,args.signin_ui),indent=2))
