# Tablet brush contact

Current TextureCraft source tested on ksu.codes was `cd2c82345a8b0f1a0d4b8795b8e4bf7a08b8e479`. The browser reported WebGL2 software rendering for the emulated 820 × 1180 touchscreen.

1. Open TextureCraft under Materials & Textures and import a triangle OBJ with texture coordinates.
2. Select **Viewport → 2D view only**. Press inside the visible grey island, hold for about a second, draw a short line, and lift.
3. Choose **File → Save**. Reopen the resulting native `.tcraft` project through Files and inspect the paint layer.

The held stroke saved zero pixel entries. Both Anon and a disposable signed-in account also lost the first stroke in full-height windows under concurrent software rendering. In a shorter window, both roles saved five pixel channels and reopened the same mesh and paint bytes. A separate full-height Anon replay saved five channels and changed all five on a second edit after reopening. Browser event tracing delivered the full touch sequence to the focused canvas.

![The full-height 2D texture view following a lost held stroke](tablet-held-brush.png)

The software issue stays open for a deployed fix. A physical tablet still needs finger and stylus checks.
