# PhotoCraft on a phone

A new PhotoCraft project now opens with the image and document tab visible on a phone. **Show panels** opens the regular workspace. **Hide panels** returns to the image. Fit, Zoom out and Zoom in are available with one tap. Tablet and desktop windows wide enough for the normal workspace retain their docks. The compact layout uses the width of the editor window.

On ksu.codes, a 390 × 844 viewport gave PhotoCraft 336 CSS pixels. The same blank 1920 × 1080 document previously showed a 34-pixel strip. It now shows the full page at 250 pixels wide. An emulated two-finger pinch reduced the image to 105 pixels and Fit returned it to 250. Tapping the panels button twice restored the original view. These actions also passed after reopening an edited project.

| Viewport | Production result | Screenshot |
|---|---|---|
| 390 × 844, Anon | Saved two revisions, reopened the two-layer native project from Files in the same tab, and used zoom and the panels with no private file requests | [Canvas](phone-canvas.png) · [Panels open](phone-panels.png) |
| 390 × 844, signed in | Signed back in from a fresh browser context and opened the same editable two-layer project. Changing the view preserved its saved SHA-256 | [Reopened project](phone-reopened.png) |
| 820 × 1180, Anon | Kept the regular workspace and reopened the saved project from Files using touch | [Tablet](tablet-reopened.png) |
| 1920 × 1080, Anon | Maximized the editor, placed an image layer, saved and reopened it with the same revision | [Desktop](desktop-reopened.png) |
| 3840 × 2160, signed in | Kept the full desktop workspace, placed and saved a layer, and reopened the same project in a fresh signed-in browser | [4K](4k-reopened.png) |

Each test started from **Apps → Graphics → PhotoCraft**, saved a one-layer project, placed a synthetic colored PNG as a native layer, saved again, and opened the project from **Files → Documents**. Independent parsing of the native project confirmed both revisions' layer counts and document dimensions, and the reopened bytes matched the second save. Chromium used software rendering. [Five production results](compact-results.json)

The deployed viewer was `4eb8c65d9000af710b303baf3c94dfd1260e99f5a959d684a346e527e0ca87d4`. All 18 PhotoCraft files downloaded from production matched the normal viewer build. WebOS main still pinned PhotoCraft `403994fc5f41` at the time of verification. [PhotoCraft source](https://github.com/CC-David-CC/photocraft/commit/3c2f04c5e7b6fc55349b478f62c8f90d942c9011) · [WebOS release pin](https://github.com/CC-David-CC/WebOS/commit/9bc653ceebdc22a68248e4b2fd04552e522926cf)

**Physical phone check still open.** Open a project, pinch the image, tap **Fit**, and toggle **Show panels** and **Hide panels**. Check whether the buttons are comfortable to hit and the image stays centered.
