"""Retain unchanged canonical Files/Text code in a newly built CAD catalog."""
import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--prior',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
catalog=json.loads((a.output/'apps.json').read_text());prior=json.loads((a.prior/'apps.json').read_text())
assert [x['id'] for x in catalog['apps']]==['jsketcher']
for row in prior['apps']:
 if row['id'] not in ['files','text']:continue
 shutil.copytree(a.prior/'apps'/row['id'],a.output/'apps'/row['id']);catalog['apps'].append(row)
assert sorted(x['id'] for x in catalog['apps'])==['files','jsketcher','text']
(a.output/'apps.json').write_text(json.dumps(catalog,indent=2)+'\n')
print('catalogSHA256',hashlib.sha256((a.output/'apps.json').read_bytes()).hexdigest())
