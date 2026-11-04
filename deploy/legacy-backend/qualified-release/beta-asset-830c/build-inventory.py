#!/usr/bin/env python3
"""Derive narrowly pinned inventory for 3ad/830c gate transitions."""
import hashlib,sys
from pathlib import Path
ops=Path(__file__).resolve().parents[2]/'beta-isolated-hosting/ops';raw=(ops/'render_inventory.py').read_bytes()
if hashlib.sha256(raw).hexdigest()!='c6a14a1d3ddbe52a592ecc2e519d430ca654056af99b3af1a92e43dcbb4c0c35':raise ValueError('inventory baseline changed')
s=raw.decode();old='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';new='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0'
for name,count in (('olddata',1),('newdata',2)):
 anchor=name+".get('codi_beta_opfs')!='"+old+"'"
 if s.count(anchor)!=count:raise ValueError('inventory policy anchor changed')
 s=s.replace(anchor,name+".get('codi_beta_opfs') not in ('"+old+"','"+new+"')",1)
out=Path(sys.argv[1]);out.mkdir(mode=0o700);(out/'render_inventory.py').write_text(s);print(hashlib.sha256(s.encode()).hexdigest())
