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

## Qualification and restart

The parent assembly commit is `963a5adc` on `webos/weather-apps`. The complete candidate is `f72bd3db` on `webos/weather-release-candidate`. Both branches exist in the parent’s local bare origin. The candidate uses the deployed SolidCraft pin to reuse its existing engine. The maintained source branch keeps the independently updated SolidCraft pin. The two weather apps and their shared server package are identical on both.

The server package belongs to the parent repository at `scripts/webos_weather/`. Its routes are installed by `scripts/run_development.py` and included by `scripts/package_viewer_backend.py`. The forecast cache is shared across windows and accounts within one server process. It starts empty after a server restart. It stores provider responses in memory and keeps precise user location histories out of persistent storage. There is no third GitHub repository or desktop entry for it.

Verified locally:

- 86 Weather tests, 159 Weather Maps tests, 3 shared cache tests and 4 server origin tests passed.
- In actual Chromium both apps opened together from the classic desktop, selected Seattle, displayed provider times, resized, closed and reopened. Workers returned to baseline. No automatic geolocation request, browser exception or CSP violation was observed. All 15 existing desktop regression checks passed.
- A real NWS cache test coalesced three simultaneous requests for TOP/50,55. Repeating the request added zero upstream calls. MET forecasts, NOAA GRIB range decoding, radar tiles and ten years of NCEI calendar-day observations were exercised. Coverage and provider availability still vary.
- The complete static archive passed its inventory verification (905 files, 26 app IDs). The packaged backend booted with the deployed Accounts source pin and served health, place search and actual historical observations. Release ID `6e0b1e8ca1a1826571080f8877129a0926dfab20bc8017df277efc74c81787e1`.
- Both public destinations are in the existing paced creation queue with source reviews and exact upstream/integration refs. The GitHub ledger records publication separately. Existing live sites have not received this weather candidate.

For the loopback preview, the origin is in the private checkpoint’s `desktop-origin.txt`. The qualification snapshot is `site-final/`. Receipts include `desktop-weather-receipt.json`, `existing-desktop/result.json`, `live-cache-check.json`, `packaged-backend-check.json` and `package-verification.json`. If the laptop has restarted, use the saved port on loopback with this snapshot, the existing private `disposable-accounts/` and the development server. The existing account-state marker pins the origin.
