#!/usr/bin/env python3
"""Document the current prepared app's static source-link exposure."""
import json,pathlib
from html.parser import HTMLParser
root=pathlib.Path(__file__).resolve().parents[1];app=root/'apps/system/jsketcher'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.extend(v for k,v in attrs if k=='href')
p=Links();p.feed((app/'SOURCE-INDEX.html').read_text());data=json.loads((app/'app.json').read_bytes());items=set(data['assets']) if 'assets' in data else set(data['files']);prefix='node_modules/jsketcher-build/'
assert len(p.links)>10 and all(prefix+x in items for x in p.links);source=(app/'index.mjs').read_text();assert "window.open(new URL('./node_modules/jsketcher-build/SOURCE-INDEX.html',import.meta.url).href" in source
print('CONFIRMED source index and',len(p.links),'linked artifacts packaged as static app assets; menu uses direct window.open')
