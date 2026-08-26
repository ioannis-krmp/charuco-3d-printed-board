# Project History: Charuco 3D Printed Board (Full Process Log)

This document records the full process we followed, including what worked, what failed, and the final successful workflow for both STL and STEP outputs.

## Goal

Create a **3D-printable CharUco board** and make it usable for:
1. **Multi-color 3D printing** (white board + black markers)
2. **CAD editing/design work** (proper STEP solids)
3. **OpenCV calibration** (correct YAML parameters)

Target board:
- 14 x 10 squares
- 20 mm square size
- 15 mm marker size
- `DICT_5X5_100`
- Total size: 280 x 200 mm
- Thickness: 2.5 mm

---

## Phase 1 — Initial generation and geometry pipeline

### What we did first
- Generated board image from OpenCV CharUco setup (`gen_png.py`).
- Saved:
  - `charuco.png`
  - `meta.txt` (image width/height and pixels-per-mm)

### Approach used
- Convert PNG pixels into 3D solids using FreeCAD:
  - Identify black regions
  - Build run-length row boxes (`Part.makeBox`)
  - Fuse them into one black solid (`multiFuse`)
  - Create white base by subtraction:
    - `white = full_slab - black`

### Why this was chosen
This creates **complementary solids** (interlocking geometry), which is ideal for 2-color slicing and clean CAD export.

---

## Phase 2 — Printing geometry validation (STL)

### First STL attempt issues
We hit slicing conflicts at first (common in dual-color workflows):
- object overlap warnings
- first-layer collisions
- occasional wrong color assignment / ambiguity in slicer

### What fixed it
Using **complementary bodies** fixed all geometry conflicts:
- Black = actual marker/pattern volume
- White = slab with black volume removed

This means:
- No overlap
- No layer-0 ambiguity
- Cleaner assignment in slicer

### STL outcome
✅ `charuco_white.stl` and `charuco_black.stl` exported correctly
✅ Multi-color slicing works when print sequence is set to **By layer**
✅ Physical print dimensions match expected board footprint

---

## Phase 3 — "Proper STEP" for CAD design work

### Requirement
You asked for a **proper STEP** file suitable for CAD editing, not just rough mesh-like output.

### What we did
- Kept BREP solid workflow in FreeCAD
- Added face cleanup:
  - `removeSplitter()` on black and white shapes
- Exported:
  - `charuco_white.step`
  - `charuco_black.step`
  - `charuco_board.step` (both solids)
  - `charuco_board_step.FCStd`

### Why this matters
`removeSplitter()` merges coplanar split faces and improves editability in CAD systems.

### STEP outcome
✅ Correct dimensions confirmed
✅ Solids valid and loadable in viewers/CAD
✅ Suitable for design operations

---

## Phase 4 — Color visualization request

You asked to include colors for better visualization.

## Attempt 1: FreeCAD headless (`freecadcmd`) with object colors
- Tried setting:
  - `ViewObject.ShapeColor`
  - and exporting colored STEP
- Result: no visible color in STEP output

**Problem:** In headless console mode, color metadata handling is limited/inconsistent.

## Attempt 2: `ImportGui` in console script
- Switched to `ImportGui.export()` + `DiffuseColor`
- Result: failed with:
  - `Cannot load Gui module in console application.`

**Problem:** Your FreeCAD installation cannot load Gui module in console mode (`freecadcmd`, `freecad --console`, `freecad -c` all same limitation).

## Attempt 3: External OCC path (`pythonocc-core`)
- Tried installing with `uv add pythonocc-core`
- Result: dependency resolution failed

**Problem:** `pythonocc-core` packaging availability constraints (not straightforward via uv/pip in your environment).

## Attempt 4 (successful): CadQuery color export
- Used CadQuery assembly workflow:
  - import white STEP
  - import black STEP
  - assign colors to each part
  - export colored assets

### Result
✅ Export succeeded
✅ `charuco_board_colored.step` produced
✅ `charuco_board_colored.glb` produced
✅ `.glb` showed colors correctly in web viewer

---

## Phase 5 — Viewer confusion and final clarification

### What looked wrong
You could not see colors in `3dviewer.net` for STEP.

### Root cause
Many web STEP viewers (including 3dviewer.net in this case) do not reliably display STEP/XDE colors.

### Verification
- GLB displayed colors correctly
- Therefore color assignment/export workflow is valid
- Issue was viewer capability, not model correctness

---

## Final status (everything working)

## Geometry / CAD
✅ Proper STEP solids created
✅ Clean dimensions and thickness
✅ Editable FreeCAD files saved (`.FCStd`)

## Printing
✅ White/black STLs are correct and slicer-compatible
✅ Multi-material print workflow validated

## Visualization
✅ Colored GLB works in web viewer
✅ Colored STEP generated (viewer support may vary)

## Calibration
✅ YAML values aligned with board specification

```yaml
dict_type: DICT_5X5_100
reference_frame: charuco_board
squares_x: 14
squares_y: 10
square_size: 0.020
marker_size: 0.015
```

---

## Lessons learned / what to avoid next time

1. **Avoid overlapping dual-color solids**
   Always build complementary geometry (`white = slab - black`).

2. **Expect FreeCAD booleans to be slow on pixel-derived models**
   Large `multiFuse` is normal; patience required.

3. **Use `removeSplitter()` for CAD-friendly STEP output**
   Improves face cleanliness and editability.

4. **Do not rely on web STEP viewers for color validation**
   Use CAD tools or export GLB for web visualization.

5. **Headless FreeCAD cannot always export colored STEP**
   If GUI modules are unavailable, use CadQuery/OCP route.

6. **Script pasting can truncate files**
   Unterminated string and similar errors were caused by partial paste; always verify full file saved.

---

## Final produced files (core)

- `charuco.png`
- `meta.txt`
- `charuco_white.stl`
- `charuco_black.stl`
- `charuco_white.step`
- `charuco_black.step`
- `charuco_board.step`
- `charuco_board_colored.step`
- `charuco_board_colored.glb`
- `charuco_board_step.FCStd`
- `charuco_board_colored.FCStd`
- scripts: `gen_png.py`, `build_step.py`, `build_stl.py`, `build_step_colored.py`, `colorize_step_cq.py`, `export_glb.py`

Project completed successfully.
