#!/usr/bin/env python3
"""Exercise local experimental selection; not consensus or channel recovery."""
import concurrent.futures,json,multiprocessing,os,sqlite3,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from steward.official_controller_recovery_journal import RecoveryJournal
cases=json.loads(subprocess.check_output([ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node',ROOT/'scripts/official-controller-recovery-parity-corpus.mjs'],text=True))
a=next(x for x in cases if x['name']=='valid');b=next(x for x in cases if x['name']=='competing valid proposal');channel=a['trusted']['channel']
with tempfile.TemporaryDirectory(prefix='codi-recovery-journal-') as folder:
    path=Path(folder)/'selection.sqlite';j=RecoveryJournal(path);j.initialize(a['trusted'])
    try:j.select(channel,a['wire'],a['acceptance'],before_commit=lambda:(_ for _ in ()).throw(RuntimeError('injected interruption')))
    except RuntimeError:pass
    else:raise AssertionError('interruption unexpectedly committed')
    assert j.context(channel)==a['trusted'];j.close()
    def crash_before_commit():
        store=RecoveryJournal(path)
        store.select(channel,a['wire'],a['acceptance'],before_commit=lambda:os._exit(17))
    process=multiprocessing.get_context('fork').Process(target=crash_before_commit);process.start();process.join(15);assert process.exitcode==17
    j=RecoveryJournal(path);assert j.context(channel)==a['trusted'];assert j.db.execute('SELECT COUNT(*) FROM recovery_selections').fetchone()[0]==0;j.close()
    def attempt(c):
        store=RecoveryJournal(path)
        try:
            try:return {'ok':True,'value':store.select(channel,c['wire'],c['acceptance'])}
            except ValueError:return {'ok':False}
        finally:store.close()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,[a,b]))
    assert sum(r['ok'] for r in results)==1
    winner=a if results[0]['ok'] else b;loser=b if results[0]['ok'] else a
    j=RecoveryJournal(path);state=j.context(channel);assert state['generation']==1 and state['controller']==results[0 if results[0]['ok'] else 1]['value']['replacement']
    assert j.select(channel,winner['wire'],winner['acceptance'])['replacement']==state['controller']
    try:j.select(channel,loser['wire'],loser['acceptance'])
    except ValueError:pass
    else:raise AssertionError('competing stale proposal accepted')
    assert j.db.execute('SELECT COUNT(*) FROM recovery_selections').fetchone()[0]==1;j.close()
    j=RecoveryJournal(path);assert j.context(channel)==state;j.close()
print(json.dumps({'status':'PASS','checks':['interrupted transaction rolls back','process death before commit rolls back','two concurrent proposals select one','exact retry is idempotent','competing proposal is stale','selected state survives reopen'],'scope':'local SQLite prototype; no channel authority, history synchronization, validator fencing or deployment'}))
