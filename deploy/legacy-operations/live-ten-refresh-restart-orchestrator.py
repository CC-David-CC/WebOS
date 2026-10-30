#!/usr/bin/env python3
"""Run a bounded live ten-session service restart in a disposable channel."""
import json,os,secrets,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];tag=secrets.token_hex(6);db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';helper='/tmp/temporary-restart-test-channel-r1.py';created=False
def control(action):return subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','-u','codi-official','/srv/codi-connected/venvs/official-chess-r1/bin/python','-B',helper,action,tag,db,keys,package,'history-test'],check=True,capture_output=True,text=True,timeout=30).stdout.strip()
try:
 value=json.loads(control('create'));created=True;assert value['label']=='Temporary test '+tag;print('Created isolated restart test channel',flush=True)
 env=os.environ.copy();env['CODI_TEMP_CHANNEL_LABEL']=value['label'];env['CODI_RESTART_TAG']=tag;env['CODI_TEST_CHAT_ONLY']='1'
 result=subprocess.run(['python3',str(ROOT/'scripts/live-ten-refresh-restart-check.py')],env=env,timeout=420)
 if result.returncode:raise RuntimeError('Service restart group test failed')
finally:
 if created:
  try:print(control('remove'),flush=True)
  except Exception as error:print('Temporary channel preserved for inspection; cleanup failed:',error,flush=True);raise
