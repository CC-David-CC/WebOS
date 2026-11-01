#!/usr/bin/env python3
"""Cryptographic admission model only; not a server or release qualification."""
import secrets,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system/codiserver-server-v0.3.0'))
from codiauth import jose
from cryptography.hazmat.primitives.asymmetric import ec

TICKET='codi-admission-model+jwt';PROOF='codi-admission-proof-model+jws'
ORIGIN='https://example.invalid';AUD=ORIGIN+'/gateway';ROUTE='/gateway/challenge-v2'
clock=[1000];authority=ec.generate_private_key(ec.SECP256R1());authority_jwk=jose.public_jwk(authority)

def token():return secrets.token_urlsafe(32)
def issue(session,key):
 # A stand-in for the existing issuer's full session, generation and proof checks.
 subject,sid,expected=session;assert jose.thumbprint(jose.public_jwk(key))==jose.thumbprint(expected)
 return jose.sign({'v':1,'iss':ORIGIN,'aud':AUD,'sub':subject,'sid':sid,'cnf':expected,'iat':clock[0],'exp':clock[0]+30,'jti':token()},authority,TICKET)
def proof(ticket,key,request):
 return jose.sign({'v':1,'ticket_sha':jose.digest(ticket),'request_sha':jose.digest(request),'path':ROUTE,'iat':clock[0],'exp':clock[0]+20,'jti':token()},key,PROOF)
class RateDenied(Exception):pass
class Invalid(Exception):pass
class Gate:
 def __init__(self,verified=100,per_account=4,bad=2,legacy=1,max_accounts=40,max_proofs=100):
  self.limits=verified,per_account,bad,legacy,max_accounts,max_proofs;self.window=None;self.counts={};self.seen={};self.used=self.bad=self.legacy=0
 def reset(self):
  window=clock[0]//60
  if window!=self.window:self.window=window;self.counts.clear();self.used=self.bad=self.legacy=0
  self.seen={jti:expiry for jti,expiry in self.seen.items() if expiry>clock[0]}
 def reject(self):
  self.reset();self.bad+=1
  if self.bad>self.limits[2]:raise RateDenied('unverified budget')
  raise Invalid('invalid ticket or proof')
 def old_client(self):
  self.reset();self.legacy+=1
  if self.legacy>self.limits[3]:raise RateDenied('legacy budget')
 def accept(self,ticket,signature,request):
  self.reset()
  try:
   claims=jose.verify(ticket,authority_jwk,TICKET,8192)
   assert set(claims)=={'v','iss','aud','sub','sid','cnf','iat','exp','jti'} and claims['v']==1 and claims['iss']==ORIGIN and claims['aud']==AUD
   assert type(claims['iat']) is int and type(claims['exp']) is int and claims['iat']<=clock[0]<claims['exp']<=claims['iat']+30
   assert isinstance(claims['sub'],str) and claims['sub'] and isinstance(claims['sid'],str) and claims['sid'] and len(jose.unb64(claims['jti']))==32
   signed=jose.verify(signature,claims['cnf'],PROOF,8192)
   assert set(signed)=={'v','ticket_sha','request_sha','path','iat','exp','jti'} and signed['v']==1 and signed['ticket_sha']==jose.digest(ticket) and signed['request_sha']==jose.digest(request) and signed['path']==ROUTE
   assert type(signed['iat']) is int and type(signed['exp']) is int and signed['iat']<=clock[0]<signed['exp']<=signed['iat']+20
   assert isinstance(signed['jti'],str) and len(jose.unb64(signed['jti']))==32 and signed['jti'] not in self.seen
  except (ValueError,TypeError,KeyError,AssertionError):self.reject()
  if signed['jti'] in self.seen:self.reject()
  if len(self.seen)>=self.limits[5] or self.used>=self.limits[0]:raise RateDenied('verified global capacity')
  subject=claims['sub'];count=self.counts.get(subject)
  if count is None and len(self.counts)>=self.limits[4]:raise RateDenied('account table capacity')
  if (count or 0)>=self.limits[1]:raise RateDenied('account capacity')
  self.seen[signed['jti']]=signed['exp'];self.used+=1;self.counts[subject]=(count or 0)+1
  return subject

def expect(exc,fn):
 try:fn()
 except exc:return
 raise AssertionError('Expected '+exc.__name__)

a=ec.generate_private_key(ec.SECP256R1());a2=ec.generate_private_key(ec.SECP256R1());b=ec.generate_private_key(ec.SECP256R1());evil=ec.generate_private_key(ec.SECP256R1());request='{"path":"sample"}'
ta=issue(('alice','session-a',jose.public_jwk(a)),a);ta2=issue(('alice','session-a2',jose.public_jwk(a2)),a2);tb=issue(('bob','session-b',jose.public_jwk(b)),b)
g=Gate(per_account=2);g.old_client();expect(RateDenied,g.old_client)
assert g.accept(ta,proof(ta,a,request),request)=='alice';assert g.accept(ta2,proof(ta2,a2,request),request)=='alice';expect(RateDenied,lambda:g.accept(ta,proof(ta,a,request),request));assert g.accept(tb,proof(tb,b,request),request)=='bob'
# The transport is intentionally not consulted; forged headers cannot choose an account.
forged=proof(tb,evil,request);expect(Invalid,lambda:g.accept(tb,forged,request));assert g.counts['bob']==1
sig=proof(tb,b,request);assert g.accept(tb,sig,request)=='bob';expect(Invalid,lambda:g.accept(tb,sig,request))
# A still-valid proof cannot be replayed across a fixed-minute boundary.
clock[0]=1019;boundary=Gate();boundarySig=proof(tb,b,request);boundary.accept(tb,boundarySig,request);clock[0]=1020;expect(Invalid,lambda:boundary.accept(tb,boundarySig,request))
# Exhausting the unverified and legacy shares does not debit the verified share.
g=Gate(per_account=4);g.old_client();expect(RateDenied,g.old_client)
for _ in range(3):
 try:g.accept(tb,proof(tb,evil,request),request)
 except (Invalid,RateDenied):pass
assert g.accept(tb,proof(tb,b,request),request)=='bob'
expect(Invalid,lambda:Gate().accept(tb,proof(tb,b,'other'),request))
# Bounded table refuses a new subject without evicting an existing one.
g=Gate(max_accounts=1);g.accept(ta,proof(ta,a,request),request);expect(RateDenied,lambda:g.accept(tb,proof(tb,b,request),request));assert set(g.counts)=={'alice'}
clock[0]=1040;expect(Invalid,lambda:Gate().accept(tb,proof(tb,b,request),request))
# Thirty independently verified subjects can share one transport budget.
clock[0]=1080;classroom=Gate(verified=100,per_account=4,max_accounts=40,max_proofs=100)
for i in range(30):
 key=ec.generate_private_key(ec.SECP256R1());ticket=issue(('student-'+str(i),'sid-'+str(i),jose.public_jwk(key)),key)
 for _ in range(2):assert classroom.accept(ticket,proof(ticket,key,request),request)=='student-'+str(i)
assert classroom.used==60 and len(classroom.counts)==30
# An attacker cannot forge an issuer's account ticket.
forged_ticket=jose.sign({'v':1,'iss':ORIGIN,'aud':AUD,'sub':'alice','sid':'x','cnf':jose.public_jwk(evil),'iat':clock[0],'exp':clock[0]+30,'jti':token()},evil,TICKET)
expect(Invalid,lambda:Gate().accept(forged_ticket,proof(forged_ticket,evil,request),request))
def negotiate(status,value):
 if status==404:return 'legacy'
 if status==200 and value=={'version':'codi-gateway-admission/2'}:return 'enhanced'
 raise Invalid('Capability unknown; do not downgrade')
assert negotiate(404,None)=='legacy' and negotiate(200,{'version':'codi-gateway-admission/2'})=='enhanced'
for status,value in [(429,None),(500,None),(200,{}),(0,None)]:expect(Invalid,lambda:negotiate(status,value))
print('PASS model ES256 key/request binding, shared-NAT accounts, replay, expiry, bounded state and isolated legacy/unverified shares')
