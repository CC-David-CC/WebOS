#!/usr/bin/env python3
"""Run only the explicitly targeted G-code live smoke with private credentials.

This creates two random accounts. It never deletes them. The receipt allows the
separately reviewed, scoped cleanup tool to check and remove exactly those two.
On failure credentials are retained in a private directory for recovery.
"""
import argparse, json, os, secrets, subprocess, sys, tempfile
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--live',action='store_true',help='Explicitly target https://ksu.codes/')
parser.add_argument('--node',required=True,help='Absolute path to the Node executable')
parser.add_argument('--cdp',default='http://127.0.0.1:19778',help='Loopback Chromium debugging URL')
parser.add_argument('--phone',action='store_true',help='Use an emulated phone viewport')
args=parser.parse_args()
if not args.live:parser.error('Pass --live to explicitly target the site')
node=Path(args.node)
if not node.is_absolute() or not node.is_file() or not os.access(node,os.X_OK):parser.error('--node must be an absolute executable path')
root=Path(__file__).resolve().parents[1];driver=root/'tests/gcode-live-only-smoke.mjs'
if not driver.is_file():raise SystemExit('Smoke driver missing')
os.umask(0o077);directory=Path(tempfile.mkdtemp(prefix='codi-gcode-live-smoke-',dir='/tmp'));directory.chmod(0o700)
credentials=directory/'credentials.json';receipt=directory/'receipt.jsonl'
values={'GCODE_SMOKE_USER_A':'smoke'+secrets.token_hex(10),'GCODE_SMOKE_USER_B':'smoke'+secrets.token_hex(10),'GCODE_SMOKE_PASS_A':secrets.token_urlsafe(15),'GCODE_SMOKE_PASS_B':secrets.token_urlsafe(15)}
fd=os.open(credentials,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f:json.dump(values,f);f.flush();os.fsync(f.fileno())
env={key:value for key,value in os.environ.items() if not key.startswith('GCODE_')};env.update(values);env.update({'GCODE_SMOKE_URL':'https://ksu.codes/','GCODE_LIVE_SMOKE':'yes','GCODE_REGISTER_LIVE':'yes','GCODE_SMOKE_RECEIPT':str(receipt),'CODI_TEST_CDP':args.cdp})
if args.phone:env['GCODE_PHONE']='yes'
print('Private smoke directory:',directory,flush=True)
try:result=subprocess.run([str(node),str(driver)],cwd=root,env=env).returncode
except BaseException:
 print('Smoke interrupted. Credentials remain in the private directory for recovery.',file=sys.stderr,flush=True);raise
if result:
 print('Smoke failed. Credentials remain in the private directory for recovery; do not delete accounts without reviewing the receipt and files.',file=sys.stderr,flush=True);sys.exit(result)
try:
 records=[json.loads(line) for line in receipt.read_text().splitlines() if line.strip()]
 if len(records)!=3 or set(records[2])!={'quiesced_at'} or any(records[i].get('username')!=values['GCODE_SMOKE_USER_'+('A' if i==0 else 'B')] for i in range(2)):raise ValueError('incomplete or mismatched receipt')
except Exception as error:
 print('Smoke receipt is incomplete; credentials remain for recovery:',error,file=sys.stderr,flush=True);sys.exit(1)
credentials.unlink();print('Smoke passed. Receipt retained at:',receipt,flush=True)
