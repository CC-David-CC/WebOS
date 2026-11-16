#!/usr/bin/env python3
"""Build exact review-only enabled main launcher; no host installation."""
import hashlib,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent;raw=(here/'main-launcher.py').read_bytes()
if hashlib.sha256(raw).hexdigest()!='1db014d4d207fb746f52849bd7378a02aaf1b574d9585cb1d262214c74085c26':raise ValueError('Reviewed disabled launcher changed')
line=b" raise ValueError('Research launcher disabled until coordinated beta successor and qualification')\n"
if raw.count(line)!=1:raise ValueError('Expected exact disable line')
enabled=raw.replace(line,b'',1);out=Path(sys.argv[1]);out.mkdir(mode=0o700);(out/'main-launcher.py').write_bytes(enabled)
record={'source':hashlib.sha256(raw).hexdigest(),'enabled':hashlib.sha256(enabled).hexdigest(),'removed':'single reviewed research-only hard-disable line'}
(out/'manifest.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n');print(json.dumps(record,sort_keys=True))
