# Readable guest display and phone keyboard

Open **Programming → Linux X11**. Fit shows the full guest inside the app window. Choose **100%**, **150%** or **200%** to enlarge terminal text. When the screen extends beyond the window, enable **Pan** and swipe. Turn Pan off to select an xterm or Chromium input. Tap **Keyboard** to send text into the selected guest application.

| Hosted check | Result |
|---|---|
| Anonymous phone, 390 × 844 | The 800 × 600 Linux guest fitted to a 336 × 252 view, then enlarged to its actual size. Touch panning scrolled the zoomed workspace. Fit restored the original dimensions. |
| Phone input | A touch selected xterm. The mobile input accepted a complete command in a single text commit followed immediately by Enter. The resulting guest file in WebOS Files contained exactly the guest's loopback hosts record. |
| Signed-in 4K desktop | Linux selected its native 1280 × 800 framebuffer. It fitted to a 3344 × 2090 area inside the maximized WebOS window. Actual size restored native pixels; Fit enlarged it again. A keyboard command copied the guest file into the account workspace. |

Both tests opened System Tools → Files, selected the guest-written file, clicked Download, and checked its exact contents. The tests ran in Chromium on the deployed site.

For the remaining hardware check, open Linux X11 on a physical phone from a cold start and time how long it takes to reach xterm and then Chromium. Switch X11 to 150%, enable Pan and swipe across the desktop. Turn Pan off, tap xterm, tap Keyboard, type `echo hello` and press Enter. In guest Chromium, tap a local page's text field and verify the first letter and remaining text using the on-screen keyboard and a physical keyboard if available. The signed-in owner networking check also remains open. The existing [guest Chromium text and local Files test](chromium-input.md) and [networking evidence](scoped-network.md) cover the earlier software checks.

[Phone at actual size](display-phone-actual.png) · [Phone fitted](display-phone.png) · [4K desktop](display-desktop.png) · [Production receipts](display-release.json) · [X11 source](https://github.com/CC-David-CC/linux-x11/commit/557a102702c26158dde685a26152afd594765713) · [WebOS release](https://github.com/CC-David-CC/WebOS/commit/00567c04cff88e3934bfb84c49cf9b39f1ac2129)

Both source pins were fetched from their published release branches. At verification, WebOS main `3f541eb6e556` had no `apps/linux-x11` gitlink; the hosted deployment uses the release branch.
