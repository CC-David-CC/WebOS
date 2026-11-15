# Android Chrome toolbar behavior

On compact Android Chromium-style browsers with a coarse pointer and an
unzoomed visual viewport, the page provides 180 pixels of top-level scroll.
The desktop stays sticky to the visible viewport; its own scrollable apps keep
their normal scrolling, and keyboard/viewport resize continues to use the
VisualViewport API. The extra space gives the browser an opportunity to hide
its toolbar on a native page scroll. There is no fullscreen control or API.
Desktop and nonmatching browsers retain the existing non-scrollable page.

The browser decides whether to collapse its toolbar. Gestures consumed by an
app's own scrolling, drawing canvas, window drag handle or contained scroller
may not reach the document. When the extra scroll range is exhausted, further
swipes cannot scroll it until the user scrolls back. This is not a guarantee
that the toolbar will hide on every gesture or browser version.

`tests/android-chrome-scroll-review.test.mjs` uses Android user-agent and touch
emulation in desktop Chromium to check native document swipes, the end of the
scroll range, sticky desktop geometry, a Text editor's independent scrolling
and account save, viewport shrink/restore, orientation-sized changes, and the
desktop baseline. It does not contain real Chrome for Android browser chrome,
a physical Android keyboard, or a physical-touch toolbar-collapse test.
