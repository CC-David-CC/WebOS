# Live app fix queue

| App | Impact and reproduction | Status and retest |
|---|---|---|
| SoundCraft | Arm a track in a new session with no available audio input, then press Record. The deployed engine can panic and delay closing the window. | Local fix passed the reproduction and seven account checks. Retest the hosted recording and close path after promotion. Browser microphone capture remains a separate gap. |
| Weather Maps | The layer panel intercepted the start of the forecast slider at several tablet widths. | Fixed on ksu.codes. Seven touch-emulated widths passed. Physical iPad confirmation is open. |
