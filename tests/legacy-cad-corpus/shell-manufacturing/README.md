# Complete shell manufacturing workflow — prepared, not run

This driver uses the actual registered public command API and retained
`source-bound-shell.mjs` example, normal material assignments, native Save and
fresh Open, and the protected Native controlled-mesh → Worker 3MF → My files
export path. It never writes model/history or injects geometry/storage replies.
The `__CAD_APP` reads are detached accepted-state/resource/material observations.
No runtime, services or browser were started for this preparation.

The composed source must contain the Core shell manufacturing admission repair
and exact optional shell assets. It must retain the authored part's explicit
build, not select a new default:

```
sha256:57b74074e0a249b917ac68357fbd003c37d1ab61897206886b575088e6995858:60dc956b08e01f43d08a48035a384e478e63bb34fb55f21a152c8cd12e8b8947
```

One whole workflow:

1. Public box100×50×20 → actual builder Z_MAX discovery → inward shell2.
   Check native volume20512mm³, bounds, material/void/boundary points and cleanup.
2. Assign one printable part `shell`, one region `main`, PLA/blue. Shared
   assignment UndoRedo; normal Save/server-byte equality/fresh Open.
3. Export `initial.3mf`; preserve accepted source, metrics, journal and resources.
4. Thickness2→3 and source box120×60×25, each with actual shared UndoRedo.
   Refuse collapse without replacing the accepted part; confirm the ordinary
   material rebind proposal. Expected edited volume44568mm³.
5. Save/export edited, fresh login/Open, unchanged Save and reopened export.
   The same box/shell feature IDs, opaque removed-face identity, backend and
   material/appearance IDs remain bound throughout.

After root freezes the complete composed fixture, run once with fresh outputs:

```sh
CODI_TEST_URL=http://127.0.0.1:ROOT_FIXTURE/ \
CODI_TEST_CDP=http://127.0.0.1:19329 \
CODI_SIGNED_PINS=/path/to/frozen-runtime-pins.json \
CODI_EXPECT_SOURCE=EXACT_CORE_COMMIT \
CODI_EXPECT_DESKTOP=EXACT_RUNTIME_DESKTOP_COMMIT \
CODI_EVIDENCE=/tmp/new-complete-shell-manufacturing \
PUPPETEER_CORE_PATH=/path/to/qualified/puppeteer-core \
/path/to/node test/agent-cad-corpus/shell-manufacturing/workflow.mjs
```

Freeze the driver commit first. It records `driverSourceCommit` separately
from runtime Desktop pins. The offline oracle verifies all producing source
hashes using those frozen Git objects, not the present working tree. Once the
complete workflow has produced real artifacts:

```sh
python3 test/agent-cad-corpus/shell-manufacturing/oracle.py \
  /tmp/new-complete-shell-manufacturing /path/to/desktop-repository \
  > /tmp/new-complete-shell-manufacturing/independent-oracle.json
```

The oracle derives dimensions/thickness from the actual two saved features and
corroborates their public receipts. Opaque face/body IDs are compared, never
parsed or regenerated. It independently reads CRC/ZIP entries and 3MF XML,
millimeter units, material/color/resource mappings, and the source revision.
It checks indexed edge incidence and vertex links, one connected closed
boundary with Euler2, oriented planar patches and their analytic areas, actual
open top without triangles spanning the cavity, volume, bounds and winding
material/void witnesses. Curved-mesh approximation bounds are not needed for
this entirely planar fixture. Frozen bounds1e-6mm, surface coordinates1e-7mm,
volume1e-6mm³, surface area1e-6mm² and winding1e-7 are distinct numerical checks.
Edited/reopened source files and canonical oriented triangles must agree.

This bounded one-region part does not qualify arbitrary shells, multi-material
interfaces, all inherited Native capabilities, a slicer or physical printing.
The complete shell modeling proof is separate from this not-yet-run export
workflow. Preserve any actual first failure before correcting source or driver;
do not weaken the analytic or identity checks.
