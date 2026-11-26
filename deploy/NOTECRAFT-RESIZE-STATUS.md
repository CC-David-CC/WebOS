## NoteCraft resize warning and notebook save

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `1899c82ed7a896a16bdd68786859268e564e2724486a1b17cd51917a1bd3aa0a` | `bb2f2d765aa687a6f178969bce1f64ec4158e48e` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

NoteCraft `4b751a8` keeps deferred resize notifications out of the notebook failure banner. The retained native editor on the S10+ completed the welcome wizard, accepted a page title edit with the Android keyboard, saved a bare name as `.notecraft`, and reopened the editable page from My files. Tablet and desktop Chromium reopened the HTML page and saved copies. An injected error event with an error object still displayed a failure.

All 27 changed asset paths matched over HTTPS. Hosted guest Chromium opened the edited notebook archive from My files. On box-webhost, `sudo python3 -I -B /var/backups/webos-notecraft-resize-status-1899c82ed7a8/deploy-viewer.py rollback` restores viewer `07803e135d2f`. [NoteCraft phone evidence](https://github.com/CC-David-CC/notecraft/blob/webos/phone-resize-status/docs/webos-qa/PHONE.md)

