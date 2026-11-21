# G-code Viewer

A disposable account uploaded a G-code file through Files on a phone-sized viewport. The file describes a square with a travel move and four extrusion moves. On each layout the reviewer launched the viewer from 3D Printing, opened the same account path, hid and showed travel, and reloaded the file. The worker parsed the file and the canvas displayed the square and travel segment.

| CSS viewport | Preview canvas, CSS pixels | Result |
|---|---|---|
| 390 × 844 | 298 × 148 | [Pass](phone.png) |
| 820 × 1180 | 728 × 218 | [Pass](tablet.png) |
| 1920 × 1080 | 1824 × 808 | [Pass](desktop.png) |
| 3840 × 2160 | 3744 × 1888 | [Pass](4k.png) |

On the phone the controls above the drawing leave only 148 CSS pixels for the preview with File path expanded. The captured window cuts off the bottom of the grid and the status text. On larger screens the complete preview and status are visible. The phone and tablet tests used touch emulation. Physical-device pinch, drag and GPU performance remain unverified.

Hosted release `9fd73c498d02ad91d523fbb6e97832ddbcea24c20e09c5c947cea0ce780b3583`.
