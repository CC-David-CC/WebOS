#!/usr/bin/env python3
"""Summarize bounded RPC metadata from a ten-browser burst receipt."""
import argparse,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('receipt',type=Path);args=p.parse_args();receipt=json.loads(args.receipt.read_text());burst=receipt['burst'];assert 'wireMetadata' in burst
out={}
for side,events in burst['wireMetadata'].items():
 pending={};completed=[]
 for event in events:
  request=event.get('request');method=event.get('method');op=event.get('op')
  if event.get('direction')=='send' and op=='call' and method in ('submit','relay-submit') and request:pending[request]=event
  elif event.get('direction')=='receive' and op in ('error','result') and request in pending:
   start=pending.pop(request);completed.append({'method':start['method'],'outcome':event.get('code') if op=='error' else 'result','seconds':round((event['start']-start['start'])/1000,3)})
 out[side]={'completed':completed,'unmatchedSent':len(pending)}
print(json.dumps({'scope':'Observed member-link RPC metadata; no payloads. Link hooks can miss frames and calls cannot be assigned to specific messages.','participants':out},indent=2))
