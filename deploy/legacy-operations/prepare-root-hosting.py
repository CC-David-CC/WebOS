#!/usr/bin/env python3
"""Generate a KSU-only root/blog hosting candidate; never apply live config."""
import hashlib,importlib.util,json,shutil,sys
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
INPUT=ROOT/'.build/hosting/root-mount-r1-inputs'
OUTPUT=ROOT/'.build/hosting/root-mount-r1-candidate'


def module(name,path):
    sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def sha(raw):return hashlib.sha256(raw).hexdigest()


def build():
    before=module('root_hosting_before',INPUT/'common.py');after=module('root_hosting_after',ROOT/'hosting_root/common.py')
    manifest=before.load(INPUT/'sites.toml');old=before.caddy(manifest,'production')
    assert old==(INPUT/'Caddyfile').read_text()
    assert sha(old.encode())=='694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad'
    assert after.caddy(manifest,'production')==old,'Absent selector must preserve all current Caddy bytes'
    value=deepcopy(manifest);site=next(s for s in value['sites'] if s['domain']=='ksu.codes');site['codi_mount']=''
    after.validate(value)
    assert not OUTPUT.exists();OUTPUT.mkdir()
    for n in ['common.py','hardware_hosting.py','cardboard_hosting.py']:shutil.copyfile(ROOT/'hosting_root'/n,OUTPUT/n)
    (OUTPUT/'sites.toml').write_text(after.dump(value))
    assert after.load(OUTPUT/'sites.toml')==value
    for mode in ['prepare','production']:(OUTPUT/('Caddyfile.'+mode)).write_text(after.caddy(value,mode))
    # Every non-KSU route block remains exactly the same; the shared ingress and
    # certificate blocks are not changed by the root selector.
    def blocks(text):
        result={};name=None;lines=[]
        for line in text.splitlines():
            if line and not line[0].isspace() and line.endswith(' {'):
                name=line;lines=[line]
            elif name is not None:
                lines.append(line)
                if line=='}':result[name]='\n'.join(lines);name=None
        return result
    a,b=blocks(old),blocks((OUTPUT/'Caddyfile.production').read_text());assert set(a)==set(b)
    assert {n:v for n,v in a.items() if n!='ksu.codes {'}=={n:v for n,v in b.items() if n!='ksu.codes {'}
    records={p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(OUTPUT.iterdir())}
    result={'status':'PASS','files':records,'directory':str(OUTPUT),'baselineGeneratorSHA256':sha((INPUT/'common.py').read_bytes()),'baselineManifestSHA256':sha((INPUT/'sites.toml').read_bytes()),'baselineCaddySHA256':sha(old.encode()),'currentHiddenRenderingByteIdentical':True,'nonKSUSiteBlocksByteIdentical':True,'productionChanged':False}
    (OUTPUT/'hosting-candidate.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    result=build();(ROOT/'.build/checks/root-hosting-build-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
