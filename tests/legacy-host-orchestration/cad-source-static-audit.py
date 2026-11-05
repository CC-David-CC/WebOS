#!/usr/bin/env python3
"""The generated app catalog cannot publish source-index linked files."""
import json,pathlib
from html.parser import HTMLParser
root=pathlib.Path(__file__).resolve().parents[1];app=root/'apps/system/jsketcher'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.extend(v for k,v in attrs if k=='href')
p=Links();p.feed((app/'SOURCE-INDEX.html').read_text());items=set(json.loads((app/'app.json').read_bytes())['assets']);prefix='node_modules/jsketcher-build/'
assert len(p.links)>20 and len(p.links)==len(set(p.links))
assert prefix+'SOURCE-INDEX.html' not in items and all(prefix+x not in items for x in p.links)
source=(app/'index.mjs').read_text();assert 'openCadSources' in source and "window.open(new URL('./node_modules/jsketcher-build/SOURCE-INDEX.html'" not in source
print('PASS source index and',len(p.links),'linked artifacts excluded from app manifest; signed dialog referenced')
