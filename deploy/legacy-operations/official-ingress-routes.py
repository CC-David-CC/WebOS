#!/usr/bin/env python3
"""Render exact Caddy routes for an official-channel loopback backend.

This emits a candidate fragment only; install through the hosting controller.
"""
import argparse,re

def routes(prefix,port):
 if prefix and not re.fullmatch(r'/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+',prefix):raise ValueError('Invalid mount prefix')
 if type(port) is not int or not 1024<=port<=65535:raise ValueError('Invalid backend port')
 paths=('official-head','official-history','official-directory','official-channel','official-ingest/challenge','official-ingest/use')
 lines=[]
 for path in paths:
  lines.append('handle '+prefix+'/'+path+' {')
  if prefix:lines.append('  uri strip_prefix '+prefix)
  lines.extend(('  reverse_proxy 127.0.0.1:'+str(port),' }'))
 return '\n'.join(lines)+'\n'

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prefix',default='');p.add_argument('--port',type=int,required=True);a=p.parse_args();print(routes(a.prefix,a.port),end='')
