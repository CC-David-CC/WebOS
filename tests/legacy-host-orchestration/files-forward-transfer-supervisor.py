#!/usr/bin/env python3
"""Bound one owned external test: five minutes per observed phase, 15 total."""
import os, pathlib, signal, sys, time
if len(sys.argv)!=5:raise SystemExit('usage: node-pid browser-pid phase-log supervisor-log')
pid,browser=int(sys.argv[1]),int(sys.argv[2]);log=pathlib.Path(sys.argv[3]);out=pathlib.Path(sys.argv[4]);ticks=os.sysconf('SC_CLK_TCK')
stat=pathlib.Path(f'/proc/{pid}/stat').read_text();startticks=int(stat[stat.rfind(')')+2:].split()[19]);uptime=float(pathlib.Path('/proc/uptime').read_text().split()[0]);total_started=time.monotonic()-(uptime-startticks/ticks)
phase_count=-1;phase_started=time.monotonic();last='unobserved'
with out.open('w') as f:
 while pathlib.Path(f'/proc/{pid}').exists():
  phases=[x.strip() for x in log.read_text(errors='replace').splitlines() if 'PHASE ' in x] if log.exists() else []
  if len(phases)!=phase_count:
   now=time.monotonic();f.write(f'{time.time():.3f} prior={last!r} observed_seconds={now-phase_started:.3f} next={(phases[-1] if phases else "startup")!r}\n');f.flush();last=phases[-1] if phases else 'startup';phase_count=len(phases);phase_started=now
  if time.monotonic()-total_started>900 or time.monotonic()-phase_started>300:
   f.write('TIMEOUT: terminating owned test and browser; preserve profile and logs\n');f.flush()
   for p in (pid,browser):
    try:os.kill(p,signal.SIGTERM)
    except ProcessLookupError:pass
   break
  time.sleep(1)
 f.write('monitor ended\n');f.flush()
