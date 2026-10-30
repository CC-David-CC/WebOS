#!/usr/bin/env python3
"""Signed metadata storage, search, restart and rejection checks; no server deployment."""
import json,os,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from steward.publisher import PublicChannelDirectory
now=int(time.time());v=json.loads(subprocess.check_output([str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'),str(ROOT/'scripts/public-directory-signed-fixture.mjs'),str(now)],text=True));checks=[]
def check(name,ok):
 if not ok:raise AssertionError(name)
 checks.append(name)
def refused(f):
 try:f();return False
 except ValueError:return True
with tempfile.TemporaryDirectory(prefix='codi-public-directory-') as tmp:
 path=Path(tmp);os.chmod(path,0o700);d=PublicChannelDirectory(path);scope=v['scope'];other=v['otherScope'];d.publish(scope,[v['a']['listing'],v['b']['listing'],v['c']['listing']],now);page=d.search(scope,'alpha','',1);page2=d.search(scope,'alpha',page['next'],1)
 dbfile=path/'public-channels.sqlite3';before=(dbfile.stat().st_mtime_ns,dbfile.read_bytes());d.publish(scope,[v['a']['listing']],now+1);check('identical listing causes no database modification',before==(dbfile.stat().st_mtime_ns,dbfile.read_bytes()))
 check('search pages find both matching public references',len(page['items'])==1 and len(page2['items'])==1 and page['next'] and page2['next'] is None)
 check('another public scope cannot see these references',not d.search(other,'','',2)['items'])
 check('private channels cannot be listed',refused(lambda:d.publish(scope,[v['privateChannel']['listing']],now)))
 bad=v['b']['listing'][:-1]+('A' if not v['b']['listing'].endswith('A') else 'B');check('modified signature refuses the whole batch',refused(lambda:d.publish(scope,[v['update'],bad],now+1)) and not d.search(scope,'updated','',2)['items'])
 d.publish(scope,[v['update']],now+1);d.publish(scope,[v['a']['listing']],now+2);check('older signed announcement cannot roll back a changed description',len(d.search(scope,'updated','',2)['items'])==1)
 check('conflicting same-time update is rejected',refused(lambda:d.publish(scope,[v['conflict']],now+2)))
 d.close();d=PublicChannelDirectory(path);page=d.search(scope,'updated','',2);check('signed public reference survives restart and retains original verification time',len(page['items'])==1 and page['items'][0]['verifiedAt']==now+1)
 check('expired listing cannot be published anew',refused(lambda:d.publish(scope,[v['a']['listing']],now+301)))
 check('past references stay searchable when the owner is offline',len(d.search(scope,'updated','',2)['items'])==1);d.close()
print(json.dumps({'status':'PASS','checks':checks,'scope':'temporary SQLite and signed WebCrypto descriptors; no chat history or live service'}))
