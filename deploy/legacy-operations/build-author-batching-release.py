#!/usr/bin/env python3
"""Compose the reviewed Chat and Chess bundles over the live pinned release."""
import importlib.util,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/official-chat-wake-profile27-r1';PIN='5925e903f2b6c457068b3e301ea4e8a8e04740aac68ae05eb12780c50f539f18';OUT=ROOT/'.build/releases/author-batching-profile27-r1'
spec=importlib.util.spec_from_file_location('app_builder',ROOT/'scripts/build-native-app-update.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
with tempfile.TemporaryDirectory(prefix='codi-offered-apps-') as temp:
 target=Path(temp);items=[]
 for name,folder in [('chat',ROOT/'.build/chat-offered-build-r7'),('chess',ROOT/'.build/chess-app-build-r9')]:
  catalog=json.loads((folder/'apps.json').read_text());assert len(catalog['apps'])==1 and catalog['apps'][0]['id']==name;item=catalog['apps'][0];relative=Path(item['path']).parent.relative_to('assets/desktop');shutil.copytree(folder/relative,target/relative);items.append(item)
 (target/'apps.json').write_text(json.dumps({'version':'codi-public-apps/2','hostAPI':2,'apps':items}));result=builder.build(target,OUT,BASE,PIN,allow_new=('chess',));print(json.dumps({k:v for k,v in result.items() if k!='obsoleteGeneratedFilesRemoved'},indent=2))
