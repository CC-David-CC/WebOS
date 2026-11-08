# One object, two explicit materials — complete workflow preparation

Not run. Freeze the composed ACAD runtime and driver source, then execute ONE
complete public workflow; no per-step tests or synthetic Native successes.

Actual authored boxes: base origin0 dimensions40×30×10, cap origin[0,0,10]
dimensions40×30×5. Both use the explicit `CODI_ENGINE_REVISION`, never a default
or migrated saved revision. One printable part `two-material` groups region
`base` PLA/blue and region `cap` PETG/yellow. The exact full interface is z10,
rectangle[0,0]..[40,30], area1200mm²; interiors are disjoint. Initial volumes
12000+6000=18000mm³. Cap height5→8 preserves that interface and produces
12000+9600=21600mm³. Material definitions remain distinct from geometric parts.

The driver performs real public creation, genuine Native metrics/point reads,
shared material assignment UndoRedo, normal native Save/server synchronization,
fresh login/Open, actual 3MF export, source-height edit UndoRedo, material rebind,
resave/export/fresh Open/reexport. It also changes the actual cap source to
interior overlap, gap, edge-only, point-only and partial-face contact, rebinds
the same assignments, and requires typed interface refusal with exact accepted
state preservation and no file in its own account. It restores source via the
public edit command and proves healthy continuation after each refusal.

```sh
CODI_TEST_URL=http://127.0.0.1:ROOT_FIXTURE/ \
CODI_TEST_CDP=http://127.0.0.1:19329 \
CODI_SIGNED_PINS=/path/to/frozen-runtime-pins.json \
CODI_EXPECT_SOURCE=EXACT_ACAD_COMMIT \
CODI_EXPECT_DESKTOP=EXACT_RUNTIME_DESKTOP_COMMIT \
CODI_ENGINE_REVISION=EXACT_REGISTERED_MANUFACTURING_NATIVE_PAIR \
CODI_EVIDENCE=/tmp/new-complete-two-material-workflow \
PUPPETEER_CORE_PATH=/path/to/qualified/puppeteer-core \
/path/to/node test/agent-cad-corpus/two-material-box-interface/workflow.mjs
```

After the full workflow produces real files:

```sh
python3 test/agent-cad-corpus/two-material-box-interface/oracle.py \
  /tmp/new-complete-two-material-workflow /path/to/desktop-repository \
  > /tmp/new-complete-two-material-workflow/independent-oracle.json
```

The independent oracle reads the actual two saved box features and public
producer receipts without constructing/parsing opaque IDs. It verifies frozen
driver Git custody separately from runtime Desktop, normal saved-byte custody,
CRC/ZIP/XML, one build item with two independently material-indexed regions,
every provenance/resource association, exact full-face/opposite-interior source
geometry, all six mesh surfaces per region, orientation/area/volume, indexed
manifold incidence/vertex links/Euler2, material/void witnesses and unchanged
edited/reopened canonical geometry. Integer fixture coordinates are exact;
volume/face area allowances are1e-6 and winding1e-7. The geometry remains two
closed material regions; no coordinate welding or triangle diagonal matching
is assumed at the interface. No arbitrary interface, embedded label, physical
material solver, slicer or physical-printer qualification is implied.

Use fresh accounts/output directories on a root-owned private fixture. The
driver owns only its browser context and disconnects the shared browser. No
service/runtime start, production writes or filesystem race probes belong here.
