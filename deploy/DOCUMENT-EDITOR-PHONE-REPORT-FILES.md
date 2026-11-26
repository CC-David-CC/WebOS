## Document Editor report filenames and dark controls

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `0a387a0bf300b06cb4bbcfcd71dd0a61f02d7ec6a1b88c15760a0f275c5b82e2` | `b3a63fbefcf05f4678d09d84bbb960bbbc8aaf42` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Document Editor `40b3c11` accepts names such as `Documents/Tide report` and adds `.codidoc` when the filename has no extension. The file controls follow the WebOS palette. The S10+ and Chromium at 820 and 1300 CSS pixels formatted a report, saved it twice, exported a separate PDF, previewed the text and reopened the editable report from My files. Desktop Chromium also reopened an explicit legacy `.doc` file. Six reference checks passed, and a malformed report retained its bytes while opening a separate recovery copy.

Fifty-one asset paths matched over HTTPS. Hosted guest Chromium replayed the report and PDF workflow and verified that the temporary report cleared on reload. On box-webhost, `sudo python3 -I -B /var/backups/webos-document-editor-phone-report-files-0a387a0bf300/deploy-viewer.py rollback` restores viewer `0c76681810b6`. [Document Editor phone evidence](https://github.com/CC-David-CC/document-editor/blob/webos/phone-report-files/docs/webos-qa/PHONE.md)

