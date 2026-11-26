## GridCraft workbook filenames and status layout

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `227df9c7785bae5d750ad0349b3cd0f0d9268aba17247b18451a09e0b1d76ee3` | `25e94a7d9feb1ddc32a5320e0e7b8253bce72c50` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

GridCraft `446a7df6` adds `.xlsx` to bare names and removes the light spacing around the document status bar. The assembly rebuilt the WebOS wrapper using the shared host inputs at `8c120b55` that reproduced the preceding bundle byte for byte. It retained the installed native Rust/WASM engine. The Galaxy S10+ and Chromium at 820 and 1300 CSS pixels saved and reopened an editable workbook through My files. All three saved archives had formula `=2+3*4` and result `14` in A1. Twenty-seven adapter checks passed.

All six changed assets matched over HTTPS, and hosted Chromium repeated the temporary Files workflow in a guest session. On box-webhost, `sudo python3 -I -B /var/backups/webos-gridcraft-phone-workbook-227df9c7785b/deploy-viewer.py rollback` restores viewer `8d95a743e8ae`. [GridCraft source and Galaxy S10+ screenshot](https://github.com/CC-David-CC/gridcraft/blob/webos/phone-workbook-files/docs/webos-qa/PHONE.md)

