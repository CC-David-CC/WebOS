#!/usr/bin/env python3
"""Compose the reviewed Chat and Chess bundles over the live pinned release."""
import importlib.util,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/chess-rotation-profile27-r1';PIN='85d679fc3aed1db710a88a56e5f09a69ed333107401365484ab5a5941398d665';OUT=ROOT/'.build/releases/author-names-profile27-r1'
spec=importlib.util.spec_from_file_location('app_builder',ROOT/'scripts/build-native-app-update.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
with tempfile.TemporaryDirectory(prefix='codi-offered-apps-') as temp:
 target=Path(temp);items=[]
 for name,folder in [('chat',ROOT/'.build/chat-offered-build-r6'),('chess',ROOT/'.build/chess-app-build-r8')]:
  catalog=json.loads((folder/'apps.json').read_text());assert len(catalog['apps'])==1 and catalog['apps'][0]['id']==name;item=catalog['apps'][0];relative=Path(item['path']).parent.relative_to('assets/desktop');shutil.copytree(folder/relative,target/relative);items.append(item)
 (target/'apps.json').write_text(json.dumps({'version':'codi-public-apps/2','hostAPI':2,'apps':items}));result=builder.build(target,OUT,BASE,PIN,allow_new=('chess',));print(json.dumps({k:v for k,v in result.items() if k!='obsoleteGeneratedFilesRemoved'},indent=2))
