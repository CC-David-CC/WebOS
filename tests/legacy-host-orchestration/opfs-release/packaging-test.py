#!/usr/bin/env python3
import hashlib,json,pathlib,shutil,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parents[2];here=root/'research/beta-opfs-release';baseline=pathlib.Path(sys.argv[1]);bundle=pathlib.Path(sys.argv[2]);pin='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
def build(base,files,out,ok=True):
 r=subprocess.run([sys.executable,str(here/'build.py'),'--baseline',str(base),'--files-bundle',str(files),'--out',str(out)],capture_output=True,text=True)
 assert (r.returncode==0)==ok,(r.stdout,r.stderr)
def verify(out,ok=True):
 r=subprocess.run([sys.executable,str(here/'verify.py'),str(out),pin],capture_output=True,text=True);assert (r.returncode==0)==ok,(r.stdout,r.stderr)
with tempfile.TemporaryDirectory(prefix='codi-beta-opfs-package-') as t:
 t=pathlib.Path(t);a=t/'a';b=t/'b';build(baseline,bundle,a);build(baseline,bundle,b);verify(a);verify(b);assert (a/'manifest.json').read_bytes()==(b/'manifest.json').read_bytes();old=json.loads((baseline/'apps.json').read_bytes());new=json.loads((a/'assets/desktop/apps.json').read_bytes());assert [x for x in old['apps'] if x['id']!='files']==[x for x in new['apps'] if x['id']!='files'];assert len(old['apps'])==len(new['apps']);
 target=next(a.glob('storage/browser/releases/*/mirror.mjs'));target.write_bytes(target.read_bytes()+b' ');verify(a,False);(b/'unexpected').write_text('x');verify(b,False)
 bad=t/'bad';shutil.copytree(baseline,bad);(bad/'app.js').write_bytes(b'not beta');build(bad,bundle,t/'bad-out',False)
 bad_bundle=t/'bad-bundle';shutil.copytree(bundle,bad_bundle);entry=json.loads((bad_bundle/'apps.json').read_bytes())['apps'][0];p=bad_bundle/'apps/files'/entry['bundleSHA256']/'index.mjs';p.write_bytes(p.read_bytes()+b' ');build(baseline,bad_bundle,t/'bad-bundle-out',False)
print('PASS reproducible 87-file package, other catalog entries preserved, tamper/extra/baseline/bundle drift rejected')
