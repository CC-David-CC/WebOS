## ProjectCraft phone scheduling and Files

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `ee39f4de7bb845dee1837b7fd460303921d34b66e317b9c429d31ed9312b8fd9` | `03ad63a6943bd2e84862833118c119b81681da69` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

ProjectCraft `251f396` and Desktop adapter `77daaa6` passed the Galaxy S10+ task, Gantt and editable Files workflow. The two-day draft ran November 26–27 and the dependency moved the review to November 30. CSV and Microsoft Project XML showed those dates and the same dependency. The phone reopened both exports through ProjectCraft. Phone and Chromium at 820 and 1300 CSS pixels reopened the native `.projectcraft` file in fresh signed-in sessions and saved a second edit. Status text measured 11.25:1 in dark mode, and the ready footer took about 22 CSS pixels. Twenty-four Desktop tests passed.

Eighteen asset paths matched over HTTPS. Hosted guest Chromium repeated task scheduling, both exports, native save, reopen and resave. Reload cleared the temporary project. On box-webhost, `sudo python3 -I -B /var/backups/webos-projectcraft-phone-files-ee39f4de7bb8/deploy-viewer.py rollback` restores viewer `0901c5fd1940`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/desktop/blob/webos/projectcraft-phone-files/active-system/webos-app-bridges/projectcraft/docs/webos-qa/PHONE.md)
