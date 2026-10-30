#!/usr/bin/env python3
"""Disposable policy checks; these switches apply only to official uploads."""
import tempfile,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from steward.official_registry import OfficialChannelRegistry
from steward.official_upload_policy import OfficialUploadPolicy,initialize
from room_service.contract import Principal

with tempfile.TemporaryDirectory() as temp:
    path=Path(temp)/'official.sqlite';store=OfficialChannelRegistry(path);channel='A'*43;other='B'*42+'A'
    store._db.execute('INSERT INTO official_channels VALUES(?,?,?,?,?,?,?)',(channel,'A'*43,'fixture','test','',1,0))
    initialize(path);policy=OfficialUploadPolicy(path);account='user:'+str(uuid.uuid4());anon=Principal({'kind':'anonymous','sub':'anon:'+str(uuid.uuid4())},100);registered=Principal({'kind':'registered','sub':account},100)
    assert policy(anon,channel) and policy(registered,channel) and not policy(registered,other)
    policy.set_anonymous(False);assert not OfficialUploadPolicy(path)(anon,channel) and policy(registered,channel)
    policy.set_ban(channel,account,True);assert not policy(registered,channel)
    policy.set_ban(channel,account,False);assert policy(registered,channel)
    policy.set_ban('*',account,True);assert not OfficialUploadPolicy(path)(registered,channel)
    policy.set_ban('*',account,False);policy.set_anonymous(True);store.set_enabled(channel,False);assert not policy(registered,channel) and not policy(anon,channel)
    for bad in ('root','user:not-a-uuid','anon:'+str(uuid.uuid4())):
        try:policy.set_ban('*',bad,True);raise AssertionError('invalid ban accepted')
        except ValueError:pass
    store.close()
print('PASS: official upload scope, registered bans, anonymous switch, restart and disabled channel')
