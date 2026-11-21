# Chess Study

A disposable account launched Chess Study from Games → Arcade games on ksu.codes. In each viewport the reviewer chose **Tactical exercises → Back-rank finish A**, started the exercise, resumed play, and moved the rook from a1 to a8 using the visible board. The move list recorded `Ra8#`, the game reported the exercise solved, and Undo turn restored the initial position.

| CSS viewport | Input | Board width | Result |
|---|---|---:|---|
| 390 × 844 | Emulated touch | 308 px | [Pass](phone.png) |
| 820 × 1180 | Emulated touch | 498 px | [Pass](tablet.png) |
| 1920 × 1080 | Mouse | 512 px | [Pass](desktop.png) |
| 3840 × 2160 | Mouse | 512 px | [Pass](4k.png) |

At phone width the board takes most of the available window width. At 4K it occupies one corner of a maximized window. Physical phone and iPad testing, a full game against the AI, and saved-study reopening still need separate checks.

Hosted release `9fd73c498d02ad91d523fbb6e97832ddbcea24c20e09c5c947cea0ce780b3583`. The screenshots show the real app window with the completed move.
