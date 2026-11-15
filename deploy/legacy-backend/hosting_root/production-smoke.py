#!/usr/bin/env python3
"""Verified TLS GET/content checks; explicitly record the testing network scope."""
import argparse
import datetime
import http.client
import json
from pathlib import Path
import re
import socket
import ssl
from common import ROOT,load

p=argparse.ArgumentParser()
p.add_argument('--address',help='Optional connection IP; TLS SNI/hostname verification still use the domain')
p.add_argument('--scope',required=True)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
context=ssl.create_default_context()

def fetch(domain,path='/',secure=True,method='GET',host=None):
    address=args.address or domain
    port=443 if secure else 80
    conn=http.client.HTTPConnection(address,port,timeout=12)
    cert=None
    if secure:
        conn.sock=context.wrap_socket(socket.create_connection((address,port),timeout=12),server_hostname=domain)
        cert=conn.sock.getpeercert()
    try:
        conn.request(method,path,headers={'Host':host or domain})
        r=conn.getresponse();body=r.read();headers={k.lower():v for k,v in r.getheaders()}
        return r.status,body,headers,cert
    finally: conn.close()

out={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':args.scope,'connection_address':args.address or 'public DNS resolution','certificate_verification':'ssl.create_default_context; chain + exact hostname; no insecure override','sites':{}}
sites=[s for s in load()['sites'] if s['enabled']]
for s in sites:
    d=s['domain']
    try:
        if s.get('hardware_studio'):
            from hardware_hosting import smoke as hardware_smoke
            out['sites'][d]=hardware_smoke(s,fetch)
            print(d,'PASS',flush=True)
            continue
        if s.get('cardboard_studio'):
            from cardboard_hosting import smoke as cardboard_smoke
            out['sites'][d]=cardboard_smoke(s,fetch)
            print(d,'PASS',flush=True)
            continue
        path='/static/style.css?acceptance=1'
        status,_,headers,_=fetch(d,path,secure=False)
        assert status in [301,302,307,308] and headers['location']=='https://'+d+path,('redirect',status,headers)
        redirect_status=status
        root_desktop=d=='ksu.codes' and s.get('codi_mount','/hidden')==''
        homepage='/blog/' if root_desktop else '/'
        status,body,headers,cert=fetch(d,homepage)
        assert status==200 and f'site:{d}:starter-v1'.encode() in body
        for other in sites:
            if other!=s: assert f"site:{other['domain']}:starter-v1".encode() not in body
        assert not re.search(rb'(?:src|href)\s*=\s*[\"\']http://',body,re.I)
        assert headers['x-content-type-options']=='nosniff' and "default-src 'none'" in headers['content-security-policy']
        assert headers['cache-control']=='no-cache, max-age=0, must-revalidate'
        code,head,h,_=fetch(d,homepage,method='HEAD');assert code==200 and head==b''
        assert h['cache-control']=='no-cache, max-age=0, must-revalidate'
        if root_desktop:
            code,content,h,_=fetch(d)
            assert code==200 and b'site:ksu.codes:starter-v1' not in content and b'assets/desktop/' in content
            assert h['cache-control']=='no-store' and "wasm-unsafe-eval" in h['content-security-policy']
            code,head,h,_=fetch(d,method='HEAD');assert code==200 and head==b'' and h['cache-control']=='no-store'
            code,content,h,_=fetch(d,'/config.json');assert code==200 and h['cache-control']=='no-store'
            identity=json.loads(content)['identity'];assert identity['mode']=='server' and identity['issuer']=='https://ksu.codes' and identity['apiBase']=='/api/v1'
            for entry in ['/hidden','/hidden/']:
                code,_,h,_=fetch(d,entry);assert code==308 and h['location']=='/'
            code,_,h,_=fetch(d,'/blog');assert code==308 and h['location']=='/blog/'
        for asset,marker in [('/static/style.css',b'body'),('/static/favicon.svg',b'<svg'),('/robots.txt',b'User-agent')]:
            code,content,h,_=fetch(d,asset);assert code==200 and marker in content,asset
            assert h['cache-control']=='no-cache, max-age=0, must-revalidate',asset
        code,content,h,_=fetch(d,'/healthz')
        assert code==200 and json.loads(content)=={'status':'ok','site':d} and h['cache-control']=='no-store'
        for path in ['/missing-page','/docs','/redoc','/openapi.json','/.env','/.git/config','/app/main.py','/requirements.lock.txt','/.venv/pyvenv.cfg','/static/%2e%2e/%2e%2e/etc/passwd']:
            code,content,_,_=fetch(d,path);assert code in [403,404] and b'root:x:' not in content,path
        out['sites'][d]={'result':'PASS','http_redirect':redirect_status,'https_get':200,'homepage_path':homepage,'root_desktop_verified':root_desktop,'certificate':cert,'checks':['HTTP redirect preserving path/query','verified TLS chain and hostname','GET/HEAD homepage and exact marker','CSS/favicon/robots','health and no-store','HTML and assets require cache revalidation','headers','private/missing routes denied','no insecure HTML asset references']}
        print(d,'PASS',flush=True)
    except Exception as e:
        out['sites'][d]={'result':'FAIL','error':str(e)};print(d,'FAIL',str(e),flush=True)
code,body,_,_=fetch(sites[0]['domain'],secure=False,host='unlisted.invalid')
out['unknown_http_host']={'status':code,'tenant_content':b'site:' in body}
assert code==404 and b'site:' not in body
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
if any(s['result']!='PASS' for s in out['sites'].values()): raise SystemExit(1)
