#!/usr/bin/env python3
"""Launch one isolated loopback systemd socket proxy, with real socket activation."""
import os,socket,sys
if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit('Expected loopback target port')
port=int(sys.argv[1]);assert 1<=port<=65535
backlog=int(os.environ.get('CODI_PROXY_BACKLOG','128'))
if backlog not in (16,128):raise SystemExit('Test backlog must be 16 or 128')
sock=socket.socket();sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);sock.bind(('127.0.0.1',19865));sock.listen(backlog)
if sock.fileno()!=3:os.dup2(sock.fileno(),3)
os.set_inheritable(3,True)
os.environ['LISTEN_PID']=str(os.getpid());os.environ['LISTEN_FDS']='1';os.environ.pop('LISTEN_FDNAMES',None)
os.execv('/usr/lib/systemd/systemd-socket-proxyd',['systemd-socket-proxyd','--connections-max=16','127.0.0.1:'+str(port)])
