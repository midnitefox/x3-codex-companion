# Create your own interface

The live bridge runs `display_ui.render_status(data)` and expects a Pillow image in mode `1`, exactly **528 x 792**. `bridge.pack` rotates it into the device's native 792 x 528 framebuffer. Do not rotate the renderer itself.

- `scripts/build_assets.py`: vector geometry, static labels, font outlines, status marks and template layout.
- `scripts/render_assets.cjs`: turns SVG templates into PNG files using Sharp.
- `assets/`: eight checked-in SVG/PNG backgrounds. Task-name banners and numeric values are blank in these templates.
- `display_ui.py`: live task selection, two-line title, counter values, and rendering.
- `generate_screens.py`: creates matching firmware boot/offline headers. Changes require a firmware rebuild/reflash **only for those fallback screens**; a normal live UI change requires a bridge restart.

Task selection and count semantics should remain independent of the visual design. A disconnected feed must never display fabricated activity. Keep missing counts as dashes. The selected category uses a black counter tile; other categories remain white.

## Prompt for Codex or another coding assistant

Copy this into a coding assistant with this repository open. Replace the bracketed style brief.

```text
Customize the interface of this X3 Codex Companion repository.

My style brief: [describe the look, attach visual references, and specify any symbols or typography you want].

First inspect README.md, docs/ARCHITECTURE.md, display_ui.py,
scripts/build_assets.py, scripts/render_assets.cjs, and the existing assets.
Keep the current working USB protocol and Codex status integration intact.

Produce real SVG vectors and a pixel-accurate 528 x 792 portrait preview.
Do not use a generated image as production UI code. Use image references
only as visual guidance. Preserve the physical 2:3 screen aspect ratio.

Design all eight states: Working, Needs input, Ready, Idle, Failed,
Waiting, Offline, and Unknown. Give each a recognizable static symbol.
Show the selected task's actual name and RUN / INPUT / READY counts.
Do not add a redundant application title. Keep connection indication small.
Use black and white, large bold type, and generous gaps so symbols,
frames, text, and side decoration cannot overlap. Target readability from
about three feet away. Do not shrink long task titles to unreadable sizes;
wrap to two lines and truncate with an ellipsis. Test long words, Unicode,
empty titles, and 0/1/multiple task counts.

The renderer must return a 528 x 792 Pillow mode-1 image. Retain the
existing task-priority and freshness behavior. Unknown totals must be
shown as dashes, not zero. No fake percentage progress, invented task
activity, continuous animation, network service, or model API calls.

Use fonts installed locally or openly licensed fonts with their notices.
Do not redistribute proprietary font files. If replacing the Codex outline,
use original artwork and keep the symbol family geometrically consistent.

Create a comparison sheet of all eight states using synthetic task names.
Use these previews to check proportions, clipping, text wrapping, counters,
and a small USB indicator. Run the existing tests plus meaningful tests
for changed layout/data handling. Document files changed and limitations.

Implement the design in the repository and regenerate assets. Do not
flash a device or replace a running user's design until I approve the
preview. If approved, back up the current renderer/assets, restart the
bridge, confirm a USB frame acknowledgement, and ask me to check the
physical screen. For matching boot/offline screens, regenerate the C++
headers and build firmware, then follow docs/FIRMWARE.md before flashing.
```

## Regenerate assets

From the repository root, with development dependencies installed:

```powershell
.\.venv\Scripts\python.exe scripts/build_assets.py
node scripts/render_assets.cjs
.\.venv\Scripts\python.exe scripts/make_preview.py
.\.venv\Scripts\python.exe generate_screens.py
```

`docs/status-preview.png` uses clearly synthetic tasks and counts. Inspect it before restarting a bridge. Disable the lifecycle watcher before maintenance if needed; otherwise it will restart a stopped bridge. Enable it again after validation. No secrets or real conversation text should be added to examples.
