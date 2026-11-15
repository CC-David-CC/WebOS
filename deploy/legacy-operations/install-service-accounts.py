#!/usr/bin/env python3
"""Provision three locked Debian/Ubuntu service accounts; never starts services.

An explicit guest GID lets the operator choose a narrow ping group policy.
This tool does not change sysctls, passwords of existing accounts or memberships.
Existing incompatible users/groups fail before any account is created.
"""
import argparse,grp,json,os,pwd,subprocess

ROLES=('issuer','steward','guest')
def validate(name,guest_gid):
 try:group=grp.getgrnam(name)
 except KeyError:group=None
 try:user=pwd.getpwnam(name)
 except KeyError:user=None
 users=pwd.getpwall()
 if group:
  if group.gr_gid==0 or group.gr_mem or (name=='codi-guest' and group.gr_gid!=guest_gid) or (name!='codi-guest' and group.gr_gid>=1000):raise ValueError('Existing incompatible group: '+name)
  if any(other.pw_gid==group.gr_gid and other.pw_name!=name for other in users):raise ValueError('Existing group has another primary member: '+name)
 if user:
  if not group or user.pw_gid!=group.gr_gid or not 0<user.pw_uid<1000 or user.pw_dir!='/nonexistent' or user.pw_shell!='/usr/sbin/nologin':raise ValueError('Existing incompatible user: '+name)
  if os.getgrouplist(name,user.pw_gid)!=[user.pw_gid]:raise ValueError('Existing supplementary memberships: '+name)
  if any(other.pw_uid==user.pw_uid and other.pw_name!=name for other in users):raise ValueError('Existing UID has another account name: '+name)
  shadow=subprocess.run(['getent','shadow',name],check=True,capture_output=True,text=True).stdout.split(':')
  if len(shadow)<2 or not shadow[1].startswith(('!','*')):raise ValueError('Existing service password is not locked: '+name)
 return user,group

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--guest-gid',type=int,required=True);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 if os.geteuid()!=0:parser.error('Run as root to validate locked account state')
 if not 1<=args.guest_gid<=2147483647:parser.error('A non-root Linux GID is required')
 try:
  try:occupied=grp.getgrgid(args.guest_gid)
  except KeyError:occupied=None
  if occupied and occupied.gr_name!='codi-guest':raise ValueError('Guest GID belongs to another group; select an unused GID')
  initial={role:validate('codi-'+role,args.guest_gid) for role in ROLES}
  if args.apply:
   for role,(user,group) in initial.items():
    name='codi-'+role
    if group is None:subprocess.run(['groupadd',*(['--gid',str(args.guest_gid)] if role=='guest' else ['--system']),name],check=True)
    if user is None:subprocess.run(['useradd','--system','--gid',name,'--home-dir','/nonexistent','--no-create-home','--shell','/usr/sbin/nologin',name],check=True)
  records={}
  for role in ROLES:
   name='codi-'+role;user,group=validate(name,args.guest_gid)
   records[role]={'name':name,'uid':user.pw_uid if user else None,'gid':group.gr_gid if group else args.guest_gid if role=='guest' else None,'locked':bool(user),'createdUser':args.apply and initial[role][0] is None,'createdGroup':args.apply and initial[role][1] is None}
  if args.apply:assert len({record['uid'] for record in records.values()})==len({record['gid'] for record in records.values()})==3
  print(json.dumps({'status':'applied' if args.apply else 'plan','accounts':records,'networkPolicyChanged':False,'servicesStarted':False},indent=2))
 except (ValueError,subprocess.SubprocessError) as error:parser.error(str(error))
if __name__=='__main__':main()
