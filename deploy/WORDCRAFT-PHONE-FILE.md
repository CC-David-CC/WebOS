## WordCraft phone File, Tools and Save As

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `42da3a24b9fe5107d40235aa450338103d6773aa46132bd521c37c17dea4e61b` | `68a316fbde0a8058c34ac560f7eabfe7460f5e4b` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

The `7c4dcedf` WordCraft engine adds a compact File panel and fixes the Tools tap. Save As adds the suggested extension when the entered name has none. The Galaxy S10+ ran Undo, opened and canceled the file picker, saved a DOCX, and reopened the editable document from My files. File opened with the keyboard visible and dismissed. Chromium at 820 and 1300 CSS pixels passed the wide File, Open and Save As flow. The native Backstage suite passed 30 checks and the Node wrapper passed 43.

The rollout verified 221 assets over HTTPS. Hosted Chromium replayed Tools, Undo and File Open and verified that the save footer takes no space when empty. The backend process and account issuer retained their existing identity. On box-webhost, `sudo python3 -I -B /var/backups/webos-wordcraft-phone-file-42da3a24b9fe/deploy-viewer.py rollback` restores viewer `baadc037b6c6`. [WordCraft source](https://github.com/CC-David-CC/wordcraft/tree/webos/compact-tools-touch) · [Galaxy S10+ screenshots](https://github.com/CC-David-CC/wordcraft/blob/webos/qa-phone/docs/webos-qa/PHONE.md)

