## Calculator session filenames

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `149d4467877cdde78c087a71fcc89446d9d280058e9301b637efce6b60a14cc4` | `ae216c5a18a53cd770be832955732123eb7712b7` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Calculator `e5db161` accepts bare session names and shows the saved path with `.calc.json`. The Galaxy S10+ and desktop Chromium computed `9.5`, traced a parabola at `f(2) = 2` with slope `4`, and reopened the editable session through My files. Both downloaded a session JSON and a graph PNG. Desktop Chromium also rejected invalid JSON without discarding the session, then imported the valid file.

All 20 changed files matched over HTTPS. Hosted Chromium repeated the calculation, graph and My files workflow and confirmed the guest file cleared on reload. The backend process and account issuer retained their identity. On box-webhost, `sudo python3 -I -B /var/backups/webos-calculator-filenames-149d4467877c/deploy-viewer.py rollback` restores viewer `568dc73168cc`. [Calculator source and Galaxy S10+ screenshot](https://github.com/CC-David-CC/calculator/blob/webos/session-filenames/docs/webos-qa/PHONE.md)

