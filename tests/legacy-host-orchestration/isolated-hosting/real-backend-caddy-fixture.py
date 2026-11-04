#!/usr/bin/env python3
"""Local generated beta TLS vhost for disposable, separately running backends."""
import importlib.util,os,shutil,signal,subprocess,sys,tempfile,time,tomllib
from pathlib import Path
root=Path(__file__).resolve().parents[1];source=root.parents[1]/'active-system/network';sys.path.insert(0,str(root/'ops'))
spec=importlib.util.spec_from_file_location('beta_hosting',root/'ops/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='beta-real-caddy-') as name:
 d=Path(name);cert=d/'cert.pem';key=d/'key.pem';static=d/'static';(static/'network').mkdir(parents=True);(static/'index.html').write_text('<!doctype html><title>Disposable beta fixture</title>')
 for n in ('identity.mjs','crypto.mjs','strict-json.mjs'):shutil.copy2(source/n,static/'network'/n)
 subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=beta.ksu.codes','-addext','subjectAltName=DNS:beta.ksu.codes'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
 values=tomllib.loads((root/'sites.toml').read_text());values['codi_beta_simplified']='a'*64;rendered=m.caddy(values,'production');start=rendered.index('beta.ksu.codes {');end=rendered.index('\n}\n',start)+3;block=rendered[start:end]
 block=block.replace('beta.ksu.codes {','https://beta.ksu.codes:18444 {\n\tbind 127.0.0.1\n\ttls '+str(cert)+' '+str(key),1).replace('\timport site_defaults\n','').replace('/srv/codi-connected/simplified/'+'a'*64,str(static))
 cfg=d/'Caddyfile';cfg.write_text('{\n admin off\n auto_https disable_redirects\n}\n'+block+'\n')
 proc=subprocess.Popen(['/tmp/codi-microduck-hosting-evidence/caddy','run','--config',str(cfg),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  import socket
  for _ in range(100):
   if proc.poll() is not None:raise RuntimeError('Caddy exited')
   try:
    with socket.create_connection(('127.0.0.1',18444),timeout=.1):break
   except OSError:time.sleep(.02)
  else:raise RuntimeError('Caddy did not listen')
  print('beta fixture ready at 127.0.0.1:18444',flush=True)
  signal.pause()
 finally:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
