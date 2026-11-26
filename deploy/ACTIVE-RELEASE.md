# Active ksu.codes release

The November 25, 2026 walkthrough release is live.

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `8a2b06a99ca2f9e5382f148991d86da6df1cff81be4d779b85b504f626e0cf5d` | `fe54b6d6b0dced335520726ba293a8ee732c99b3` |
| Backend | `13193818d7f70b10e01934b3e2ca4c2efdbdd2ede46bda671c1171cbfd87abcd` | `32abd64fcdf494a62ab874799b753d580b4933c2` |

The public viewer contains 135 launcher entries. Desktop and compact Chromium on ksu.codes verified Files recovery and retry in Document Editor, SheetJS Spreadsheet, Data Explorer and PDF.js. Anonymous and registered workflows preserved the original file bytes. The paired HTTPS cutover retained the account issuer and backend instance. Safari and physical-device checks are open.

The viewer and backend have independent source assemblies. The backend build uses the exact retained production Accounts and Runtime sources recorded in its manifest. GitHub carries the backend input assembly on `release/ksu-backend-20261125`. The build checkout on `main` includes the password reset validation change and the public source pins below.

## Public source pins for retained Craft inputs

| App | Packaged source | Public build checkout |
| --- | --- | --- |
| figcraft | `2837cfdc32e3f2ec9746e7c047189c7f09f540f6` | `db8862f37ffaaebe51bcdbd1ea042751a2ec1720` |
| lightcraft | `fab135fc4ffb5db1354e95a094b19b4cdaf1f872` | `b3eea00a67affbcb1141ac835be4da46420bb053` |
| vectorcraft | `c54691a43f7ab304f083121064bcbab8b7b33a7b` | `70b4dab5687d8923434240f32a5f1c797f7dee4a` |

FigCraft is tree-identical at both commits. LightCraft and VectorCraft use the same runtime source, with public-source documentation and branding differences. The packaged binaries and exact source are retained with the release.

Use the pinned source and the verified prepared app inputs for incremental builds. The commands in [README.md](../README.md#build-the-core-viewer-from-a-checkout) build the core viewer. A full cold rebuild of all hosted apps remains open.

Hosted rollback restores viewer `e50026bd9dff8e0b7d852a10e2b95fe09ebb733af951f2f2cfae978f5c8c236d` and backend `b7f0816a7eddef49e96a4bfd2b3f8b88a0ddb2770228e4b348154dddf082cd1b` together.

[Live release manifest](https://ksu.codes/viewer-release.json)
