# Signed generic source-bound plate + linear hole pattern

**Prepared, not executed.** This new driver must wait for exact fresh combined
core/desktop/outer-bundle pins and the parent-owned signed fixture. No older
app is substituted as qualification of the new commands.

All mutations use the actual registered desktop commands. The exact reusable
module `apps/system/jsketcher/examples/source-bound-pattern.mjs` is imported by
the Node driver and called through a thin transport proxy: its command descriptor
list is the real mounted window's public list; execute forwards to the real
public registry in that window. No fake model/native output is supplied. The
driver separately imports the actual served outer module, checks its example
export and invokes one readonly public inspection through the actual browser
registry. That check qualifies import/export availability separately from the
full recipe execution through Node transport.

The recipe authors a constrained100×50 source, selected extrusion20, centeredD10,
four cornerD4/offset8, twoR3 fillets, two1mm chamfers, then a source-local+X pattern
count3 including the centered seed at20mm spacing. Source/region/outer connector
IDs are discovered, not invented or extracted from private native indices. The
example takes four actual original line connector records, chooses one and its
unique opposite by disjoint incident IDs, then chamfers the two remaining IDs.
It uses the generic single-part owned path, never the old bracket helper.

Planned checks: creation append Undo/Redo; source150×30/depth25 and seedD14 full
replay; count2/spacing30 edit Undo/Redo; count4/spacing15; overlap/outside/count1/
over-budget/stale refusal preservation; public inch display without canonical
model/chronology changes; normal native Save+server sync, fresh Open, count/
spacing reedit and Undo/Redo, resave/second Open and millimeter display roundtrip.
Save must contain one source sketch/profile, two semantic hole features, two edge
treatments and one semantic pattern intent; no derived Circle tools, internal
Boolean features or native identities. Source, seed, target, producer, region,
axis and build references remain exact through replay and reopen.

Independent public native metrics check volume, bounds, one valid solid and the
expected face/edge/vertex census. The detached Float32 display-ray check proves
only preview void/material placement, including material at former copied-hole
centers. It does not call private native classification or infer native topology
from preview triangles. Component84-point native evidence remains separate.
Read-only private app access is limited to accepted snapshots/source bytes,
detached display positions and ledger resource counts. No authoring/history
writer, model seed, native handle or fake successful Worker reply is used.

The harness owns fresh test accounts and contexts; closes only its contexts;
disconnects without closing shared Chrome; checks all owned context targets are
released. Ledger counts are not WASM used memory, RSS or OS reclamation claims.
Normal My files Save/Open is exercised; there is no Files race/security re-audit,
network/hosting mutation or deployment.

```
CODI_TEST_URL=http://127.0.0.1:PORT/ CODI_TEST_CDP=http://127.0.0.1:19329/ CODI_SIGNED_PINS=/path/exact-pins.json PUPPETEER_CORE_PATH=/path/puppeteer-core CODI_EVIDENCE=/tmp/new-pattern-run node test/agent-cad-corpus/source-bound-pattern/signed.test.mjs
node test/agent-cad-corpus/source-bound-pattern/check-saved.mjs /tmp/new-pattern-run
```

Puppeteer24.35.0 and trusted ordinary fixture origin are required. Source and all
actual app/Worker/native asset bytes must match the supplied frozen pins. Initial
failures are retained and reported; no weakened assertions or fake success path.
