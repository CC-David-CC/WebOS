#!/usr/bin/env python3
"""Fault-inject official switch journal with temporary fake system effects."""
import json,sys,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from origin_service import official_management as m,official_backend_custody,maintenance,deployment
class Crash(BaseException):pass
class Op:
 def __init__(self):self.stops=[];self.starts=[]
 def atomic(self,path,data,mode=0o600):Path(path).write_bytes(data)
 def read_owned(self,path,*a):return Path(path).read_bytes()
 def unit(self,c,role):return role+'.service'
 def render(self,c,role):return ('enabled='+str(c.get('officialChannels',False))).encode()
 def installed(self,c):pass
 def stop(self,c,roles):self.stops.append(list(roles))
 def systemctl(self,*args):
  if args[0]=='show':return 'inactive'
  if args[0]=='start':self.starts.append(args[1:])
  return ''
 def ready(self,c,roles):pass
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);units=root/'units';units.mkdir();path=root/'managed.json';base={'maintenance':1,'unitDir':str(units),'release':'old'};op=Op();path.write_text(json.dumps(base));checks=[]
 with patch.object(m,'check_backend',return_value=True),patch.object(official_backend_custody,'verify_listener',return_value=123) as custody,patch.object(maintenance,'guard'),patch.object(maintenance,'guard_epoch'),patch.object(maintenance,'sync_directory'),patch.object(deployment,'syntax'),patch.object(deployment,'active',return_value=['issuer']):
  try:m.configure(op,base,path,True,backend_port=18925);raise AssertionError('missing custody pins accepted')
  except ValueError:pass
  pins={'unit':'official.service','unit_path':'/unit','unit_sha256':'0'*64,'uid':123,'argv':['runtime']}
  def interrupt(name):
   if name=='switching':raise Crash()
  try:m.configure(op,base,path,True,backend_port=18925,backend_custody=pins,phase=interrupt)
  except Crash:pass
  else:raise AssertionError('interruption not injected')
  current=json.loads(path.read_text());result=m.recover(op,current,path);assert result['status']=='official-switch-rolled-back' and json.loads(path.read_text())==base and not (root/'maintenance.json').exists();checks.append('interrupted switch restores prior issuer config')
  def committed(name):
   if name=='committed':raise Crash()
  try:m.configure(op,base,path,True,backend_port=18925,backend_custody=pins,phase=committed)
  except Crash:pass
  else:raise AssertionError('commit interruption not injected')
  current=json.loads(path.read_text());result=m.recover(op,current,path);assert result['status']=='official-switch-committed-recovered' and json.loads(path.read_text())['officialChannels'] is True;checks.append('committed switch resumes enabled state')
  result=m.configure(op,json.loads(path.read_text()),path,False);assert result['status']=='official-switch-configured' and 'officialChannels' not in json.loads(path.read_text());checks.append('disable restores omitted setting')
  assert all(v==['issuer'] for v in op.stops) and all(v==('issuer.service',) for v in op.starts);checks.append('switch only restarts issuer')
  assert custody.call_count==2 and all(call.kwargs['port']==18925 for call in custody.call_args_list);checks.append('enable requires listener custody pins before switch')
print(json.dumps({'status':'PASS','checks':checks,'scope':'Actual journal logic with temporary files and mocked process/syntax/readiness; no live systemd'}))
