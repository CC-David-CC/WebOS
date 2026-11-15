#!/usr/bin/env python3
"""Operator policy file behavior, including fail-closed invalid inputs."""
import asyncio,importlib.util,json,os,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('serve_steward',ROOT/'scripts/serve-steward.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Server:
 def __init__(self):self.values=[]
 async def set_anonymous_allowed(self,v):self.values.append(v)
async def run():
 checks=[]
 def check(name,value):assert value,name;checks.append(name);print(name,flush=True)
 with tempfile.TemporaryDirectory(prefix='codi-gate-') as temp:
  path=Path(temp)/'policy';path.write_text('enabled\n');path.chmod(0o644);check('valid owned enabled policy is read',m.anonymous_policy(path,owner=os.getuid()) is True)
  path.chmod(0o666)
  try:m.anonymous_policy(path,owner=os.getuid());raise AssertionError('writable policy accepted')
  except ValueError:check('group or world writable policy is refused',True)
  path.chmod(0o644);Path(temp).chmod(0o777)
  try:m.anonymous_policy(path,owner=os.getuid());raise AssertionError('writable directory accepted')
  except ValueError:check('writable policy directory is refused',True)
  Path(temp).chmod(0o700);link=Path(temp)/'link';link.symlink_to(path)
  try:m.anonymous_policy(link,owner=os.getuid());raise AssertionError('symlink accepted')
  except OSError:check('symlink policy is refused',True)
  server=Server();watcher=asyncio.create_task(m.watch_anonymous_policy(server,path,owner=os.getuid()))
  try:
   await asyncio.sleep(1.2);path.write_text('disabled\n');await asyncio.sleep(1.2);path.write_text('invalid\n');await asyncio.sleep(1.2);path.write_text('enabled\n');await asyncio.sleep(1.2);path.unlink();await asyncio.sleep(1.2)
   check('watcher disables and re-enables with fail-closed invalid and missing input',server.values==[True,False,True,False])
  finally:watcher.cancel();await asyncio.gather(watcher,return_exceptions=True)
 out=ROOT/'.build/checks/steward-anonymous-file-r1-result.json';out.write_text(json.dumps({'status':'PASS','checks':checks,'productionChanged':False},indent=2)+'\n')
if __name__=='__main__':asyncio.run(run())
