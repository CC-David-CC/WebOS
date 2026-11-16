# Organized immutable artifact inputs

These are public static reference artifacts and verified build inputs. They are separate from the independently owned source repositories. Payloads are ignored by Git; the source parent tracks only the locks, this guide and verification tools. Do not place account databases, credentials, private documents or audit logs here.

Current source-organization scope: the reference snapshot is optional recovery material, not a beta-parity requirement. The existing working-tree `input-files.json` has 87 entries and is preserved uncommitted; the separate speech lock lists 34 files. Counts below describe earlier acquisition batches. See [the current matrix](../migration/APP-MATRIX.md) for source/build gaps rather than treating those historical batch counts as completion gates.

- `reference-beta/<catalog-key>/`: complete frozen74-entry public app catalog payload,6143 files/1,028,162,239 bytes, every declared SHA256/size verified after placement. The public catalog lock identifies each immutable path and file. This is a reference/recovery snapshot, not an enabled new release or proof that every dynamic asset was declared correctly.
- `inputs/microduck/space/`: pinned public upstream rig and38 original STL meshes in the source project's native input layout.
- `inputs/microduck/policy/alpha_walking.onnx`: exact source-manifest policy bytes.
- `inputs/microduck/mujoco-noeval-3.17.0/`: three retained qualified engine files, checked against the original source pins. Exact cross-directory WASM source-build reproducibility remains unresolved; a retained binary is not an independent source rebuild.
- `input-files.json`: exact file hashes/sizes for the44 Microduck input/license files.

Run `python3 scripts/verify_artifacts.py` from the assembly to verify both sets without network access or changes. A source-only Git clone needs these explicitly locked payloads acquired or restored separately. Private verified recovery archives remain outside the source checkout. The original workspace is not a supported input location.

For a Microduck build, point `MICRODUCK_SPACE_DIR` to this directory's `inputs/microduck/space`, `MICRODUCK_POLICY` to `inputs/microduck/policy/alpha_walking.onnx` and `MICRODUCK_MUJOCO_NOEVAL` to `inputs/microduck/mujoco-noeval-3.17.0`. The source-owned tools verify input hashes before producing generated assets. Keep generated outputs separate from source and this immutable cache.

This cache closes the catalog-listed public app payload recovery only. It does not establish source rebuildability or require collecting more historical site assets for the current organized starting point.

Circuit Lab local research inputs now live at `inputs/circuit-lab/local-research-runtime/`:5 exact runtime/relink/notice files recovered from the previously verified archive. They are NOT public-release assets. The retained source/relink archive has unresolved model distribution terms, and the source app is not enabled; keep that gate intact. `input-files.json` explicitly records the restriction. The49 total locked input/license files remain ignored payloads, with hashes tracked for local recovery and testing.

Notebook pinned widget inputs are stored under `inputs/notebook/`: two wheels verified against source SHA256 pins and nineteen declared files recovered from their contents. They are offline build inputs, not a qualified complete JupyterLite build. See `input-files.json` and `migration/ASSET-COVERAGE.md`.

Speech inputs: `inputs/speech/` contains34 public runtime/model/notice files totaling97,100,582 bytes, individually locked by `engines/speech/inputs.lock.json`. Recover them with that component’s explicit fetcher; build offline with its builder. No microphone recording or test audio is stored in this cache. The public acceptance audio remains private test evidence and is not a runtime payload. This cache is separate from the existing input-files.json WIP and earlier87-file asset inventory.
