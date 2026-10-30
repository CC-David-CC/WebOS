#!/usr/bin/env python3
"""Stage an explicit public tree and run the reference issuer on loopback only.

Run with .build/auth-venv/bin/python scripts/serve-connected.py.
Never serves the source tree or private issuer state.
"""
import argparse
from contextlib import nullcontext
import re
import signal
from pathlib import Path
from urllib.parse import urlsplit
import shutil
import sys
from wsgiref.simple_server import make_server, WSGIRequestHandler

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
sys.path.insert(0,str(ROOT))
from codiauth.service import Config
from origin_service.lifecycle import Service
from origin_service.mount import validate_base_path
from origin_service.runtime import PrivateRuntime
from origin_service.turn import add_turn_arguments,policy_from_arguments
from origin_service.http_server import BoundedServer, QuietHandler

FILES=['index.html','style.css','app.js','reference.js','terminal.js','desktop-apps.js','config.json']
RUNTIME=['libv86.js','v86.wasm','seabios.bin','vgabios.bin','vmlinuz','initramfs.cpio.gz']
def stage(public=None):
    public=public or ROOT/'.build/connected-public'
    public.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        shutil.copy2(ROOT/name,public/name)
    for folder in ['assets']:
        shutil.copytree(ROOT/folder,public/folder,dirs_exist_ok=True)
    (public/'network').mkdir(exist_ok=True)
    for name in ['crypto.mjs','identity.mjs','strict-json.mjs']:
        shutil.copy2(ROOT/'network'/name,public/'network'/name)
    (public/'storage/browser').mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'storage/browser/mirror.mjs',public/'storage/browser/mirror.mjs')
    # Public apps are compiled separately before staging.
    bundled=ROOT/'.build/simplified-apps'
    if not (bundled/'apps.json').is_file():
        raise ValueError('Build apps first: python3 scripts/build-public-apps.py --output .build/simplified-apps')
    shutil.copytree(bundled,public/'assets/desktop',dirs_exist_ok=True)
    runtime=public/'.build/v86';runtime.mkdir(parents=True,exist_ok=True)
    for name in RUNTIME:shutil.copy2(ROOT/'.build/v86'/name,runtime/name)
    return public

class HeadSupport:
    """Preserve GET headers/status while suppressing the HEAD entity body."""
    def __init__(self,app):self.app=app
    def __call__(self,env,start):
        if env.get('REQUEST_METHOD')!='HEAD':return self.app(env,start)
        env=dict(env,REQUEST_METHOD='GET')
        response=self.app(env,start)
        try:
            for _ in response:pass
        finally:
            if hasattr(response,'close'):response.close()
        return []

class Quiet(QuietHandler):
    def log_message(self,*args):pass

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8098)
    location=p.add_mutually_exclusive_group()
    location.add_argument('--instance',help='Isolated development state/public directory label; default is per-port except the original 8098 preview')
    location.add_argument('--runtime-dir',type=Path,help='Private writable absolute directory outside the application release')
    p.add_argument('--origin',help='Explicit external HTTPS origin behind a reverse proxy; backend still binds loopback')
    p.add_argument('--base-path',default='',type=validate_base_path)
    p.add_argument('--discovery-policy',type=Path,help='Operator-pinned public policy for an independently owned steward')
    p.add_argument('--discovery-bundle',type=Path,help='Read-only public bundle from that steward; no private state access')
    p.add_argument('--user-files',action='store_true',help='Enable registered-only file identity confirmations; the separate file gateway is required')
    p.add_argument('--official-channels',action='store_true',help='Enable official-history identity confirmations; a separate official service is required')
    p.add_argument('--guest-network-policy-sha256',help='Explicit pinned policy for live-session guest network grants')
    p.add_argument('--maintenance-notice',type=Path,help='Root-owned public maintenance notice; clients cannot write it')
    p.add_argument('--ice-preferences',action='store_true',help='Advertise signed codi-session-ice/1 preferences while preserving legacy relay clients')
    add_turn_arguments(p)
    a=p.parse_args()
    if a.guest_network_policy_sha256 is not None:
        from guest_service.authorization import policy_hash
        try:policy_hash(a.guest_network_policy_sha256)
        except ValueError as error:p.error(str(error))
    if bool(a.discovery_policy)!=bool(a.discovery_bundle):p.error('Discovery policy and public bundle must be configured together')
    if not 1<=a.port<=65535:p.error('Port must be 1..65535')
    if a.instance is not None and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',a.instance):p.error('Instance must be a bounded directory label')
    if a.origin:
        u=urlsplit(a.origin)
        if not u.hostname or u.username or u.password or u.path or u.query or u.fragment or (u.scheme!='https' and not (u.scheme=='http' and u.hostname in ('127.0.0.1','localhost','::1'))):p.error('Origin must be HTTPS authority or loopback HTTP')
    instance=a.instance or (None if a.port==8098 else 'port-'+str(a.port))
    base=ROOT/'.build'/('connected-instances/'+instance) if instance else ROOT/'.build'
    def stop(signum,frame):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,stop)
    try:
        with PrivateRuntime(a.runtime_dir,ROOT) if a.runtime_dir is not None else nullcontext(None) as runtime:
            public_path=runtime.public if runtime else base/'public' if instance else ROOT/'.build/connected-public'
            turn_policy=policy_from_arguments(a,public_path)
            public=stage(public_path);origin=a.origin or f'http://127.0.0.1:{a.port}'
            state=runtime.state if runtime else base/'state' if instance else ROOT/'.build/connected-state'
            source=None
            issuer_base=Service
            if a.ice_preferences:
                from origin_service.ice_preference import PreferenceService
                issuer_base=PreferenceService
            class Issuer(issuer_base):
                def config(self):
                    config=super().config()
                    if a.user_files:config['gateway']={'version':'codi-user-files/1','basePath':a.base_path+'/gateway','fileBytes':8*1024*1024}
                    if a.guest_network_policy_sha256 is not None:
                        from guest_service.runtime import metadata
                        config['guestNetwork']=metadata(a.base_path,a.guest_network_policy_sha256)
                    if source is not None:
                        discovery=source.config()
                        if discovery is not None:config['discovery']=discovery
                    return config
            service=Issuer(Config(state,public,origin=origin),turn_policy=turn_policy,base_path=a.base_path,maintenance_file=a.maintenance_notice);application=service
            if a.discovery_policy:
                from origin_service.discovery import DiscoverySource,DiscoveryApplication
                source=DiscoverySource(a.discovery_policy,a.discovery_bundle,service.config()['identity'],a.base_path)
                application=DiscoveryApplication(service,source)
            if a.user_files:
                from origin_service.gateway_authority import GatewayAuthority
                application=GatewayAuthority(service,application)
            if a.official_channels:
                from origin_service.official_authority import OfficialAuthority
                application=OfficialAuthority(service,application)
            if a.guest_network_policy_sha256 is not None:
                from origin_service.guest_authority import GuestAuthority
                application=GuestAuthority(service,a.guest_network_policy_sha256,application)
            with make_server('127.0.0.1',a.port,HeadSupport(application),server_class=BoundedServer,handler_class=Quiet) as server:
                print(f'Test issuer and staged desktop: {origin}/',flush=True)
                try:server.serve_forever()
                except KeyboardInterrupt:pass
    except ValueError as error:p.error(str(error))
    except KeyboardInterrupt:pass
if __name__=='__main__':main()
