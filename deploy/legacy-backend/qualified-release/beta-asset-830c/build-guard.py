#!/usr/bin/env python3
"""Derive exact 830c-aware guard from reviewed fb27; no installation."""
import hashlib,sys
from pathlib import Path
here=Path(__file__).resolve().parent;raw=(here.parent/'webctl-main-guard.py').read_bytes()
if hashlib.sha256(raw).hexdigest()!='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783':raise ValueError('Guard baseline pin mismatch')
s=raw.decode();OLD='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';NEW='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0';block='b25aa6d01471730a27a73ec85569704f59d20bc7b6c30cb1e371e9b0e570d61c'
def one(a,b):
 global s
 if s.count(a)!=1:raise ValueError('guard anchor changed')
 s=s.replace(a,b)
one("MAIN_RESTRICTION_JOURNAL = STATE/'main-restriction-journal.json'", "MAIN_RESTRICTION_JOURNAL = STATE/'main-restriction-journal.json'\nASSET_FLOOR = STATE/'files-asset-floor.json'\nASSET_JOURNAL = STATE/'files-asset-transition.json'\nASSET_BETA_BLOCK_SHA = '"+block+"'")
anchor='def _assert_v2_beta(data):\n'
new='''def _asset_active():
    try: ASSET_FLOOR.lstat()
    except FileNotFoundError: return False
    parent=ASSET_FLOOR.parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=os.geteuid() or stat.S_IMODE(parent.st_mode)!=0o700: raise ValueError('Unsafe asset floor custody')
    fd=os.open(ASSET_FLOOR,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        a=os.fstat(fd)
        if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_nlink!=1 or a.st_size>4096: raise ValueError('Unsafe asset floor')
        raw=os.read(fd,4097);z=os.fstat(fd)
        if len(raw)!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns): raise ValueError('Asset floor changed')
    finally: os.close(fd)
    record=json.loads(raw)
    if not isinstance(record,dict) or type(record.get('version')) is not int or record!={'version':1,'baseline':\"'''+OLD+'''\",'candidate':\"'''+NEW+'''\"}: raise ValueError('Unrecognized asset floor')
    return True

def _assert_v2_beta(data):
'''
one(anchor,new)
one("    if not _floor_guard_active: return\n    if data.get('codi_beta_opfs')!='"+OLD+"' or data.get('codi_beta_maintenance') is not False:", "    asset_active=_asset_active()\n    if not _floor_guard_active:\n        if asset_active: raise ValueError('Asset floor requires original OPFS floor')\n        return\n    expected='"+NEW+"' if asset_active else '"+OLD+"'\n    if data.get('codi_beta_opfs')!=expected or data.get('codi_beta_maintenance') is not False:")
one("if hashlib.sha256(proposed.encode()).hexdigest()!=BETA_V2_BLOCK_SHA:","if hashlib.sha256(proposed.encode()).hexdigest()!=(ASSET_BETA_BLOCK_SHA if asset_active else BETA_V2_BLOCK_SHA):")
needle="        # Pending work blocks all legacy writes. A durable floor permits\n"
one(needle,"        try: ASSET_JOURNAL.lstat()\n        except FileNotFoundError: pass\n        else: raise RuntimeError('Legacy hosting writes frozen by pending beta asset transition')\n"+needle)
out=Path(sys.argv[1]);out.mkdir(mode=0o700);(out/'webctl.py').write_text(s);print(hashlib.sha256(s.encode()).hexdigest())
