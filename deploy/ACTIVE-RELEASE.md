# Active ksu.codes release

## Scríobh manuscript files and picker contrast

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `8069281f64e82d68861f8df8f7b079ba240883afe0dc8afbe572395107984a44` | `113ab0e3d702f40748f98e8a226f1913b84918ca` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Desktop `5def3aef9e819` gives the shared Files picker hint 8.08:1 contrast in dark mode. Scríobh `afc3feb30387` records three of ten workflow groups. The Galaxy S10+ and Chromium at 820 and 1300 CSS pixels edited two ordered chapters in rich text and Markdown, cancelled and retried Save as, saved a bare filename with `.scriobh`, reopened it directly from My files, and updated the same path. A fresh registered session matched the saved project bytes. Two SQLite store tests and 24 Desktop tests passed. The 18 rebuilt Scríobh assets matched the retained runtime.

All three changed assets matched over HTTPS. The hosted guest S10+ replay repeated the manuscript and file cycle. On box-webhost, `sudo python3 -I -B /var/backups/webos-scriobh-picker-contrast-8069281f64e8/deploy-viewer.py rollback` restores viewer `c2acfe055fdc`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/scriobh/blob/webos/phone-manuscript-files/docs/webos-qa/PHONE.md)

## LoveCraft phone writing and backups

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `c2acfe055fdcdc1dbb74f50ca8de657542112cb6300454d89ca0571c47717870` | `b1e42313c656cd27e3f43b1174a79d9264f95931` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

LoveCraft `47d45201b1d0` fits the project dialogs and chapter outline into phone windows. The S10+ wrote a scene with the keyboard open, reopened it after refresh and restored an editable `.prosecraft` backup through the Android picker. Cancelling a second picker preserved the manuscript. Minimizing restored the WebOS launcher. Chromium at 820 and 1300 CSS pixels passed the edit, reopen and backup cycle. Desktop Chromium also exported the manuscript as plain text and reopened an edited outline summary in the preceding optimized preview. All five repository checks passed with 608 native tests passing and 7 existing ignored tests.

The hosted S10+ guest replay passed the manuscript and backup cycle. A desktop guest profile created on the previous viewer reopened the same browser library after the release. All 17 changed assets matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-lovecraft-compact-writing-c2acfe055fdc/deploy-viewer.py rollback` restores viewer `e91a7ae19ef0`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/lovecraft/blob/webos/compact-writing/docs/webos-qa/PHONE.md)

## Earlier November 25 walkthrough release

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

Use the pinned source and the verified prepared app inputs for incremental builds. The commands in [README.md](../README.md#build-the-core-viewer-from-a-checkout) build the core viewer. The clean-checkout packaging check uses the published WordCraft component build and retains the notices for both transitive math dependencies. A full cold rebuild of all hosted apps remains open.

Hosted rollback restores viewer `e50026bd9dff8e0b7d852a10e2b95fe09ebb733af951f2f2cfae978f5c8c236d` and backend `b7f0816a7eddef49e96a4bfd2b3f8b88a0ddb2770228e4b348154dddf082cd1b` together.

[Live release manifest](https://ksu.codes/viewer-release.json)
