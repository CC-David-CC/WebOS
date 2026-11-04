#!/usr/bin/env python3
"""Verify disabled main launcher's embedded source pins against checkout."""
import ast,hashlib
from pathlib import Path
here=Path(__file__).resolve().parent;ops=here.parent/'beta-isolated-hosting/ops';tree=ast.parse((here/'main-launcher.py').read_text())
def constant(name):return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
for name,pin in constant('PINS').items():
 path=(here if name in ('forward-transaction.py','render-inventory.py') else ops)/name
 assert hashlib.sha256(path.read_bytes()).hexdigest()==pin,name
assert hashlib.sha256((here/'main-successor-preflight.py').read_bytes()).hexdigest()==constant('SUCCESSOR_PREFLIGHT')
assert hashlib.sha256((here/'webctl-main-guard.py').read_bytes()).hexdigest()==constant('GUARD')
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='ctl' and n.func.attr=='load' and not n.args and not n.keywords for n in ast.walk(tree)), 'do not use imported default manifest path'
print('PASS all disabled launcher source pins')
