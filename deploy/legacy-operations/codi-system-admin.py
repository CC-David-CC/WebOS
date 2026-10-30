#!/usr/bin/env python3
"""Publish an operator announcement to the designated SYSTEM channel.

Example: printf '%s' 'The server will restart soon.' | sudo codi-system-admin post
"""
import argparse,json,os,subprocess,sys
from pathlib import Path
PACKAGE=Path('/srv/codi-connected/official-services/chat-ban-review-r3')
PYTHON=Path('/srv/codi-connected/venvs/official-chess-r1/bin/python')
STATE=Path('/var/lib/codi-official/state')
def publish(raw):
 if not isinstance(raw,bytes) or not 1<=len(raw)<=4096:raise ValueError('Announcement must contain 1–4096 UTF-8 bytes')
 try:text=raw.decode('utf-8')
 except UnicodeDecodeError:raise ValueError('Announcement must be valid UTF-8') from None
 if not text.strip() or any(ord(c)<32 and c not in '\n\r\t' or 127<=ord(c)<=159 for c in text):raise ValueError('Announcement cannot be empty or contain control characters')
 command=['/usr/sbin/runuser','-u','codi-official','--',str(PYTHON),'-I','-B',str(PACKAGE/'scripts/official-admin.py'),'--state',str(STATE),'system-post']
 result=subprocess.run(command,input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=True)
 value=json.loads(result.stdout)
 if not isinstance(value,dict) or value.get('status')!='posted':raise ValueError('Publisher did not confirm the announcement')
 return value
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('post',));parser.parse_args()
 if os.geteuid()!=0:raise SystemExit('Run as the server administrator (sudo).')
 try:print(json.dumps(publish(sys.stdin.buffer.read(4097))))
 except (ValueError,subprocess.SubprocessError) as error:raise SystemExit('Announcement was not confirmed: '+str(error)) from None
if __name__=='__main__':main()
