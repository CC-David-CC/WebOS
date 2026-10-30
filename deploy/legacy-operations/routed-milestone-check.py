#!/usr/bin/env python3
"""Bind measured public routing candidate scope; never promote the full goal."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
CHECKS=ROOT/'.build/checks';records={}
def read(name):
    raw=(CHECKS/name).read_bytes();records[name]=hashlib.sha256(raw).hexdigest();value=json.loads(raw);assert value['status']=='PASS',name
    for file,pin in value['sha256'].items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==pin,file
    return value
repair=read('routed-history-browser-result.json');accounting=read('routed-history-unit-result.json')
assert repair['contexts']==3 and repair['physicalLinks']==2 and len(repair['checks'])>=23 and all(repair['allBudgetsReleased'])
assert not repair['HTTPChatUsed'] and not repair['liveSiteChanged'] and not repair['independentWANTested']
assert len(accounting['checks'])==13
three=read('routed-group-browser-result.json');four=read('routed-four-room-browser-result.json');scope=read('routed-scope-browser-result.json');regression=read('routed-regression-result.json')
assert three['contexts']==3 and len(three['checks'])>=36 and all(three['allBudgetsReleased'])
assert four['contexts']==8 and four['simultaneousRoutedRooms']==4 and four['physicalLinks']==7 and four['allFourActiveBeforeMeasuredSends']
assert four['unintendedRoomDeliveries']==0 and four['unaffectedGroupsSurviveMemberLoss'] and all(four['allBudgetsReleased'])
assert not four['guestInternetConfigured'] and not four['guestRelayLimitsChanged']
# Recount actual recorded histories rather than relying on the reported denominator.
remote=0
for witness in four['witnesses']:
    i=witness['context']
    for group in witness['groups']:
        history=group['snapshot']['history'];assert len(history)==3
        origins=set()
        for message in history:
            parts=message['text'].split('_');assert parts[:3]==['ROUTED','MARKER','FOUR'] and int(parts[3])==group['room']
            author=int(parts[4]);assert author in group['members'] and author not in origins;origins.add(author)
            assert message['author']==group['snapshot']['members'][group['members'].index(author)]['name']
            remote+=int(author!=i)
        assert origins==set(group['members'])
assert remote==24==four['observedRemoteChatDeliveries']
for name in ['validOriginCannotBeTransplantedBetweenTwoAdmittedGroups','rejectedScopeDidNotAdvanceOriginalReplayFloor','correctDestinationDeliversExactlyOnce','legacyUnnegotiatedRoutingRejectedBeforeDelivery','existingTwoPeerChatAndSeparateLegalChessOnSamePool','matchingLegacyPgnExcludesChat','existingDesktopPoolPreserved']:assert scope[name],name
assert regression['protocol']['cases']==153 and all(c['status']=='PASS' for c in regression['protocol']['results'])
assert regression['guestCapacity']['actualAdmittedWires']==4 and regression['guestCapacity']['fifthHTTPStatus']==503 and not regression['guestCapacity']['productionLimitsChanged']
report={'status':'PASS','scope':__doc__,'contexts':8,'simultaneousRoutedPublicRooms':4,'physicalLinks':7,'recountedRemoteDeliveries':remote,'unintendedRoomDeliveries':0,'actualScopeAndLegacyNegatives':True,'protocolRegressionCases':153,'guestRelayCapacityVerified':4,'eightGuestInternetSessionsClaimed':False,'publicRollout':False,'privateGroupsEnabled':False,'fullGoalComplete':False,'routedProfile':'codi-routed-room/2','boundedHistoryRepair':{'checks':len(repair['checks']),'cacheLeaseChecks':len(accounting['checks']),'historicalOnly':True,'fullM03GateClaimed':False},'remaining':['arbitrary routed topologies, dependency-gate audit and production/security review','reviewed private-group key profile','versioned export, installed-service/browser/cache and public rollout gates','independent WAN/NAT and full supplied acceptance audit'],'receiptSHA256':records}
report['sha256']={'scripts/routed-milestone-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(CHECKS/'routed-milestone-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
