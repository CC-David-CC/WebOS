# Contrasting rectangular inset label — whole workflow prepared, not run

Run only after root freezes the normal composed ACAD application. No tests,
Native probes, builds, browser or services ran for this source preparation.
All authoring uses actual public commands. `__CAD_APP` reads are detached
accepted-state/resources/material observations, never model/history writes.

One actual Native history: base box80×50×4 at0; tool box30×20×3 at[25,15,2];
real subtract(base,tool); independent label box30×20×2 at[25,15,2]. The Cut
consumes both genuine operands. Final outputs are pocketed lid and flush label,
assigned as ONE printable part `lid`, region `lid` PLA/blue and region `label`
PETG/white. The Native file keeps the same authored sources/material identities;
it stores no duplicate interface-proof flags or Native ordinals.

Initial truth:14800+1200=16000mm³. Five internal positive-area interfaces:
floor600mm², two X walls80mm², two Y walls120mm²; total800. Flush label top600mm²
is exterior, not another A/B interface. Real tool width30→36 and label width30→36
are explicit independent edits, not an implicit driving constraint. Mixed
UndoRedo retains IDs/Cut, then material rebind/resave/export/fresh Open/reexport.
Edited volumes14560+1440 still total16000; interface area720+80+144=944mm².
Exported material witness[58,25,3] switches from lid to label with the edit.

The whole workflow also accepts actual source states representing underfill,
overfill, protrusion/displacement, through/edge cuts, rebinds current materials,
and requires typed INTERFACE refusal with unchanged accepted state and no file.
It restores real sources and proves healthy continuation after each refusal.
Those source geometries may be valid; they must not be called invalid merely
because they are outside this sufficient flush-interface domain.

```sh
CODI_TEST_URL=http://127.0.0.1:ROOT_FIXTURE/ \
CODI_TEST_CDP=http://127.0.0.1:19329 \
CODI_SIGNED_PINS=/path/to/frozen-runtime-pins.json \
CODI_EXPECT_SOURCE=EXACT_ACAD_COMMIT \
CODI_EXPECT_DESKTOP=EXACT_RUNTIME_DESKTOP_COMMIT \
CODI_ENGINE_REVISION=EXACT_REGISTERED_MANUFACTURING_NATIVE_PAIR \
CODI_EVIDENCE=/tmp/new-complete-inset-label-workflow \
PUPPETEER_CORE_PATH=/path/to/qualified/puppeteer-core \
/path/to/node test/agent-cad-corpus/inset-label-interface/workflow.mjs
```

After the complete workflow produces real artifacts:

```sh
python3 test/agent-cad-corpus/inset-label-interface/oracle.py \
  /tmp/new-complete-inset-label-workflow /path/to/desktop-repository \
  > /tmp/new-complete-inset-label-workflow/independent-oracle.json
```

The independent oracle derives geometry from actual saved boxes/Cut and public
opaque receipt bindings. It verifies frozen driver Git custody separately from
runtime Desktop, native-file/server custody, ZIP CRC/XML, one group/two regions,
distinct material/appearance identities and all provenance/resource links.
It checks eleven pocket patches and six label faces, exact rational polygon
clipping (independent of product SAT) to exclude triangles crossing the opening,
plane/range/orientation/area, indexed manifold incidence/vertex links/Euler2,
per-region/total volumes, material/void points and five actual matching opposite
interface patches. Edited/reopened Native bytes and canonical meshes must agree.
Retained box-oracle helpers are reused without changing their source.

Integer fixture coordinates/rational patch areas are exact; volume reporting
uses1e-6mm³ and winding1e-7, neither used for fill/contact/identity. This slice
does not qualify arbitrary inset text, curved/through interfaces, physical
material solving, a slicer/printer or the future separate body/lid workflow.
Use own fresh account/outputs, close only own contexts, leave parent services
and shared browser alive, and preserve first failures without weakening checks.
