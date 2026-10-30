#!/usr/bin/env python3
"""Create/verify a private code-only experimental official-service package."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=frozenset({
 'scripts/run-official-runtime.py','scripts/official-init-receipts.py','scripts/official-admin.py','scripts/official-mark-spam.py','scripts/official-set-account-ban.py','scripts/provision-official-chat.py','scripts/provision-official-chess.py','scripts/featured-chess-runner.py','requirements.lock',
 *('steward/'+name+'.py' for name in ('__init__','leases','protocol','official_access','official_authors','official_certificates','official_chat_replay','official_chat_authority','official_chat_writer','official_chat_custody','official_chat_moderator','official_chat_access','official_chess_replay','official_chess_publisher','official_chess_custody','official_content','official_errors','official_ingest_http','official_local_transport','official_read_http','official_receipts','official_registry','official_runtime','official_sparse_cache','official_submission','official_submission_http','official_upload_policy','official_witness','official_state_paths','system_custody','system_publisher')),
 *('gateway_service/'+name+'.py' for name in ('__init__','auth','policy','user_store','http','transfers')),
 'room_service/__init__.py','room_service/contract.py','origin_service/__init__.py','origin_service/official_authority.py',
 *('codiserver-server-v0.3.0/codiauth/'+name+'.py' for name in ('__init__','jose','service')),
})
def record(path):
    raw=path.read_bytes();return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def verify(target):
    target=Path(target)
    if target.is_symlink() or not target.is_dir():raise ValueError('Real package directory required')
    manifest=target/'official-service.json'
    if manifest.is_symlink() or not manifest.is_file():raise ValueError('Package manifest missing')
    data=json.loads(manifest.read_text())
    if set(data)!={'version','files'} or data['version']!='codi-official-service/1' or set(data['files'])!=FILES:raise ValueError('Invalid package manifest')
    found=set()
    for path in target.rglob('*'):
        if path.is_symlink():raise ValueError('Package symlink refused')
        if path.is_dir():continue
        if not path.is_file() or path.stat().st_nlink!=1:raise ValueError('Nonregular package file')
        name=str(path.relative_to(target))
        if name=='official-service.json':continue
        if name not in FILES or record(path)!=data['files'][name]:raise ValueError('Unexpected or changed package file')
        found.add(name)
    if found!=FILES:raise ValueError('Package file missing')
    return {'status':'verified','files':len(found),'manifestSHA256':record(manifest)['sha256']}
def export(target):
    target=Path(target).absolute();base=ROOT/'.build/official-services'
    if target.exists() or target.is_symlink() or not target.is_relative_to(base) or any(p.is_symlink() for p in [target,*target.parents]):raise ValueError('Choose a new private official-services build path')
    target.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.official-export-',dir=target.parent))
    try:
        records={}
        for name in sorted(FILES):
            source=ROOT/name
            if not source.is_file() or source.is_symlink() or any(p.is_symlink() for p in source.parents if p.is_relative_to(ROOT)):raise ValueError('Regular declared source required')
            dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o644);records[name]=record(dest)
        (stage/'official-service.json').write_text(json.dumps({'version':'codi-official-service/1','files':records},indent=2,sort_keys=True)+'\n')
        verify(stage);stage.rename(target);return verify(target)
    finally:
        if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--output',type=Path);action.add_argument('--verify',type=Path);args=parser.parse_args()
    print(json.dumps(export(args.output) if args.output else verify(args.verify),indent=2))
