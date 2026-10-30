#!/usr/bin/env python3
"""Run the public catch-up profile on i36 over its Ethernet Internet path."""
import pathlib,re,secrets,shlex,subprocess,time,urllib.request,json
R=pathlib.Path(__file__).resolve().parents[1];remote='maint@10.0.7.105';port=19538;pidfile='/tmp/codi-profile-'+secrets.token_hex(8)+'.pid';proc=tunnel=None
try:
 ip=subprocess.check_output(['ssh','-o','BatchMode=yes',remote,'curl','-4','-fsS','--max-time','10','https://api.ipify.org'],text=True,timeout=20).strip();assert ip=='104.180.210.36',ip;print('i36 outbound IP:',ip,flush=True)
 cmd='umask 077; echo $$ > '+pidfile+'; exec /usr/bin/chromedriver --port='+str(port)+' --allowed-ips=127.0.0.1';proc=subprocess.Popen(['ssh','-o','BatchMode=yes',remote,cmd],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(port)+':127.0.0.1:'+str(port),remote],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 until=time.monotonic()+25
 while True:
  if proc.poll() is not None or tunnel.poll() is not None:raise RuntimeError('i36 driver stopped')
  try:
   if json.load(urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status',timeout=1))['value']['ready']:break
  except OSError:pass
  if time.monotonic()>=until:raise TimeoutError('i36 driver not ready')
  time.sleep(.2)
 source=(R/'scripts/live-chat-catchup-profile.py').read_text().replace("spec.loader.exec_module(d)\n", "spec.loader.exec_module(d);d.DRIVER='http://127.0.0.1:19538'\n").replace('/snap/chromium/current/usr/lib/chromium-browser/chrome','/usr/bin/chromium')
 exec(compile(source,str(R/'scripts/live-chat-catchup-profile.py'),'exec'),{'__file__':str(R/'scripts/live-chat-catchup-profile.py'),'__name__':'__main__'})
finally:
 for child in (tunnel,proc):
  if child:
   child.terminate()
   try:child.wait(5)
   except subprocess.TimeoutExpired:child.kill();child.wait()
 cleanup='''import os,pathlib,re,signal,sys\np=pathlib.Path(sys.argv[1]);assert re.fullmatch(r"/tmp/codi-profile-[0-9a-f]{16}[.]pid",str(p))\nif p.exists():\n pid=int(p.read_text());cmd=pathlib.Path('/proc')/str(pid)/'cmdline'\n if cmd.exists() and b'chromedriver' in cmd.read_bytes():os.kill(pid,signal.SIGTERM)\n p.unlink()\nprint('i36 driver cleaned')'''
 try:print(subprocess.run(['ssh','-o','BatchMode=yes',remote,'python3','-c',shlex.quote(cleanup),pidfile],check=True,capture_output=True,text=True,timeout=15).stdout.strip(),flush=True)
 except Exception as e:print('i36 driver cleanup failed:',e,flush=True)
