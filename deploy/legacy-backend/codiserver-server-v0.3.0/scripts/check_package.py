#!/usr/bin/env python3
"""Integrity/registry check only; not a browser, network, crypto or scale witness."""
import argparse
import hashlib
import json
from pathlib import Path

IGNORED={'.git','.venv','var','__pycache__','.test-output'}

def require(condition,message):
    if not condition:
        raise ValueError(message)

def inventory(root):
    return {p.relative_to(root).as_posix():p for p in root.rglob('*')
            if p.is_file() and not any(x in IGNORED for x in p.relative_to(root).parts)
            and p.name!='CHECKSUMS.sha256'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--peer',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    registry=json.loads((root/'contracts/acceptance.json').read_text())
    cases={c['id']:c for c in registry['cases']}
    require(len(cases)==len(registry['cases']),'duplicate case ID')
    gates={g['id']:g for g in registry['gates']}
    require(len(gates)==len(registry['gates']),'duplicate gate ID')
    seen=set()
    def visit(g,chain=()):
        require(g in gates,'unknown gate '+g)
        require(g not in chain,'gate cycle')
        if g in seen:return
        for d in gates[g]['requires']:visit(d,chain+(g,))
        seen.add(g)
    for g in gates:visit(g)
    assigned=[]
    for gid,g in gates.items():
        for cid in g['cases']:
            require(cid in cases and cases[cid]['gate']==gid,'misassigned case '+cid)
            assigned.append(cid)
    require(len(assigned)==len(set(assigned)) and set(assigned)==set(cases),'missing/duplicate gate case')
    ticket_list=json.loads((root/'contracts/tickets.json').read_text())
    tickets={t['id']:t for t in ticket_list}
    require(len(tickets)==len(ticket_list),'duplicate ticket ID')
    covered=set()
    def ticket_visit(t,chain=()):
        require(t in tickets,'unknown ticket '+t)
        require(t not in chain,'ticket cycle')
        for d in tickets[t]['requires']:ticket_visit(d,chain+(t,))
    for tid,t in tickets.items():
        ticket_visit(tid)
        require(t['gate'] in gates,'unknown ticket gate')
        require(all(g in gates for g in t['gate_requires']),'unknown prerequisite gate')
        require(set(gates[t['gate']]['requires']).issubset(t['gate_requires']),'missing prerequisite gate')
        for cid in t['acceptance']:
            require(cid in cases and cases[cid]['gate']==t['gate'],'bad ticket acceptance '+cid)
            covered.add(cid)
    require(covered==set(cases),'uncovered acceptance case')
    content=inventory(root)
    expected={}
    for line in (root/'CHECKSUMS.sha256').read_text().splitlines():
        digest,name=line.split('  ',1)
        require(name not in expected and '..' not in Path(name).parts and not Path(name).is_absolute(),'bad checksum name')
        expected[name]=digest
    require(set(expected)==set(content),'inventory differs from checksum list')
    for name,p in content.items():
        require(hashlib.sha256(p.read_bytes()).hexdigest()==expected[name],'hash mismatch '+name)
        require(p.suffix.lower() not in {'.ttf','.otf','.woff','.woff2','.pem','.pyc'},'forbidden artifact '+name)
    if args.peer:
        own=inventory(root/'shared');other=inventory(args.peer/'shared')
        require(set(own)==set(other),'shared names differ')
        for name,p in own.items():require(p.read_bytes()==other[name].read_bytes(),'shared bytes differ '+name)
    print(json.dumps({'check':'package integrity/registry only','status':'passed','files':len(content)+1,
                      'obligations':len(cases),'gates':len(gates),'tickets':len(tickets)},indent=2))

if __name__=='__main__':main()
