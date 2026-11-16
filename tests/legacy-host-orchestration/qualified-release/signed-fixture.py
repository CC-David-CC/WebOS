#!/usr/bin/env python3
"""Run the existing disposable signed fixture against a reviewed candidate tree."""
import os,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[2]
script=root/'tests/files-desktop-signed-fixture.py'
source=script.read_text()
old="public=staging.stage(root/'public',bundled=BUNDLE)"
new="public=shutil.copytree(pathlib.Path(os.environ['CODI_MAIN_CANDIDATE']),root/'public',copy_function=os.link)"
if source.count(old)!=1:raise ValueError('Unexpected signed fixture')
# Fixture stages a public-only linked snapshot; it writes its SDK into a new
# gateway_service directory. It does not mutate an existing candidate file.
source=source.replace(old,new)
opfs="config['fileStorage']={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2};"
if source.count(opfs)!=1:raise ValueError('Unexpected fixture configuration')
source=source.replace(opfs,'')
namespace={'__name__':'__main__','__file__':str(script)}
exec(compile(source,str(script),'exec'),namespace)
