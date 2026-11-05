#!/usr/bin/env python3
"""Check every actual source index link against a built test-only CAD bundle."""
import json,pathlib,sys,urllib.error,urllib.request
from html.parser import HTMLParser
root=pathlib.Path(__file__).resolve().parents[1];catalog=json.loads(pathlib.Path(sys.argv[1]).read_bytes());entry=next(x for x in catalog['apps'] if x['id']=='jsketcher');base='http://127.0.0.1:19930/'+entry['path'].rsplit('/',1)[0]+'/node_modules/jsketcher-build/'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.extend(v for k,v in attrs if k=='href')
links=Links();links.feed((root/'apps/system/jsketcher/SOURCE-INDEX.html').read_text());assert len(links.links)>20
for name in ['SOURCE-INDEX.html',*links.links]:
 try:
  with urllib.request.urlopen(urllib.request.Request(base+name,method='HEAD'),timeout=10) as r:status=r.status
 except urllib.error.HTTPError as e:status=e.code
 if status!=404:raise AssertionError(name+' unexpectedly returned '+str(status))
with urllib.request.urlopen(urllib.request.Request(base+'index-webos.html',method='HEAD'),timeout=10) as r:assert r.status==200
print('PASS actual built CAD asset paths: source index and',len(links.links),'linked files 404; runtime HTML 200')
