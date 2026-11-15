# Organized immutable artifact inputs

These are public static reference artifacts and verified build inputs. They are separate from the independently owned source repositories. Payloads are ignored by Git; the source parent tracks only the locks, this guide and verification tools. Do not place account databases, credentials, private documents or audit logs here.

- `reference-beta/<catalog-key>/`: complete frozen74-entry public app catalog payload,6143 files/1,028,162,239 bytes, every declared SHA256/size verified after placement. The public catalog lock identifies each immutable path and file. This is a reference/recovery snapshot, not an enabled new release or proof that every dynamic asset was declared correctly.
- `inputs/microduck/space/`: pinned public upstream rig and38 original STL meshes in the source project's native input layout.
- `inputs/microduck/policy/alpha_walking.onnx`: exact source-manifest policy bytes.
- `inputs/microduck/mujoco-noeval-3.17.0/`: three retained qualified engine files, checked against the original source pins. Exact cross-directory WASM source-build reproducibility remains unresolved; a retained binary is not an independent source rebuild.
- `input-files.json`: exact file hashes/sizes for the44 Microduck input/license files.

Run `python3 scripts/verify_artifacts.py` from the assembly to verify both sets without network access or changes. A source-only Git clone needs these explicitly locked payloads acquired or restored separately. Private verified recovery archives remain outside the source checkout. The original workspace is not a supported input location.

For a Microduck build, point `MICRODUCK_SPACE_DIR` to this directory's `inputs/microduck/space`, `MICRODUCK_POLICY` to `inputs/microduck/policy/alpha_walking.onnx` and `MICRODUCK_MUJOCO_NOEVAL` to `inputs/microduck/mujoco-noeval-3.17.0`. The source-owned tools verify input hashes before producing generated assets. Keep generated outputs separate from source and this immutable cache.

Full disk organization is not complete until the remaining nonregistered/platform/source areas and additional site/guest assets are reconciled. This cache closes the catalog-listed public app payload recovery only.
