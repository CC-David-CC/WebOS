# Weather

On ksu.codes a disposable account opened Weather from Weather & Maps, selected Sacramento from the four saved cities, read a temperature, switched to **7 days**, expanded tomorrow’s details, and closed the window. All four Chromium viewports returned seven forecast rows. Touch was emulated on phone and tablet. Physical Safari and actual touch hardware remain untested.

| CSS viewport | Input | Result | App window |
|---|---|---|---|
| 390 × 844 | Touch | Pass | [Phone](phone.png) |
| 820 × 1180 | Touch | Pass | [Tablet](tablet.png) |
| 1920 × 1080 | Mouse | Pass | [Desktop](desktop.png) |
| 3840 × 2160 | Mouse | Pass | [4K](4k.png) |

The narrow phone window truncates the selected city and the “Tomorrow” label. The city picker and expanded date remain usable. The app screenshots show the actual WebOS window at each viewport size. On desktop and 4K the forecast stays in a centered column.

Release `9fd73c498d02ad91d523fbb6e97832ddbcea24c20e09c5c947cea0ce780b3583`.
