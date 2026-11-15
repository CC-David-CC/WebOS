#!/usr/bin/env python3
"""Read-only public pin and site checks for the staged G-code release."""
import concurrent.futures,hashlib,json,sys,urllib.error,urllib.request
BASE='https://ksu.codes/'
RELEASE='2aa7c157438b8bb28333b70b4ffd5783d4f3467a10120c642dbfd30368fc76dd'
EXPECTED={
 'assets/desktop/cache-manifest.json':'b8cea99c75a4f200a5c270f68be3448fc2ee46653892119bbabe4573ff8ec09d',
 'assets/desktop/apps.json':'ed7603fc279d89bfd04ac3eb0878bc6e2937844db27a6db0d64ebd48b6a29ca3',
 'assets/desktop/apps/gcode-preview/a9c2b24a4bcc91a833b6debf69ae0a8ace8f9eaed5041de4984a5899e8a83ffb/index.mjs':'3327904767b618c58db7c44dace55a08088f96b7ec01d7bde6b23cb2f828a90c',
 'app.js':'beab137f4a7c7246be0c7620f2f3400df4f3056aeefa20e75a5e79ab02a4552b',
 'desktop-apps.js':'a23f99dc96dfe9cca9212eebfef666f38460b5fbc46671a447f89d4c09189ae2',
}
SITES={'python.coach':200,'code.contractors':200,'ksu.codes':200,'arpa.net.ai':200,'plastic.download':200,'official.bid':200,'does.trade':200,'codi.codes':200,'cardboard.ksu.codes':200,'hardware.ksu.codes':401}
def fetch(url):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=20) as response:return response.status,response.read(16*1024*1024+1)
 except urllib.error.HTTPError as e:return e.code,e.read(1024)
def check_site(item):
 name,expected=item
 try:status,_=fetch('https://'+name+'/');return name,status,expected,status==expected
 except Exception as error:return name,str(error),expected,False
fail=False
for name,expected in EXPECTED.items():
 try:
  status,data=fetch(BASE+name);actual=hashlib.sha256(data).hexdigest();ok=status==200 and len(data)<=16*1024*1024 and actual==expected
  if name.endswith('cache-manifest.json') and ok:ok=json.loads(data).get('id')==RELEASE
  print(('PASS ' if ok else 'FAIL ')+name+' HTTP '+str(status)+' SHA-256 '+actual);fail|=not ok
 except Exception as error:print('FAIL',name,str(error));fail=True
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
 for name,status,expected,ok in pool.map(check_site,SITES.items()):print(('PASS ' if ok else 'FAIL ')+name+' HTTP '+str(status)+' expected '+str(expected));fail|=not ok
sys.exit(1 if fail else 0)
