#!/usr/bin/env python3
"""Kill and restart an owned local runtime; not a power-loss test."""
import json,select,sqlite3,subprocess,sys,tempfile,urllib.request,urllib.error
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from codiauth import jose
from steward.official_registry import OfficialChannelRegistry
from steward.official_upload_policy import initialize as initialize_policy
from steward.official_access import initialize as initialize_access

fixture=json.loads((ROOT/'.build/checks/official-browser-offer-export-r1.json').read_text())['offerFixture'];offer=fixture['offer'];channel=offer['channel'];origin='http://127.0.0.1:8091'
with tempfile.TemporaryDirectory(prefix='codi-runtime-process-') as temp:
    root=Path(temp);db=root/'official.sqlite';ledger=root/'access.sqlite';store=OfficialChannelRegistry(db);store._db.execute('INSERT INTO official_channels VALUES(?,?,?,?,?,?,?)',(channel,fixture['genesisHash'],fixture['policyWire'],'fixture','',1,0));initialize_policy(db);initialize_access(ledger)
    for node in offer['nodes']:store.stage_node(channel,node['cid'],node['wire'])
    store.append_staged_history(channel,expected_head=offer['expectedHead'],history=offer['history'],height=offer['height'],head=offer['head']);key=ec.generate_private_key(ec.SECP256R1());policy={'mode':'server','issuer':origin,'authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(key)}]};config={'database':str(db),'ledger':str(ledger),'policy':policy};children=[]
    def launch():
        child=subprocess.Popen([sys.executable,str(ROOT/'scripts/fixtures/official-runtime-child.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);children.append(child);child.stdin.write(json.dumps(config)+'\n');child.stdin.flush()
        if not select.select([child.stdout],[],[],10)[0]:raise AssertionError('Runtime startup timeout')
        line=child.stdout.readline();assert line,child.stderr.read();return child,json.loads(line)['port']
    def request(port,path,data=None):
        body=None if data is None else json.dumps(data).encode();headers={'Host':'127.0.0.1:8091','Origin':origin,**({'Content-Type':'application/json'} if body is not None else {})};req=urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=body,headers=headers)
        with urllib.request.urlopen(req,timeout=10) as response:return json.loads(response.read())
    try:
        first,first_port=launch();assert request(first_port,'/official-head?channel='+channel)['head']==offer['head']
        def admin(action):
            result=subprocess.run([sys.executable,str(ROOT/'scripts/official-admin.py'),'--state',str(root),action,channel],capture_output=True,text=True)
            assert result.returncode==0,result.stderr
        admin('disable')
        try:request(first_port,'/official-head?channel='+channel);raise AssertionError('Disabled channel remains available')
        except urllib.error.HTTPError as error:assert error.code==404
        assert request(first_port,'/official-directory?after=&limit=16')['items']==[]
        admin('enable');assert request(first_port,'/official-head?channel='+channel)['head']==offer['head']
        challenge=request(first_port,'/official-ingest/challenge',{'key':jose.public_jwk(key),'request_sha256':jose.digest('fixture')});first.kill();first.wait(timeout=5);assert first.returncode<0
        second,second_port=launch();assert second.pid!=first.pid and request(second_port,'/official-head?channel='+channel)['head']==offer['head']
        with sqlite3.connect(ledger) as access:assert access.execute('SELECT request_sha FROM official_access_challenges WHERE nonce=?',(challenge['nonce'],)).fetchone()==(jose.digest('fixture'),)
        assert store.replayed_head(channel)['state']==fixture['state'];second.kill();second.wait(timeout=5)
    finally:
        for child in children:
            if child.poll() is None:child.kill();child.wait(timeout=5)
            for pipe in (child.stdin,child.stdout,child.stderr):
                if pipe:pipe.close()
        store.close()
print(json.dumps({'status':'PASS','scope':'operator disable/enable reflected by running local runtime; process killed after committed history and replacement recovered verified head and unused challenge; not power-loss or in-flight upload'}))
