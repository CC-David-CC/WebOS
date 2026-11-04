#!/usr/bin/env python3
"""Build the requested standalone planning report; no external dependencies."""
import csv
import html
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROWS = []


def add(key, name, group, done, partial, finish, prove, difficulty, working,
        partial_work, missing, dependencies="None beyond common host contract",
        evidence="docs/APP_STATUS.md"):
    ROWS.append(dict(id=key, silo=name, group=group, done_pct=done,
                     partial_pct=partial, remaining_pct=100-done-partial,
                     finish_days=list(finish), prove_days=list(prove),
                     difficulty=difficulty, working=working, partial=partial_work,
                     missing=missing, dependencies=dependencies, evidence=evidence))


# Rounded judgement estimates against each documented bounded finish line.
# These are planning assessments, not audited completion measurements.
add('S01','Account identity and permissions','Platform',60,25,(4,9),(3,6),3,
    'Signed registration/login; selected account-denial tests',
    'Expiry/revocation and concurrent-session coverage',
    'Complete recovery, classroom sign-ins and transition qualification',
    'Session host; test identities', 'docs/HANDOFF-STORAGE-BETA-2026-11-02.md')
add('S02','Local durable browser files / OPFS','Storage',35,45,(12,25),(8,16),4,
    'Research verified generations, CAS, cleanup, upload/download crash cases',
    'Signed sync; quota, memory and migrations',
    'Desktop adoption; complete memory/eviction/recovery qualification',
    'S01, S04 and S06 contract', 'docs/HANDOFF-STORAGE-BETA-2026-11-02.md')
add('S03','Server file store','Storage',60,25,(7,15),(5,10),4,
    'Beta signed writes, permissions, version checks and process restart',
    'Folder operations, quotas and concurrent disk accounting',
    'Complete operation recovery and realistic capacity proof',
    'S01; coordinated host writers', 'docs/HANDOFF-STORAGE-BETA-2026-11-02.md')
add('S04','Synchronization and transfer protocol','Storage',50,35,(10,22),(7,14),4,
    'Beta changed-chunk transfers, conflicts and lost-reply recovery',
    'Two-device convergence, pacing, formats and bounded resources',
    'Complete end-to-end OPFS adoption and load qualification',
    'S02/S03 agreed versions and publication contract', 'docs/HANDOFF-STORAGE-BETA-2026-11-02.md')
add('S05','Desktop shell and windows','Platform',65,25,(5,12),(3,6),3,
    'Windows, workspaces, taskbar and responsive layouts',
    'Device polish, restoration and consistent themed failures',
    'Full physical-device, focus and state-restoration acceptance',
    'S06; phone and large-display access')
add('S06','Shared app host, lifecycle and commands','Platform',40,40,(10,22),(6,12),4,
    'Mount/dispose and selected stale-operation guards',
    'Account/logout cancellation and shared command contracts',
    'Universal session safety and authorized typed operations',
    'S01 and agreed S02/S04 interface', 'docs/WEBOS-WORK-QUEUES.md')
add('S07','Browser Python Notebook','Application',45,35,(10,22),(6,12),4,
    'JupyterLite/Pyodide primary workflow and local packages',
    'Jupytext/widgets/RAM models and phone layout',
    'Saved-file stale-writer fix; qualified formats and lifecycle',
    'S02/S04/S06 stable file contract; kernel assets')
add('S08','Linux guest runtime','Platform',45,30,(7,18),(5,10),4,
    'Temporary v86 boot and guest Python baseline',
    'Kernel/tool assets and interactive executable coverage',
    'Qualified supported tools, temporary files, reset and network policy',
    'Guest image/toolchain; networking policy; S06')
add('S10','Shared runtime library portfolio','Tools',40,40,(12,30),(7,15),3,
    'Several pinned/lazy-loaded library entries',
    'Consumer coverage, notices and independent disposal',
    'Complete capability inventory and one real tested consumer per capability',
    'Consumer apps; reproducible upstream runtimes', 'apps/system/README.md')
add('J01','JSketcher integration consolidation','CAD',70,25,(3,8),(7,15),4,
    'Recorded main/surfacing integrated; adapted splines/history/DXF and WebOS fixes',
    'Combined regression coverage and remaining divergent-dev feature gaps',
    'Feature-by-feature qualification and remaining confirmed regressions',
    'J03 engine builds; attributed upstream refs', 'docs/JSKETCHER_UPSTREAM_WORK.md')
add('J02','JSketcher constraints and parameters','CAD',20,45,(35,80),(20,45),5,
    'Existing mechanical sketch/feature baseline',
    'Midpoint, atomic constraint admission, dimensional relations and units',
    'Dependable mechanical profile, configurations and rejected-edit recovery',
    'Actual solver and persistent model contract', 'docs/WEBOS-SILOED-WORK.md#j02--jsketcher-constraints-and-parametric-modeling')
add('J03','Geometry engines and provenance','CAD',35,35,(25,60),(15,35),5,
    'Focused OCC/native primitive and Boolean comparisons',
    'Source/build provenance, scales, topology and tessellation',
    'Qualified capability matrix and supported model-derived geometry',
    'Kernel sources/build environment; licenses', 'docs/JSKETCHER_ENGINE_COMPARISON.md')
add('J04','Native manufacturing document','Manufacturing',25,40,(12,28),(8,16),4,
    'Research material/region binding and assignment review',
    'Authored grouping, transforms and regeneration references',
    'Durable general assignments through edits/save/reopen',
    'J02/J03 identity contract; file service', 'docs/COMBINED-RESEARCH-CHECKPOINT.md')
add('J05','Core 3MF exporter and validator','Manufacturing',30,40,(18,40),(12,25),5,
    'Two disjoint assigned boxes exported and independently validated',
    'General tessellation and overlap/contact validation',
    'Supported curved/cavity/material-region export acceptance',
    'J03 geometry and J04 metadata', 'docs/COMBINED-RESEARCH-CHECKPOINT.md')
add('J06','CAD desktop integration','Application',40,35,(12,28),(8,16),4,
    'Scoped signed-account modeling/save/reopen and viewport tests',
    'Full runtime packaging, commands and lifecycle',
    'Qualified real CAD app on phone/1080p/4K',
    'S06 file/session contract; J01/J03 runtime', 'docs/COMBINED-RESEARCH-CHECKPOINT.md')
add('J07','Enclosure acceptance project','Manufacturing',10,30,(12,25),(8,15),4,
    'Related box/metadata export experiments',
    'Body/lid/inset fixtures and edit/regeneration path',
    'Complete editable enclosure to independently verified 3MF',
    'J02-J06 supported slice; prerequisite effort excluded', 'docs/WEBOS-SILOED-WORK.md#j07--enclosure-acceptance-project')
add('J08','Advanced curves','CAD',10,30,(40,100),(20,50),5,
    'Existing curve/spline baseline',
    'Incidence/tangency and authored contact behavior',
    'Qualified ellipse/path/G2/projection curved-handle workflow',
    'J02 solver and J03 geometry', 'docs/WEBOS-SILOED-WORK.md#j08--advanced-curves')
add('J09','Assemblies and mechanisms','CAD',5,20,(60,150),(30,70),5,
    'Small assembly constraint registry',
    'Pose/reference model and incomplete persistence',
    'Durable joints, limits, couplings and linkage acceptance',
    'Dependable parts, references and assembly persistence', 'docs/WEBOS-SILOED-WORK.md#j09--assemblies-and-mechanisms')
add('P01','Physical-system document and materials','Physics',5,25,(20,45),(10,20),4,
    'Written regions/material/interface/study design',
    'Native manufacturing identities as a foundation',
    'Implemented revisioned studies and evidence-backed material semantics',
    'J04 identity contract; physical data sources', 'docs/WEBOS-SILOED-WORK.md#p01--physical-system-document-and-material-evidence')
add('P02','Meshing','Physics',5,15,(25,60),(15,35),5,
    'Selected mesher candidates and feasibility notes',
    'Runtime and tagged-domain feasibility',
    'Runnable qualified mesher with stable region/boundary attribution',
    'J03 geometry; P01 regions; runtime/license', 'docs/WEBOS-SILOED-WORK.md#p02--meshing')
add('P03','First qualified forward solver','Physics',0,15,(35,80),(25,60),5,
    'Existing solver projects identified; no integrated study claimed',
    'Formulation/runtime selection',
    'One reproducible benchmarked forward study and result provenance',
    'P01/P02; sourced material laws and reference cases', 'docs/WEBOS-SILOED-WORK.md#p03--forward-solver-integrations')
add('P04','Magnetic design search','Physics',0,10,(40,100),(30,70),5,
    'Authored acceptance problem',
    'Fixture/objective/material catalogue design',
    'Bounded search, manufactured-model regeneration and independent reanalysis',
    'Qualified P03 magnetic study; geometry and evidence', 'docs/WEBOS-SILOED-WORK.md#p04--magnetic-design-search')
add('O01','Hosting, release and recovery','Operations',60,25,(7,15),(5,10),4,
    'Separate beta; gated guarded rollout and recovery tests',
    'Reusable promotion/update path and boot recovery',
    'Qualified current main promotion and repeatable operator workflow',
    'Qualified candidate; server access; adequate disk', 'docs/HANDOFF-STORAGE-BETA-2026-11-02.md')
add('O02','Independent baseline qualification','Operations',35,40,(15,35),(8,18),4,
    'Many scoped browser/account/fault tests',
    'Physical devices, capacity and sustained multi-device behavior',
    'Complete baseline evidence at specified resource/device limits',
    'Frozen baseline; device/network access; excludes future physics QA', 'docs/WEBOS-WORK-QUEUES.md')
add('O03','Reproducibility and student guidance','Operations',55,30,(3,7),(2,5),3,
    'Remote source/notes, handoff and scoped build recipes',
    'App inventory, deferred features and prerequisite documentation',
    'Clean other-machine checkout/build and complete supported student guide',
    'Repository access; clean build host', 'docs/HANDOFF-STORAGE-BETA-2026-11-02.md')

# Each application remains independently assignable.
apps = [
('Help',80,15,(0.5,1),(0.25,0.5),1,'Static help checked','Manual and feature accuracy','Complete concise supported-feature guide'),
('Calculator',70,20,(1,3),(0.5,1.5),2,'Calculation/file workflow and pending-close guard','History and account/lifecycle edges','Complete physical-device and error acceptance'),
('Files',60,30,(6,14),(4,8),4,'Primary file operations; account and temporary Linux home','Remote-change feedback, folder operations and interruption','Complete sync/conflict-safe file and folder workflow'),
('Terminal',65,20,(5,12),(3,7),3,'xterm and independent-shell primary workflow','Interactive programs, touch and session teardown','Qualified supported terminal/device lifecycle; networking policy'),
('Linux Notebook',5,25,(15,35),(8,18),5,'Guest Python/tools foundation; launcher disabled','Kernel bridge and browser-to-guest notebook transport','Working distinct kernel with subprocess/package and recovery proof'),
('PDF Viewer',65,25,(2,5),(1,3),2,'Open/navigation/password primary workflow','Large files, search and restore failures','Device/worker/resource qualification; OCR excluded'),
('Text',65,25,(3,7),(2,4),3,'CodeMirror and scoped signed file workflow','Large files, encodings and touch','Full conflict/lifecycle/device acceptance'),
('SVG Editor',55,30,(3,8),(2,4),3,'Basic open/edit/export workflow','Complex SVG/CSS and external-resource behavior','Supported-format matrix and physical touch'),
('Excalidraw',65,25,(3,7),(2,4),3,'Files workflow and stale chooser guard','Complex SVG/images/provider audit','Resource and device/lifecycle qualification'),
('diagrams.net',60,30,(4,9),(2,5),3,'Primary file workflow and restore retry','Provider/export/version-update coverage','Qualified adapter and physical touch'),
('G-code Preview',65,25,(3,8),(2,5),3,'Primary preview; session/visibility guards','Large-file and interpretation boundaries','Physical-device and supported-code qualification'),
('Audio Editor',55,30,(4,10),(3,6),3,'Primary edit/file workflow; channel rejection','Unusual codecs, multiwindow audio','Physical audio and complete export/lifecycle coverage'),
('Image Editor',55,30,(5,12),(3,7),3,'Primary edit/file workflow; metadata warnings','Format coverage and low-copy saves','Supported-format, memory and device qualification'),
('Doc',55,30,(5,12),(3,7),3,'Report editing, file workflow and PDF output','Complex scripts, clipboard and layout','Qualified Unicode, layout and conflict/lifecycle behavior'),
('Mesh:Tool',50,30,(5,12),(4,8),4,'Basic mesh/file workflow','Undo, geometry defects and memory','Supported-edit and export correctness qualification'),
('Replicad',45,35,(7,16),(4,9),4,'Starter script/models and geometry exports','Regeneration/UI/examples','Useful qualified script-CAD workflow; not general CAD'),
('Spreadsheet',50,35,(8,18),(5,10),4,'CSV/TSV workflow; long-cell preservation','Large files/formulas/memory','Measured higher limits and correct supported round trips'),
('Data Explorer',50,35,(8,18),(5,12),4,'Import/query/pivot/chart primary workflow','Precision and large-data resource use','Exact identifiers and reproducible resource-limited workflow'),
('Kiri:Moto',50,35,(8,18),(5,12),4,'Primary workspace/file workflow','Printer/process/output profiles','Independent supported-output and device checks; no real print gate'),
('Digital Logic',55,25,(5,12),(3,7),3,'Combinational examples and truth-table files','Component coverage and UI polish','Qualified supported logic workflow; timing not implied'),
('Circuit Simulator',45,35,(7,18),(5,10),4,'Primary circuit/file workflow','Solver/probe semantics and reference cases','Qualified supported analyses; hardware validation excluded'),
('Stitch Converter',50,30,(6,15),(5,10),4,'Supported conversion/file workflow','SVG loss cases and machine format fidelity','Independent format checks; physical sewing optional external test'),
('Embroidery Studio',45,35,(10,24),(7,15),4,'Primary artwork/project workflow','Digitizing/thread/format/provider coverage','Qualified native/export and device workflow'),
('Arduino Simulator',45,35,(12,28),(7,15),4,'Real AVR firmware and GPIO examples','Compiler options/peripheral models','Qualified source-build-run-save loop for supported board'),
('Pico Simulator',35,40,(15,35),(10,20),5,'Supported firmware/serial and file workflow','Flash/peripheral/reset behavior','Qualified real-firmware project lifecycle and explicit limits'),
('Electronics Design',35,40,(18,40),(12,25),5,'Primary project workflow','Part coverage and cross-view consistency','Useful synchronized breadboard/schematic/PCB and exports'),
('Circuit Lab',20,40,(20,45),(12,25),5,'Scoped solver/close-guard research','Runtime/model source and packaging','Distributed usable circuit study workflow'),
('PCB Design',10,30,(25,55),(15,30),5,'Research design/browser prototype','Dependency/build and fabrication workflow','Usable design-to-verified-fabrication-output baseline'),
('Microduck',50,35,(10,25),(8,18),4,'Live two-account project workflow','Runner, physical touch and model coverage','Qualified controls/recovery with honest simulation limits'),
('Browser (experimental)',20,35,(30,75),(15,35),5,'Experimental render/relay source','Compatibility, profiles, policy and file integration','Supported-site baseline; arbitrary website parity excluded'),
]
for n,d,p,f,v,k,w,q,m in apps:
    deps = {'Files':'S02/S03/S04/S06; folder-operation contract',
            'Terminal':'S08 guest runtime; S06; physical phone',
            'Linux Notebook':'S08 guest Python; kernel bridge; S06'}.get(
                n, 'S06 file/session contract; physical device where applicable')
    add('APP-'+n.lower().replace(' ','-'),n,'Application',d,p,f,v,k,w,q,m,
        deps)

# Each title is independently scoped, preserving the existing four groups.
games = [
('Falling Blocks','Arcade',65,25,(2,5),(2,4),2,'Rules, save/lifecycle, emulated touch; authored Rive art','Physical touch/audio and full play acceptance'),
('Chess Study','Arcade',60,30,(3,7),(2,5),3,'AI and saved-game workflow','Rules/AI limits, full playthroughs and physical touch'),
('Solitaire','Arcade',65,25,(2,6),(2,5),3,'One draw-one victory and account reopen','Draw-three and broader deals/touch'),
('Snake Garden','Arcade',50,30,(4,10),(3,6),3,'Preview rules and account workflow','Final artwork and complete touch/play acceptance'),
('Sky Courier','Arcade',45,35,(5,12),(4,8),3,'Steering/firing and saved preview','Full campaign, artwork and physical touch'),
('Lantern Leap','Arcade',45,35,(5,12),(4,8),3,'Overlapping input/focus/save guards','All rooms, artwork and physical touch'),
('Garden Defense','Arcade',45,35,(5,12),(4,8),3,'Map/pending-save interactions','Full waves, artwork and physical touch'),
('Pocket Rally','Arcade',45,35,(5,12),(4,8),3,'Input/focus/account save','All races, artwork and physical multitouch'),
('Physics Playground','Physics games',40,35,(7,18),(5,12),4,'Interactive preview and account workflow','Complete challenges, art and separately tested XR'),
('Marble Works','Physics games',50,30,(5,12),(4,8),3,'Pause/save/reopen','All eight puzzles, art and physical touch'),
('Stack & Balance','Physics games',50,30,(4,10),(3,7),3,'Touch cancellation and saves','Complete challenge set, art and physical devices'),
('Sling Targets','Physics games',50,30,(4,10),(3,7),3,'Aim interruption and dirty settings','All arrangements, art and physical touch'),
('Gravity Pinball','Physics games',55,25,(3,8),(3,6),3,'Save/reopen and input focus','Complete play acceptance, art and physical touch'),
('Kinetic Relay','Physics games',50,30,(4,10),(3,7),3,'Step/save/deleted-file protection','All puzzles, art and physical touch'),
('Tabletop Bot Arena','Physics games',45,35,(5,12),(4,8),3,'Independent inputs and file guards','Full cup, art and physical devices'),
('Clockwork Room','World games',55,30,(4,10),(4,8),3,'Four mechanisms and save recovery','Full content, art and physical-device review'),
('Crystal Defense','World games',45,35,(5,12),(4,8),3,'Pause/deleted-save checks','Eight-wave playthrough, art and physical touch'),
('Drone Circuit','World games',45,35,(5,12),(4,8),3,'Focus/input and file workflow','Full course, art and physical multitouch'),
('Pocket Golf','World games',50,30,(4,10),(4,8),3,'In-flight save and hole-change guards','All holes, art and physical touch'),
('Target Garden','World games',45,35,(5,12),(4,8),3,'Pointer cancellation and independent inputs','Full rounds, art and devices'),
('Orbital Courier','World games',40,40,(7,18),(6,12),4,'Controlled mission checkpoints and saves','Uninterrupted mission, art, touch and XR'),
('Clockwork Quest','World games',55,30,(5,14),(5,12),4,'Full quest/account reopen; mocked XR lifecycle','Real headset, art and physical touch'),
('Owl Companion','Interactive games',45,35,(4,10),(3,7),3,'Interactive/account preview','Authored art and physical-device acceptance'),
('Reactive Control Desk','Interactive games',50,30,(4,10),(3,7),3,'Pending save and account reopen','All orders, art and physical touch'),
('Story Cards','Interactive games',50,30,(4,10),(3,7),3,'Account workflow and isolation','Complete story, art and physical touch'),
('Expression Puppet','Interactive games',50,30,(4,10),(3,7),3,'Poses/challenge and account reopen','Art, assistive technology and physical touch'),
('Rhythm Garden','Interactive games',45,35,(5,12),(4,9),4,'Input/save and accessibility activation','Full medal runs, art and physical audio timing'),
('Memory Garden','Interactive games',60,25,(3,7),(2,5),2,'Full keyboard game and account reopen','Art, assistive technology and physical touch'),
]
for n,g,d,p,f,v,k,w,m in games:
    add('GAME-'+n.lower().replace(' ','-'),n,g,d,p,f,v,k,w,
        'Procedural presentation; selected interaction/account cases',m,
        'S06; final assets and physical devices/headset where required',
        'docs/GAME_PREVIEW_REVIEW.md')
for n in ['Math Path','Fraction Farm','Word Weaver','Rule Detective','Market Math','Pocket Conquest','Tile Islands']:
    add('LEARN-'+n.lower().replace(' ','-'),n,'Learning games',10,25,(10,25),(6,12),4,
        'Pure rules model/tests; menu disabled','Rule core; no released game UI',
        'Usable UI, assets, file adapter and playthrough/device acceptance',
        'Final game design/assets; S06', 'docs/APP_STATUS.md')

for n,f,p,k,w in [
    ('Photo Gallery',(5,12),(3,6),3,'Selected viewer/library candidates'),
    ('Video Player',(7,18),(4,8),3,'Selected playback/runtime candidates'),
    ('Music Player',(5,12),(3,6),3,'Audio playback libraries identified'),
    ('E-book Reader',(8,20),(5,10),4,'Reader/runtime candidates identified'),
    ('News Reader',(8,18),(4,9),3,'Readability/feed candidates identified'),
    ('Maps',(10,25),(6,12),4,'Map library capability; map data/style not bundled'),
]:
    add('NEXT-'+n.lower().replace(' ','-'),n,'Requested apps',0,20,f,p,k,w,
        'Inventory and integration design; user app not qualified',
        'Actual local-file user workflow and lifecycle/device qualification',
        'Verify source/runtime; content/data licensing; S06', 'docs/WEBOS-WORK-QUEUES.md')


def midpoint(v):
    return sum(v) / 2


def duration(v):
    def fmt(n):
        return str(int(n)) if int(n) == n else str(n)
    return f'{fmt(v[0])}–{fmt(v[1])} d'


RISK = {1:'Low', 2:'Moderate', 3:'High', 4:'Very high', 5:'Research / very high'}
ROWS.sort(key=lambda r:(midpoint(r['finish_days']), midpoint(r['prove_days']), r['silo']))
for i, r in enumerate(ROWS, 1):
    r['rank'] = i
    assert 0 <= r['done_pct'] <= 100 and 0 <= r['partial_pct'] <= 100
    assert r['remaining_pct'] >= 0 and 1 <= r['difficulty'] <= 5
    assert 0 <= r['finish_days'][0] <= r['finish_days'][1]
    assert 0 <= r['prove_days'][0] <= r['prove_days'][1]
assert len({r['id'] for r in ROWS}) == len(ROWS)

INTRO = '''Planning estimates dated 2026-11-03, based on the saved 2026-11-02
checkpoint and existing app review notes. These percentages are rounded scope
judgements, not audited measurements or a project completion score. Done means
supported by the recorded scoped evidence; partial means implemented/research
work with acceptance still open. The remainder is missing or unverified.
The three shares are mutually exclusive and total 100%; do not add done+partial
and call it complete. Do not average rows into an overall percentage.

Times are rough remaining focused engineering effort for each documented
bounded finish line: one day = 8 hours. Finish excludes the separate prove
column; prove includes additional testing, independent review and fixing
defects found there. Dependencies, build/device access and waiting are excluded.
Expect estimates to move after a bounded audit. They are not agent runtime or
calendar delivery promises. Future solver/mesher rows cover a first qualified
workflow, not every physics formulation. The qualification row covers the
current baseline, not all future apps; avoid double-counting it with per-app QA.

Difficulty 1–5 also expresses expected first-implementation rework risk:
1 low, 2 moderate, 3 high, 4 very high, 5 research-heavy/very high. These are
judgement bands, not statistically measured failure probabilities. Proof means
passing the agreed acceptance, not mathematical proof or hardware safety.
Game effort assumes final assets and required devices become available;
external artwork, hardware acquisition and content licensing are not included.

Sorted by midpoint of remaining implementation effort, then proof effort.
This is a shortest-job list, not the recommended execution order. A dependent
enclosure or physics task may be short itself but cannot start before its inputs.
Development remains paused. This report does not perform a fresh live audit.
'''

payload = dict(date='2026-11-03', basis='Saved checkpoint and scoped app evidence',
               methodology=INTRO, rows=ROWS)
(ROOT/'SILO-MATRIX.json').write_text(json.dumps(payload, indent=2)+'\n')
columns = ['rank','id','silo','group','working','partial','missing','done_pct',
           'partial_pct','remaining_pct','finish_days','prove_days','difficulty','dependencies','evidence']
with (ROOT/'SILO-MATRIX.csv').open('w', newline='') as f:
    writer=csv.DictWriter(f, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    for r in ROWS:
        entry={k:r[k] for k in columns}
        entry['finish_days']=duration(r['finish_days'])
        entry['prove_days']=duration(r['prove_days'])
        writer.writerow(entry)
md = ['# Silo planning matrix\n',INTRO,'\n',
      '| # | Silo | Working | Partial | Missing / not qualified | Done | Partial | Finish | Prove afterward | Difficulty / rework |',
      '|---:|---|---|---|---|---:|---:|---:|---:|---|']
for r in ROWS:
    md.append(f"| {r['rank']} | **{r['silo']}** ({r['id']}) | {r['working']} | {r['partial']} | {r['missing']} | {r['done_pct']}% | {r['partial_pct']}% | {duration(r['finish_days'])} | {duration(r['prove_days'])} | {r['difficulty']}/5 · {RISK[r['difficulty']]} |")
md += ['\nDependencies and evidence references are in the JSON/CSV and the expanded interactive report.',
       '\nScope: [separate silo checklists](../WEBOS-SILOED-WORK.md). Status: [handoff](../HANDOFF-STORAGE-BETA-2026-11-02.md).',
       '\nSource reports: `docs/APP_STATUS.md`, `docs/GAME_PREVIEW_REVIEW.md`, `docs/WEBOS-WORK-QUEUES.md`, and the CAD research notes.']
(ROOT/'SILO-MATRIX.md').write_text('\n'.join(md)+'\n')

doc = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WebOS · silo planning matrix</title>
<style>
:root{color-scheme:dark;--bg:#15181d;--panel:#20252d;--ink:#edf0f5;--muted:#b6c0ce;--edge:#394250;--green:#63c99b;--amber:#edbf68}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}
header,main{padding:24px clamp(16px,3vw,52px)}header{border-bottom:1px solid var(--edge);background:#1c2129}h1{font-size:clamp(24px,3vw,38px);margin:4px 0 12px;letter-spacing:-.025em}p{max-width:1100px;margin:8px 0;color:var(--muted)}.eyebrow{text-transform:uppercase;font-size:12px;letter-spacing:.14em;color:#83b8ff}.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin:18px 0}label{font-size:13px;color:var(--muted);display:grid;gap:5px}input,select,button{font:inherit;color:var(--ink);background:#252c36;border:1px solid #4b5869;padding:9px 12px;border-radius:7px}input{width:min(390px,85vw)}button{cursor:pointer}.stats{display:flex;gap:20px;flex-wrap:wrap;color:var(--muted);font-size:13px}.legend{display:flex;gap:18px;flex-wrap:wrap;margin:12px 0}.dot{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}.table-wrap{overflow:auto;border:1px solid var(--edge);border-radius:10px;max-height:72vh}table{border-collapse:collapse;width:100%;min-width:1580px}th{text-align:left;position:sticky;top:0;background:#2a313d;z-index:1;font-size:12px;text-transform:uppercase;letter-spacing:.03em;white-space:nowrap}td,th{padding:12px;border-bottom:1px solid var(--edge);vertical-align:top}td{font-size:13px}tr:nth-child(even){background:#1c2128}tr:hover{background:#26303d}td.desc{min-width:210px;max-width:300px}td.scope{min-width:220px;max-width:270px}.minor{display:block;color:var(--muted);font-size:11px;margin-top:6px}.bars{display:flex;height:7px;min-width:105px;border-radius:8px;overflow:hidden;background:#4a5361;margin-top:7px}.bar-done{background:var(--green)}.bar-partial{background:var(--amber)}.numbers{white-space:nowrap;font-variant-numeric:tabular-nums}details{margin:18px 0;padding:14px 16px;background:var(--panel);border:1px solid var(--edge);border-radius:8px}summary{cursor:pointer;font-weight:650}details p{white-space:pre-line}.empty{padding:30px;color:var(--muted)}a{color:#9cc7ff}.sr{position:absolute;left:-9999px}@media print{.table-wrap{overflow:visible;max-height:none;border:none}table{min-width:0}body{background:white;color:black;font-size:9px}td,th{padding:5px;background:white!important;color:black;font-size:8px}header,main{padding:10px}.toolbar{display:none}th{position:static}.minor,p{color:#444}details{display:block}}
</style>
<header><div class="eyebrow">Planning checkpoint · 03 Nov 2026 · development paused</div><h1>Independent work, one matrix.</h1>
<p>Every app and domain has its own finish line. These are rounded planning estimates from saved evidence, with implementation and proof shown separately.</p>
<div class="legend"><span><i class="dot" style="background:var(--green)"></i>Done within recorded scope</span><span><i class="dot" style="background:var(--amber)"></i>Partial / research</span><span><i class="dot" style="background:#4a5361"></i>Missing or unverified</span></div>
</header><main>
<div class="toolbar"><label>Find a silo<input id="search" type="search" placeholder="Files, JSketcher, account, game…"></label><label>Area<select id="group"><option value="">All areas</option></select></label><label>Order<select id="sort"><option value="finish">Least implementation effort</option><option value="proof">Least proof effort</option><option value="total">Least finish + proof effort</option><option value="done">Most done</option><option value="risk">Lowest difficulty</option><option value="name">Name</option></select></label><button id="reset">Reset</button><button id="csv">Export filtered CSV</button></div>
<div class="stats"><span id="count" role="status" aria-live="polite"></span><span>1 engineering day = 8 focused hours</span><span>Waiting on dependencies is excluded</span></div>
<details><summary>How to read the percentages, time and risk</summary><p id="method"></p></details>
<div class="table-wrap"><table><caption class="sr">Silo working state, remaining effort and proof estimates</caption><thead><tr><th>#</th><th>Silo / dependencies</th><th>Working</th><th>Partial</th><th>Missing / not qualified</th><th>Done</th><th>Partial</th><th>Finish</th><th>Prove afterward</th><th>Difficulty / first-pass rework</th></tr></thead><tbody id="body"></tbody></table><div id="empty" class="empty" hidden>No matching silos.</div></div>
<p>Percentages are not audited completion scores. Sorting by shortest task is not dependency order. Open an app row’s evidence reference and its silo checklist before assigning implementation.</p>
<p>Offline report: no third-party code, analytics or network calls. JSON/CSV/Markdown source and the generator are committed alongside it.</p>
</main><script>
const DATA=__DATA__;
const risk={1:'Low',2:'Moderate',3:'High',4:'Very high',5:'Research / very high'};
const mid=a=>(a[0]+a[1])/2,days=a=>`${a[0]}–${a[1]} d`;
const el=id=>document.getElementById(id),escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
el('method').textContent=DATA.methodology;
[...new Set(DATA.rows.map(r=>r.group))].sort().forEach(g=>{const o=document.createElement('option');o.value=g;o.textContent=g;el('group').append(o)});
function selected(){const q=el('search').value.toLowerCase(),g=el('group').value;let rows=DATA.rows.filter(r=>(!g||r.group===g)&&JSON.stringify(r).toLowerCase().includes(q));const orders={finish:(a,b)=>mid(a.finish_days)-mid(b.finish_days)||mid(a.prove_days)-mid(b.prove_days),proof:(a,b)=>mid(a.prove_days)-mid(b.prove_days),total:(a,b)=>mid(a.finish_days)+mid(a.prove_days)-mid(b.finish_days)-mid(b.prove_days),done:(a,b)=>b.done_pct-a.done_pct,risk:(a,b)=>a.difficulty-b.difficulty,name:(a,b)=>a.silo.localeCompare(b.silo)};return rows.sort(orders[el('sort').value])}
function render(){const rows=selected();el('count').textContent=`${rows.length} of ${DATA.rows.length} silos`;el('empty').hidden=!!rows.length;el('body').innerHTML=rows.map((r,i)=>`<tr><td>${i+1}</td><td class="scope"><strong>${escape(r.silo)}</strong><span class="minor">${escape(r.id)} · ${escape(r.group)}</span><span class="minor">Depends: ${escape(r.dependencies)}</span><span class="minor">Evidence: ${escape(r.evidence)}</span></td><td class="desc">${escape(r.working)}</td><td class="desc">${escape(r.partial)}</td><td class="desc">${escape(r.missing)}</td><td class="numbers">${r.done_pct}%<div class="bars" title="Done ${r.done_pct}%, partial ${r.partial_pct}%, missing ${r.remaining_pct}%"><span class="bar-done" style="width:${r.done_pct}%"></span><span class="bar-partial" style="width:${r.partial_pct}%"></span></div><span class="minor">${r.remaining_pct}% missing</span></td><td class="numbers">${r.partial_pct}%</td><td class="numbers">${days(r.finish_days)}</td><td class="numbers">${days(r.prove_days)}</td><td>${r.difficulty}/5<span class="minor">${risk[r.difficulty]} rework risk</span></td></tr>`).join('')}
['search','group','sort'].forEach(id=>el(id).addEventListener('input',render));el('reset').onclick=()=>{el('search').value='';el('group').value='';el('sort').value='finish';render()};el('csv').onclick=()=>{const keys=['silo','group','working','partial','missing','done_pct','partial_pct','remaining_pct','finish_days','prove_days','difficulty','dependencies','evidence'];const cell=x=>'"'+String(x).replace(/"/g,'""')+'"';const csv=[keys.map(cell).join(','),...selected().map(r=>keys.map(k=>cell(k.endsWith('_days')?days(r[k]):r[k])).join(','))].join('\r\n');const u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=u;a.download='webos-silo-matrix.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};render();
</script></html>'''
serialized=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')
(ROOT/'SILO-MATRIX.html').write_text(doc.replace('__DATA__',serialized))
print(f'Wrote {len(ROWS)} separate silos; percentages validated; sorted by implementation midpoint.')
print('Shortest:', ', '.join(r['silo'] for r in ROWS[:8]))
