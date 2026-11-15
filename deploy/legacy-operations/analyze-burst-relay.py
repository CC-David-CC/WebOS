#!/usr/bin/env python3
"""Summarize outgoing relay attempts from an existing burst receipt."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('receipt',type=Path);p.add_argument('--sender',default='j');a=p.parse_args();j=json.loads(a.receipt.read_text());b=j['burst'];origin=b['clicks'][a.sender]['at'];rows=b['wireMetadata'][a.sender];attempts=[]
for event in rows:
 if event.get('direction')!='send' or event.get('method') not in ('submit','relay-submit'):continue
 replies=[{'atSeconds':round((reply['start']-origin)/1000,3),'op':reply['op'],'code':reply.get('code')} for reply in rows if reply.get('direction')=='receive' and reply.get('request')==event.get('request')]
 attempts.append({'atSeconds':round((event['start']-origin)/1000,3),'method':event['method'],'replies':replies})
print(json.dumps({'sender':a.sender,'attempts':attempts,'scope':'Observed frames only; peer identities, message bodies and unobserved frames excluded.'},indent=2))
