#!/usr/bin/env python3
"""Serve the registered Browser relay on a Caddy-owned Unix socket.

This is an explicit operator entrypoint. It does not install a systemd unit,
modify firewall rules, create public routes or change account state.
"""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import socket
import stat
import struct
import sys
from aiohttp import web

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
sys.path.insert(0,str(ROOT.parent/'apps/system/browser'))
from browser_service.http import BrowserHTTP
from browser_service.sessions import BrowserSessions
from network_policy.policy import LocalCountryDatabase,PolicyLoader,address
from relay.wisp import Relay
from relay.download import Downloader


def protected(path,*,maximum):
    path=Path(path).absolute()
    for part in [path,*path.parents]:
        info=part.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid not in (0,os.geteuid()) or (info.st_mode&0o022 and not (stat.S_ISDIR(info.st_mode) and info.st_mode&stat.S_ISVTX)):
            raise ValueError('Protected operator-owned files and directories required')
    info=path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>maximum:
        raise ValueError('Bounded regular configuration file required')
    return path


def trusted_client(request,expected_uid):
    transport=request.transport
    peer=transport.get_extra_info('socket') if transport else None
    if peer is None or peer.family!=socket.AF_UNIX:raise web.HTTPForbidden()
    try:_,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
    except (OSError,ValueError,struct.error):raise web.HTTPForbidden() from None
    if uid!=expected_uid:raise web.HTTPForbidden()
    values=request.headers.getall('X-Codi-Client-IP',[])
    if len(values)!=1 or ',' in values[0] or '%' in values[0] or values[0]!=values[0].strip():raise web.HTTPForbidden()
    try:return str(address(values[0]))
    except ValueError:raise web.HTTPForbidden() from None


def make_app(*,origin,base_path,issuer_policy,policy_sha256,destination_policy,access_policy,geo,proxy_uid):
    if type(proxy_uid) is not int or proxy_uid<0:raise ValueError('Explicit trusted proxy UID required')
    access=PolicyLoader(access_policy,geo)
    async def unavailable(_request):return None
    relay=Relay(policy_path=destination_policy,origin=origin,authenticate=unavailable,
                source=lambda req:trusted_client(req,proxy_uid),network_check=lambda ip:access.check('outgoing',ip))
    sessions=BrowserSessions(issuer_policy,policy_sha256,base_path=base_path)
    @web.middleware
    async def only_proxy(request,handler):
        trusted_client(request,proxy_uid)
        return await handler(request)
    app=web.Application(client_max_size=16384,middlewares=[only_proxy],handler_args={'auto_decompress':False,'max_headers':32,'keepalive_timeout':5})
    BrowserHTTP(sessions,relay,origin=origin,base_path=base_path,downloader=Downloader(relay)).routes(app)
    return app


async def serve(args):
    issuer_file=protected(args.issuer_policy,maximum=32768)
    dest=protected(args.destination_policy,maximum=65536)
    access=protected(args.access_policy,maximum=1024*1024)
    if not re.fullmatch('[0-9a-f]{64}',args.issuer_policy_sha256) or not re.fullmatch('[0-9a-f]{64}',args.policy_sha256):raise ValueError('Exact policy pins required')
    raw=issuer_file.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=args.issuer_policy_sha256:raise ValueError('Issuer policy pin changed')
    value=json.loads(raw);issuer=value.get('identity',value)
    if issuer.get('issuer')!=args.origin:raise ValueError('Issuer and Browser origins differ')
    geo=LocalCountryDatabase(protected(args.geoip,maximum=128*1024*1024)) if args.geoip else None
    app=make_app(origin=args.origin,base_path=args.base_path,issuer_policy=issuer,policy_sha256=args.policy_sha256,
                 destination_policy=dest,access_policy=access,geo=geo,proxy_uid=args.proxy_uid)
    sockpath=Path(args.socket).absolute();parent=sockpath.parent
    info=parent.stat()
    if parent.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid() or info.st_gid!=args.proxy_gid or stat.S_IMODE(info.st_mode)!=0o750:
        raise ValueError('Service-owned 0750 socket directory required')
    if sockpath.exists() or sockpath.is_symlink():raise ValueError('Existing socket path refused')
    runner=web.AppRunner(app,access_log=None,shutdown_timeout=10);await runner.setup()
    try:
        site=web.UnixSite(runner,str(sockpath));await site.start();os.chmod(sockpath,0o660)
        stop=asyncio.Event();loop=asyncio.get_running_loop()
        for sig in (signal.SIGTERM,signal.SIGINT):loop.add_signal_handler(sig,stop.set)
        print('Browser relay ready on protected Unix socket',flush=True)
        await stop.wait()
    finally:
        await runner.cleanup()
        try:
            info=sockpath.lstat()
            if stat.S_ISSOCK(info.st_mode) and info.st_uid==os.geteuid():sockpath.unlink()
        except FileNotFoundError:pass
        if geo:geo.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--origin',required=True);p.add_argument('--base-path',default='')
    p.add_argument('--issuer-policy',type=Path,required=True);p.add_argument('--issuer-policy-sha256',required=True)
    p.add_argument('--policy-sha256',required=True,help='Explicit Browser authorization policy identifier')
    p.add_argument('--destination-policy',type=Path,required=True);p.add_argument('--access-policy',type=Path,required=True)
    p.add_argument('--geoip',type=Path);p.add_argument('--socket',type=Path,required=True);p.add_argument('--proxy-uid',type=int,required=True);p.add_argument('--proxy-gid',type=int,required=True)
    args=p.parse_args()
    try:asyncio.run(serve(args))
    except (ValueError,OSError,KeyError) as error:p.error(str(error))
