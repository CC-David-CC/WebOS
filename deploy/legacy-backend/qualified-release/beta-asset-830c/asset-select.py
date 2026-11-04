"""Fail-closed selection of exact e7/3ad→gate→830c recovery states.

Protected caller must hold the existing host lock, read all inputs with
custody checks, and load pinned sources. This module does not gate a site.
"""
from beta_transaction import _decode
from asset_floor import OLD,NEW,ORIGINAL_BASE
EXPECTED={'version':1,'baseline':OLD,'candidate':NEW}
ORIGINAL={'version':1,'baseline':ORIGINAL_BASE,'candidate':OLD}

def same(record,expected):return isinstance(record,dict) and type(record.get('version')) is int and record==expected

def select(*,snapshots,current,original_floor,asset_floor,asset_journal,nested_journal,other_pending):
 if other_pending:raise ValueError('Conflicting hosting operation pending')
 if not same(original_floor,ORIGINAL):raise ValueError('Original OPFS floor changed')
 if set(snapshots)!={'baseline','gate','candidate'} or set(current)!={'common','manifest','caddy'}:raise ValueError('Invalid exact asset snapshots')
 if asset_floor is not None and not same(asset_floor,EXPECTED):raise ValueError('Invalid asset floor')
 if asset_journal is not None and not same(asset_journal,EXPECTED):raise ValueError('Invalid asset journal')
 if asset_floor is None and asset_journal is None:
  if nested_journal is not None or current!=snapshots['baseline']:raise ValueError('Unexpected pre-transition state')
  return 'baseline'
 allowed=('gate','candidate') if asset_floor is not None else ('baseline','gate')
 if asset_floor is None and asset_journal is None:raise ValueError('Missing asset transition')
 if nested_journal is None:
  hits=[n for n in allowed if current==snapshots[n]]
  if len(hits)!=1:raise ValueError('Unknown or disallowed asset route')
  return hits[0]
 j=nested_journal
 if not isinstance(j,dict) or type(j.get('version')) is not int:raise ValueError('Invalid nested asset journal')
 try:a,b=_decode(j['old']),_decode(j['new'])
 except Exception as e:raise ValueError('Invalid nested asset endpoints') from e
 fields={'version','phase','old','new','timer','caddy_started','backup'}
 pairs=[(snapshots['gate'],snapshots['candidate'],1,None),(snapshots['candidate'],snapshots['gate'],2,'gate-only')] if asset_floor is not None else [(snapshots['baseline'],snapshots['gate'],1,None),(snapshots['gate'],snapshots['baseline'],1,None)]
 matches=[(v,p) for x,y,v,p in pairs if (a,b)==(x,y)]
 if len(matches)!=1:raise ValueError('Unpinned nested asset endpoints')
 version,policy=matches[0];expected_fields=fields|({'policy'} if policy else set())
 if set(j)!=expected_fields or j.get('version')!=version or j.get('policy')!=policy or j.get('phase') not in ('prepared','committed') or type(j.get('caddy_started')) is not bool or not isinstance(j.get('backup'),str) or not j['backup']:raise ValueError('Invalid nested asset journal metadata')
 timer=j.get('timer')
 if not isinstance(timer,dict) or set(timer)!={'active','enabled'} or any(type(v) is not bool for v in timer.values()):raise ValueError('Invalid nested timer state')
 if not all(current[k] in (a[k],b[k]) for k in current):raise ValueError('Mixed unpinned asset route')
 return 'nested'
