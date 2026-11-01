# Desktop, phone and headset input

Every app is fully playable on a normal phone screen. XR is an additional presentation, never the phone-control fallback. Responsive means the size of the **app window**, not a user-agent string.

## Layout target

Use a compact title/action row with Play/Pause, settings and document actions; a game viewport; and only the controls that current play needs. Narrow widths may move controls to a bottom strip or sheet. The desktop still owns its title bar and window layout. Do not create a second desktop chrome inside the app.

Design targets: 44 CSS-pixel touch targets where practical, safe-area inset support, readable type, no hover-only commands, no required orientation lock. A portrait board can letterbox while its actions remain reachable. Controls must not cover the current player, ball, board selection or critical score. Use actual canvas client coordinates and ResizeObserver; don't use screen coordinates as simulation coordinates.

## Commands, not device-specific game rules

A pointer, key, touch button or XR action becomes the same validated intent. Preserve press/held/release semantics where needed. Every touch gesture tracks its pointer id; two thumbs cannot steal one another's controls. Capture only while dragging; release on pointerup/cancel/blur, load, restart and XR transition. Keyboard repeat should not create extra drop/shoot transactions.

Use keyboard focus scoped to the returned root. Do not globally capture arrows/space from the terminal, editor or another game. Ignore game shortcuts inside text fields, sliders and file dialogs. Do not register global Phaser keys and assume the desktop will filter them for you.

Scrolling/touch-action restrictions belong only to the active gameplay surface and its controls. Menus/settings/document lists remain scrollable. Browser pinch/zoom and system navigation should not be disabled site-wide. Pointer lock/fullscreen may be optional desktop enhancements, never prerequisites for phone play.

## Accessibility and comfort

All menus have semantic labels and keyboard focus. Provide high-contrast cues, reduced motion, volume/mute and non-color-only feedback. Audio begins through user activation. Rive artwork is paired with semantic state/controls when it carries interaction; avoid duplicate focusable controls that cause the same action twice.

For XR: seated play, ray interaction and a clear Exit path are baseline. Hands and controllers add convenience but never become the only way to complete a menu. No forced head transforms, camera roll or unbounded grab impulses. Audio cues need captions/visual equivalents where they carry rules.

## Test matrix

Test at least a narrow desktop window, wide window, phone portrait, phone landscape, two touch pointers, touchcancel, keyboard-only menus and browser background/restore. Then test a physical Android phone, not only responsive emulation. The three-dimensional branch additionally needs the actual Galaxy XR browser. Record exact device/browser/build; support is evidence, not a guessed version number.
