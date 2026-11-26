## MetricCraft report files and dark status

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `0901c5fd19402eaf4f4c1292a88b6b9060ea07b83296e677d442b75e6ecf73f7` | `ba23aef0af077746703e62e98f79ac1cf3df4f74` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

The Desktop adapter `29eb23b` gives MetricCraft status messages 11.25:1 contrast and removes the inherited footer margins. The app runtime is MetricCraft `0fa9621`. A Galaxy S10+ and Chromium at 820 and 1300 CSS pixels imported CSV, Excel and Parquet, saved a one-page report under a bare filename, opened it from My files after a fresh sign-in, added a second page and saved again. All three embedded source digests matched before and after the edit. **Insert → New page** works at tablet width where the page-tab plus overlaps the zoom controls. Twenty-four Desktop tests passed.

Nineteen asset paths matched over HTTPS. Hosted guest Chromium repeated the three imports, edit, save, reopen and resave. Reload cleared the temporary guest report. On box-webhost, `sudo python3 -I -B /var/backups/webos-metriccraft-status-layout-0901c5fd1940/deploy-viewer.py rollback` restores viewer `8ba9fd0bb526`. [Galaxy S10+ evidence](https://github.com/CC-David-CC/desktop/blob/webos/metriccraft-status-layout/active-system/webos-app-bridges/metriccraft/docs/webos-qa/PHONE.md)
