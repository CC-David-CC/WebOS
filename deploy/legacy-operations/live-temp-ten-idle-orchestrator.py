#!/usr/bin/env python3
"""Test ten local browsers on two IP paths in an isolated official channel."""
import json,os,secrets,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];tag=secrets.token_hex(6);remote='box-webhost';helper='/tmp/temporary-official-test-channel.py';db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';proxy=None;created=False
def control(action):return subprocess.run(['ssh','-o','BatchMode=yes',remote,'sudo','-n','-u','codi-official','/srv/codi-connected/venvs/official-chess-r1/bin/python','-B',helper,action,tag,db,keys,package],check=True,capture_output=True,text=True,timeout=30).stdout.strip()
try:
 value=json.loads(control('create'));created=True;assert value['label']=='Temporary test '+tag;print('Created isolated test channel',flush=True)
 proxy=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-D','127.0.0.1:19542','maint@10.0.7.105'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 end=time.monotonic()+25
 while time.monotonic()<end:
  if proxy.poll() is not None:raise RuntimeError('Second network proxy stopped')
  try:
   ip=subprocess.check_output(['curl','-4','-fsS','--max-time','5','--socks5-hostname','127.0.0.1:19542','https://api.ipify.org'],stderr=subprocess.DEVNULL,text=True,timeout=7).strip()
   if ip=='104.180.210.36':break
  except (OSError,subprocess.SubprocessError):pass
  time.sleep(.3)
 else:raise TimeoutError('Second network path unavailable')
 print('Verified second outbound IP',ip,flush=True)
 env=os.environ.copy();env['CODI_TEMP_CHANNEL_LABEL']=value['label'];env['CODI_TEST_CHAT_ONLY']='1'
 result=subprocess.run(['python3',str(ROOT/'scripts/live-temp-ten-idle-check.py')],env=env,timeout=420)
 if result.returncode:raise RuntimeError('Ten-session test failed')
finally:
 if proxy:
  proxy.terminate()
  try:proxy.wait(5)
  except subprocess.TimeoutExpired:proxy.kill();proxy.wait()
 if created:
  try:print(control('remove'),flush=True)
  except Exception as error:print('Temporary channel preserved for inspection; cleanup failed:',error,flush=True);raise
