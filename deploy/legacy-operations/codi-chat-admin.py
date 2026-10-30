#!/usr/bin/env python3
"""Administrator controls for General chess chat on the KSU test host."""
import argparse,json,os,re,sqlite3,subprocess
from pathlib import Path
PACKAGE=Path('/srv/codi-connected/official-services/chat-ban-review-r3');PYTHON=Path('/srv/codi-connected/venvs/official-chess-r1/bin/python');STATE=Path('/var/lib/codi-official/state');ACCOUNT_DB=Path('/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3')
def current_channel(database):
 # The featured game and its chat are provisioned together. Resolve that
 # association each time so replacing a test chat cannot silently leave the
 # administrator controlling its retired predecessor.
 with sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True,timeout=10) as db:
  db.execute('BEGIN');row=db.execute('SELECT invitation FROM official_featured_game WHERE version=1').fetchone()
  if not row or not isinstance(row[0],str) or len(row[0])>262144:raise ValueError('Current featured game is unavailable')
  try:channel=json.loads(row[0])['chat']['config']['channel']
  except (ValueError,KeyError,TypeError):raise ValueError('Current featured chat is invalid') from None
  if not isinstance(channel,str) or not re.fullmatch(r'[A-Za-z0-9_-]{43}',channel):raise ValueError('Current featured chat is invalid')
  listing=db.execute('SELECT label,enabled FROM official_channels WHERE channel=?',(channel,)).fetchone()
  if listing!=('General chess chat',1):raise ValueError('Featured chat is not the enabled General chess chat')
  return channel
def run(script,*args):
 result=subprocess.run(['/usr/sbin/runuser','-u','codi-official','--',str(PYTHON),'-I','-B',str(PACKAGE/'scripts'/script),*map(str,args)],check=True,capture_output=True,text=True,timeout=60);return json.loads(result.stdout)
def account(username):
 if not isinstance(username,str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{2,27}',username):raise ValueError('Username must be 3–28 letters or numbers and start with a letter')
 with sqlite3.connect(ACCOUNT_DB.resolve().as_uri()+'?mode=ro',uri=True,timeout=10) as db:row=db.execute('SELECT subject FROM accounts WHERE username=?',(username.lower(),)).fetchone()
 if not row:raise ValueError('Registered account not found')
 return row[0]
def main():
 if os.geteuid()!=0:raise ValueError('Run as the server administrator')
 parser=argparse.ArgumentParser(description=__doc__);actions=parser.add_subparsers(dest='action',required=True);actions.add_parser('list');message=actions.add_parser('mark-message');message.add_argument('id');author=actions.add_parser('mark-author');author.add_argument('id')
 for name in ('ban','unban'):actions.add_parser(name).add_argument('username')
 args=parser.parse_args()
 channel=current_channel(STATE/'official.sqlite')
 if args.action in ('ban','unban'):
  result=run('official-set-account-ban.py','--database',STATE/'official.sqlite','--validator-key-dir',STATE/'validator-keys','--channel',channel,'--issuer','https://ksu.codes','--subject',account(args.username),args.action);print(json.dumps(result));return
 common=['--database',STATE/'official.sqlite','--validator-key-dir',STATE/'validator-keys','--channel',channel]
 if args.action=='list':result=run('official-mark-spam.py',*common,'--list')
 elif args.action=='mark-message':result=run('official-mark-spam.py',*common,'--message',args.id)
 else:result=run('official-mark-spam.py',*common,'--author',args.id)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
