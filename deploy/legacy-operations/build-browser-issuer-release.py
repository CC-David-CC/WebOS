#!/usr/bin/env python3
"""Build a profile-28 Browser issuer from the exact live profile-27 release.

This only creates a candidate; it does not install, restart or publish it.
The profile-27 manifest is pinned because production has evolved beyond the
older Simplified source tree. Public assets and account data are not changed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE_PIN = '14c3655633cbe74388c1e7382f20768ce75e7cbb99eb22903c8686f3a270d1d0'
POLICY_PIN = '7faf30b5457fa629acc7ffa695c15a6a8a56098ba4372412260ade478af5a537'
ADDED = ('origin_service/browser_authority.py', 'browser_service/__init__.py',
         'browser_service/authorization.py', 'network_policy/__init__.py',
         'network_policy/policy.py', 'network_policy/login.py', 'network_policy/login_server.py')


def once(text, old, new, label):
    if text.count(old) != 1:
        raise ValueError(f'{label}: expected exactly one baseline anchor, found {text.count(old)}')
    return text.replace(old, new, 1)


def verifier(root):
    path = root / 'origin_service/release.py'
    spec = importlib.util.spec_from_file_location('pinned_release_verifier', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transform_server(text):
    text = once(text, 'from contextlib import nullcontext', 'from contextlib import nullcontext, closing', 'contexts')
    anchor = "    p.add_argument('--guest-network-policy-sha256',help='Explicit pinned policy for live-session guest network grants')"
    extra = """
    p.add_argument('--browser-relay-policy-sha256')
    p.add_argument('--login-port',type=int)
    p.add_argument('--login-access-policy',type=Path)
    p.add_argument('--login-geoip',type=Path)"""
    text = once(text, anchor, anchor + extra, 'arguments')
    anchor = '\n    if a.guest_network_policy_sha256 is not None:\n'
    extra = """    login_values=(a.login_port,a.login_access_policy,a.login_geoip)
    if any(value is not None for value in login_values) and not all(value is not None for value in login_values):p.error('Login port, access policy and Geo-IP database must be configured together')
    if a.login_port is not None and (not 1<=a.login_port<=65535 or a.login_port==a.port):p.error('Distinct valid login port required')
    if a.browser_relay_policy_sha256 is not None:
        from browser_service.authorization import policy_hash
        try:policy_hash(a.browser_relay_policy_sha256)
        except ValueError as error:p.error(str(error))
"""
    text = once(text, anchor, '\n' + extra + anchor.lstrip('\n'), 'argument validation')
    anchor = "                    if a.user_files:config['gateway']={'version':'codi-user-files/1','basePath':a.base_path+'/gateway','fileBytes':8*1024*1024}"
    extra = "\n                    if a.browser_relay_policy_sha256 is not None:config['browserRelay']={'version':'codi-browser-relay/1','basePath':a.base_path+'/browser-relay','policySHA256':a.browser_relay_policy_sha256}"
    text = once(text, anchor, anchor + extra, 'browser configuration')
    anchor = "            with make_server('127.0.0.1',a.port,HeadSupport(application),server_class=BoundedServer,handler_class=Quiet) as server:\n                print(f'Test issuer and staged desktop: {origin}/',flush=True)\n                try:server.serve_forever()\n                except KeyboardInterrupt:pass"
    replacement = """            if a.browser_relay_policy_sha256 is not None:
                from origin_service.browser_authority import BrowserAuthority
                application=BrowserAuthority(service,a.browser_relay_policy_sha256,application)
            if a.login_port is not None:
                from network_policy.policy import LocalCountryDatabase
                from network_policy.login_server import split_login_server
            with closing(LocalCountryDatabase(a.login_geoip)) if a.login_port is not None else nullcontext(None) as geo:
                with split_login_server(application,a.login_access_policy,port=a.login_port,server_class=BoundedServer,handler_class=Quiet,geo=geo,base_path=a.base_path) if a.login_port is not None else nullcontext(application) as public_application:
                    with make_server('127.0.0.1',a.port,HeadSupport(public_application),server_class=BoundedServer,handler_class=Quiet) as server:
                        print(f'Test issuer and staged desktop: {origin}/',flush=True)
                        try:server.serve_forever()
                        except KeyboardInterrupt:pass"""
    return once(text, anchor, replacement, 'split login listener')


def transform_release(text):
    old = "V19_NATIVE=frozenset(V15_NATIVE|set(['origin_service/room_authority.py', 'origin_service/room_management.py', 'room_service/__init__.py', 'room_service/contract.py']))"
    names = set(ADDED) | {'origin_service/official_authority.py','origin_service/official_management.py','origin_service/official_backend_custody.py','steward/official_channel_checker.py'}
    new = old + "\nV28_NATIVE=V19_NATIVE|{" + ','.join(repr(name) for name in sorted(names)) + '}'
    text = once(text, old, new, 'profile-28 native files')
    text = once(text, 'range(1,28)', 'range(1,29)', 'profile range')
    old = "'steward/official_channel_checker.py'}}[manifest['version']]"
    new = "'steward/official_channel_checker.py'},'codi-connected-development/28':V28_NATIVE}[manifest['version']]"
    text = once(text, old, new, 'profile mapping')
    return once(text, "'codi-connected-development/26','codi-connected-development/27'):verify_hosted_mail_graph", "'codi-connected-development/26','codi-connected-development/27','codi-connected-development/28'):verify_hosted_mail_graph", 'hosted graph verification')


def transform_manager(text):
    old = "if json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/27':command+=['--official-reader-port','8145']"
    new = "if json.loads((source/'connected-release.json').read_text())['version'] in ('codi-connected-development/27','codi-connected-development/28'):command+=['--official-reader-port','8145']"
    text = once(text, old, new, 'official channel reader')
    text = text.replace("'codi-connected-development/27')", "'codi-connected-development/27','codi-connected-development/28')")
    anchor = "  if role=='issuer' and config.get('userFiles'):command+=['--user-files']"
    addition = """  if role=='issuer' and json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/28':
   command+=['--browser-relay-policy-sha256','""" + POLICY_PIN + """','--login-port','8117','--login-access-policy','/etc/codi-browser/access-policy.json','--login-geoip','/etc/codi-browser/country.mmdb']
"""
    text = once(text, anchor, addition + anchor, 'browser issuer settings')
    anchor = ' assertions=[]\n'
    addition = " if role=='issuer' and json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/28':dependency+='Requires=codi-issuer-ingress.service\\nAfter=codi-issuer-ingress.service\\n'\n"
    return once(text, anchor, addition + anchor, 'startup boundary')


def build(base, destination):
    base=base.resolve();destination=destination.absolute()
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():raise ValueError('New output directory under existing parent required')
    if verifier(base).verify(base)['manifestSHA256'] != BASE_PIN:raise ValueError('Wrong baseline manifest')
    if base in destination.parents or destination in base.parents:raise ValueError('Candidate and baseline must be disjoint')
    shutil.copytree(base,destination)
    for name in ADDED:
        src=ROOT/name;dst=destination/name
        if src.is_symlink() or not src.is_file() or dst.exists():raise ValueError('Invalid added source: '+name)
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    def edit(name,fn):
        path=destination/name;path.write_text(fn(path.read_text()))
    edit('scripts/serve-connected.py',transform_server)
    edit('origin_service/release.py',transform_release)
    edit('scripts/manage-services.py',transform_manager)
    edit('origin_service/deployment.py',lambda s:s.replace("'codi-connected-development/27')", "'codi-connected-development/27','codi-connected-development/28')"))
    lock=destination/'requirements.lock';lock.write_text(lock.read_text()+'maxminddb==2.8.2\n')
    manifest_path=destination/'connected-release.json';manifest=json.loads(manifest_path.read_text());manifest['version']='codi-connected-development/28'
    for name in (*ADDED,'scripts/serve-connected.py','origin_service/release.py','scripts/manage-services.py','origin_service/deployment.py','requirements.lock'):
        raw=(destination/name).read_bytes();manifest['files'][name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    return verifier(destination).verify(destination)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--base',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    try:print(json.dumps(build(args.base,args.output),indent=2))
    except (ValueError,OSError) as error:parser.error(str(error))
