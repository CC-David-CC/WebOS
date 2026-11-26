## Text Editor appearance and save names

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `568dc73168ccc75487de4acc7a3a31bd1069cc1a814ef18b5d4fb37101d05c6f` | `b1922cb1144af3355c16bf319b41acae60d81af3` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Text `2ead172` uses CodeMirror `04feb7d` to follow the desktop's appearance in the editor, gutter and syntax. New bare save names get `.txt`, and a bare copy of a named file keeps its current extension. The Galaxy S10+ and Chromium at 820 and 1300 CSS pixels passed the signed-in save, undo, redo, copy and reopen workflows with plain text and Python files. Desktop and tablet Chromium also passed Unicode keyboard copy and paste. Fifteen Text unit checks passed.

All six changed assets matched over HTTPS. A guest Chromium replay on ksu.codes passed the temporary file cycle, confirmed the edit and Python copy, and confirmed that temporary files cleared on reload. The backend and account issuer remained the same. On box-webhost, `sudo python3 -I -B /var/backups/webos-text-theme-filenames-568dc73168cc/deploy-viewer.py rollback` restores viewer `6a15db8b719e`. [Text source and phone screenshot](https://github.com/CC-David-CC/text/blob/webos/phone-theme-and-filenames/docs/webos-qa/PHONE.md)

