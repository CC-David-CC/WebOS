"""Staging adds only explicitly listed, verified app bundles to a pinned release."""
import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'active-system/scripts/stage-simplified-app-batch.py'
def digest(data):return hashlib.sha256(data).hexdigest()
class StageNewApps(unittest.TestCase):
 def test_explicit_new_app_and_pinned_desktop(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);name='a'*64;base=root/name;assets=base/'assets/desktop';assets.mkdir(parents=True);(base/'app.js').write_bytes(b'old-app');(base/'desktop-apps.js').write_bytes(b'old-routes');(assets/'offline-worker.js').write_text('/* worker */\nconst RELEASE='+json.dumps({'id':name})+';\n');(assets/'cache-manifest.json').write_text(json.dumps({'id':name}));(assets/'apps.json').write_text(json.dumps({'version':'test','apps':[{'id':'old','bundleSHA256':'b'*64}]}));(assets/'apps/old'/('b'*64)).mkdir(parents=True);(assets/'apps/old'/('b'*64)/'old').write_bytes(b'old')
   batch=root/'batch';payload=b'new app';bundle='c'*64;app=batch/'apps/new'/bundle;app.mkdir(parents=True);(app/'index.mjs').write_bytes(payload);record={'id':'new','bundleSHA256':bundle,'files':{'index.mjs':{'bytes':len(payload),'sha256':digest(payload)}}};(batch/'apps.json').write_text(json.dumps({'apps':[record]}));routes=root/'routes.js';routes.write_bytes(b'new-routes');out=root/'out'
   cmd=[sys.executable,str(SCRIPT),'--baseline',str(base),'--batch',str(batch),'--output',str(out),'--apps','new','--desktop-apps',str(routes),'--desktop-apps-base-sha256',digest(b'old-routes')]
   self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0);self.assertFalse(out.exists())
   bad=subprocess.run(cmd+['--new-apps','new','old'],capture_output=True);self.assertNotEqual(bad.returncode,0);self.assertFalse(out.exists())
   stale=cmd.copy();stale[-1]='0'*64;self.assertNotEqual(subprocess.run(stale+['--new-apps','new'],capture_output=True).returncode,0);self.assertFalse(out.exists())
   result=subprocess.run(cmd+['--new-apps','new'],capture_output=True,text=True,check=True);release=json.loads(result.stdout)['release'];catalog=json.loads((out/'assets/desktop/apps.json').read_text());self.assertEqual([x['id'] for x in catalog['apps']],['old','new']);self.assertEqual((out/'desktop-apps.js').read_bytes(),b'new-routes');self.assertEqual((out/'assets/desktop/apps/new'/bundle/'index.mjs').read_bytes(),payload);self.assertEqual(json.loads((out/'assets/desktop/cache-manifest.json').read_text())['id'],release)
   self.assertEqual((base/'desktop-apps.js').read_bytes(),b'old-routes')
if __name__=='__main__':unittest.main()
