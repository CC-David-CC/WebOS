## TextCraft phone status and editable files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `e91a7ae19ef02da5c0eb6157e928b6bb838c8da1d575f7f895a7936a63141129` | `d1eb8e3ecc530b3b1826a21e4e399030aa28330a` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Desktop adapter `d1f4259` fits the TextCraft editor and file status inside the app window. The Galaxy S10+ and 820- and 1300-CSS-pixel Chromium sessions created TXT and Markdown documents, cancelled and retried Save, reopened both through My files → Open With → TextCraft in fresh sign-ins, and saved a second edit to the same path. A UTF-16 LE fixture retained its byte-order mark and CRLF. The phone switched to Formatted view and displayed the revised Markdown. The editor runtime source is TextCraft `aee7b37`. Twenty-four Desktop tests passed.

Sixteen asset paths matched over HTTPS. Hosted guest Chromium saved TXT and Markdown, reopened Markdown through My files, and saved another edit. Reload cleared the guest's two files. On box-webhost, `sudo python3 -I -B /var/backups/webos-textcraft-phone-files-e91a7ae19ef0/deploy-viewer.py rollback` restores viewer `ee39f4de7bb8`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/textcraft/blob/webos/phone-files-evidence/docs/webos-qa/PHONE.md)
