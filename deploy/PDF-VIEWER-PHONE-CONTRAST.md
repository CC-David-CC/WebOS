## PDF Viewer reading contrast

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `0c76681810b69cbde9b20a70cc5359dab9f72d6f5c76189cfc010d60f3c08a3f` | `a735c45d9f1ca71459f32efdd239a0c852d7c811` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

PDF Viewer `67b8304` follows the WebOS palette for the toolbar, reading surface, search and file status. The toolbar, search and status text measured 10.1:1 contrast against their dark backgrounds. The Galaxy S10+, Chromium at 820 and 1300 CSS pixels, and hosted guest Chromium opened the edited PDF using **Files → Open With → PDF Viewer**, zoomed, restored fit width, and found the text added in PdfCraft. The source PDF digest matched before and after reading.

All eight changed assets matched over HTTPS. On box-webhost, `sudo python3 -I -B /var/backups/webos-pdf-viewer-phone-contrast-0c76681810b6/deploy-viewer.py rollback` restores viewer `66dcd85df4ad`. Physical-device tests for multi-page navigation, password entry and picker cancellation remain open. [PDF Viewer phone evidence](https://github.com/CC-David-CC/pdf-viewer/blob/webos/phone-reading-contrast/docs/webos-qa/PHONE.md)

