#!/usr/bin/env python3
"""Translate a generated Caddyfile for disposable loopback execution only."""
import os,re,subprocess,sys,tempfile,time,http.client
from pathlib import Path
root=Path(os.environ['CODI_FILES_FIXTURE_ROOT']);caddy=os.environ['CODI_FILES_FIXTURE_CADDY'];admin=os.environ['CODI_FILES_CADDY_ADMIN'];port=os.environ['CODI_FILES_CADDY_PORT']
def render(path):
 raw=Path(path).read_text();end=raw.index('\n}\n\n(site_defaults)')+3
 raw=raw[:raw.index('{\n')]+'{\n admin 127.0.0.1:'+admin+'\n auto_https off\n default_bind 127.0.0.1\n}\n'+raw[end:]
 raw=re.sub(r'(?m)^(?:http://)?([a-zA-Z0-9.-]+) \{',lambda m:'http://'+m.group(1)+':'+port+' {',raw)
 raw=re.sub(r'127\.0\.0\.1:(?:80[0-9]{2}|81[0-9]{2}|28[0-9]{3})','127.0.0.1:19901',raw)
 return raw.replace('import /etc/caddy/private/hardware-users','disposable $2a$14$Vsf9aNUClfIcH1B53DOtBeXH1dC/g55j5jA0XWRGuTb.2zsRuVONS')
def output(path):
 p=root/'loopback-caddyfile';p.write_text(render(path));return p
if sys.argv[1]=='render':output(sys.argv[2])
elif sys.argv[1]=='validate':subprocess.run([caddy,'validate','--config',str(output(sys.argv[2])),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30)
elif sys.argv[1]=='reload':subprocess.run([caddy,'reload','--address','127.0.0.1:'+admin,'--config',str(output(sys.argv[2])),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30)
elif sys.argv[1]=='wait':
 for _ in range(150):
  try:
   c=http.client.HTTPConnection('127.0.0.1',int(port),timeout=.2);c.request('GET','/',headers={'Host':'beta.ksu.codes'});r=c.getresponse();r.read();c.close();break
  except OSError:time.sleep(.1)
 else:raise SystemExit('fixture Caddy did not start')
else:raise SystemExit('unknown fixture Caddy operation')
