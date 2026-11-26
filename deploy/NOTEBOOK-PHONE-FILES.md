## Python Notebook phone and standard File controls

| Deployment | Release digest | Source assembly |
| --- | --- | --- |
| Viewer | `6a15db8b719eae49425585db340d6829a59fdf3cc7bb30eee2f86f22174936f2` | `c38369f8478c33a0fb0ab0968778d081e0c54a65` |
| Backend | `ad91cba3b6b4c2e14a63e76fcf2ddbf9d7ae1b67b7338286c362744695586d14` | `ccda1a3f893e2bfd941a89ebe1fc9f05c5ec93da` |

Notebook source `25dd759` puts Open, Save and Data files on phones, uses `.ipynb` for bare names, and preserves the standard Jupyter File menu at larger widths. The exact package ran real Pyodide on the S10+, saved an editable notebook, reopened it through My files, imported a CSV and exported a file containing `12`. Chromium repeated the save and reopen flow at 1400 CSS pixels and kept the standard File menu and current filename at 820 CSS pixels. All nine Notebook reference checks passed.

The rollout verified 598 assets over HTTPS and applied the existing Notebook-specific browser policy to the new runtime path. Hosted Chromium opened a guest notebook and ran the real Python example. The backend process and account issuer retained their existing identity. On box-webhost, `sudo python3 -I -B /var/backups/webos-notebook-phone-files-6a15db8b719e/deploy-viewer.py rollback` restores viewer `42da3a24b9fe`. [Notebook source](https://github.com/CC-David-CC/notebook/tree/webos/notebook-phone-files) · [Galaxy S10+ screenshot](https://github.com/CC-David-CC/notebook/blob/webos/qa-phone/docs/qa/PHONE.md)

