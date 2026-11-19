# Weather applications

Both supplied archives were found at the WebOS root and verified before extraction. The originals can be deleted. Each input source file was verified against its Git import. The app sources belong at the paths below. Work continues on the parent branch `webos/weather-apps`.

| Application | Independent checkout path | Supplied archive SHA-256 | Public destination queued |
|---|---|---|---|
| Weather | `apps/pohoda` | `756cc9cee08a9ce3f9ff80d101186df42743c5aca4d716769d240fd48337a1b5` | CC-David-CC/pohoda |
| Weather Maps | `apps/isobar` | `ea064f23616b23c98733a81ef54b504f7c007048cbda3369072543d7b6de9c56` | CC-David-CC/isobar |

The upstream repositories are Sokolyanskyi/pohoda-weather and Us2id/isobar. The local publication worker enforces 20 minutes between repository creations, 15 seconds between other operations, and at least 15 minutes of global cooldown on a rate-limit response. Its private ledger is `../.webos-migration/github-publication.MJn2SZsB/STATUS.md`. Destination creation and source publication are separate. Publish reviewed source pins only.

## Current checkpoint

Both independent repositories retain the upstream history on its original branch and WebOS changes on `webos/integration`. The bare local origins are `../.webos-local-git/pohoda.git` and `../.webos-local-git/isobar.git`. Restoring the source requires no ZIP. The import commits contain all 109 Pohoda and 90 Isobar source inputs. Pohoda’s other five archive entries were generated distribution files reproduced by its build.

| App | Upstream branch and commit | Verified ZIP import | WebOS integration |
|---|---|---|---|
| Weather | `master` · `687c812` | `44119f1` | `f76f997` |
| Weather Maps | `main` · `bbf10ab` | `f766b22` | `614292f` |

The classic desktop registers both applications under **APPs → Weather & Maps** in `platform/desktop/active-system/app.js` (commit `9f9950e`). The app modules, icons, licenses and provider attributions are assembled by `scripts/build_viewer.mjs`. The shared routes, bounded in-process forecast cache and offline place lookup live in `scripts/webos_weather/`. Range requests for map model data stay in the browser. Deployment status is local qualification. The public GitHub source queue and site deployment are separate operations.

Private build and test receipts live in `../.webos-migration/weather-apps.WTGfQ3kG/`, including `zip-source-verification.json`, standalone browser checks and the assembled desktop results. Both standalone browser harnesses ran against live providers. The full local viewer build includes both weather applications and the existing Craft engines.
