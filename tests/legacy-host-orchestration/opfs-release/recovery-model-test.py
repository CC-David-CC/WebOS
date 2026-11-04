#!/usr/bin/env python3
import importlib.util,pathlib
p=pathlib.Path(__file__).with_name('recovery-model.py');spec=importlib.util.spec_from_file_location('model',p);m=importlib.util.module_from_spec(spec);import sys;sys.modules[spec.name]=m;spec.loader.exec_module(m)
a=m.State();b=m.gate(a);c=m.commit_floor(b,candidate_verified=True,baseline_verified=True);d=m.expose_candidate(c,candidate_verified=True)
for state in (a,b):assert m.recover(state,candidate_verified=False,baseline_verified=True)=='restore-guarded-v1'
for state in (c,d):
 assert m.recover(state,candidate_verified=True,baseline_verified=True)=='forward-candidate'
 assert m.recover(state,candidate_verified=False,baseline_verified=True)=='remain-gated'
for call in (lambda:m.commit_floor(a,candidate_verified=True,baseline_verified=True),lambda:m.commit_floor(b,candidate_verified=False,baseline_verified=True),lambda:m.expose_candidate(b,candidate_verified=True),lambda:m.recover(m.State(candidate_exposed=True),candidate_verified=True,baseline_verified=True)):
 try:call();raise AssertionError('unsafe transition accepted')
 except ValueError:pass
print('PASS abstract recovery invariants: pre-floor rollback; post-floor forward or remain gated')
