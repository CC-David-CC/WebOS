## Spreadsheet filenames, dark grid and phone tools

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `8c65e86b901ed000dfc5747b0b695a493c06e3688401aacdb7ed64672e224947` | `b26f7b875cc83e6bb559f3d46e0cc304424f58e7` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Spreadsheet `0d7e606` gives the filename field keyboard focus, adds `.codisheet` to bare names, and follows the WebOS palette. The S10+ and Chromium at 820 and 1300 CSS pixels edited the measurement workbook, recalculated its average, saved twice and opened it from My files in a fresh account session. The same sessions exported and imported CSV and XLSX. CSV carried the calculated value and XLSX carried the formula. Thirteen reference checks passed.

Fourteen asset paths matched over HTTPS. Hosted guest Chromium saved, exported and reopened the workbook and verified temporary Files cleared on reload. On box-webhost, `sudo python3 -I -B /var/backups/webos-spreadsheet-phone-workbook-files-8c65e86b901e/deploy-viewer.py rollback` restores viewer `0a387a0bf300`. [Spreadsheet phone evidence](https://github.com/CC-David-CC/spreadsheet/blob/webos/phone-workbook-files/docs/webos-qa/PHONE.md)

