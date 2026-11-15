#!/usr/bin/env python3
"""Nine workstation browsers plus the user's phone in a disposable channel."""
import json,os,secrets,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];tag=secrets.token_hex(6);db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';helper='/tmp/temporary-official-test-channel.py';created=False
def control(action):return subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','-u','codi-official','/srv/codi-connected/venvs/official-chess-r1/bin/python','-B',helper,action,tag,db,keys,package,'phone-test'],check=True,capture_output=True,text=True,timeout=30).stdout.strip()
try:
 value=json.loads(control('create'));created=True;assert value['label']=='Temporary test '+tag;print('Created isolated phone test channel',flush=True)
 env=os.environ.copy();env['CODI_TEMP_CHANNEL_LABEL']=value['label'];env['CODI_PHONE_TAG']=tag;env['CODI_TEST_CHAT_ONLY']='1'
 result=subprocess.run(['python3',str(ROOT/'scripts/live-temp-phone-nine-check.py')],env=env,timeout=720)
 if result.returncode:raise RuntimeError('Phone group test did not complete')
finally:
 if created:
  try:print(control('remove'),flush=True)
  except Exception as error:print('Temporary channel preserved for inspection; cleanup failed:',error,flush=True);raise
