# Charuco 3D Printed Board

3D-printable CharUco board workflow with:
- PNG board generation (OpenCV ArUco/CharUco)
- CAD solid generation (FreeCAD)
- STEP export for design editing
- 2-color STL workflow for multi-material printing
- Calibration YAML for OpenCV pose estimation

## Board Spec (current project)

- Board squares: **14 x 10** (`squares_x=14`, `squares_y=10`)
- Square size: **20.0 mm**
- Marker size: **15.0 mm**
- Dictionary: **`DICT_5X5_100`**
- Physical size: **280 x 200 mm**
- Thickness: **2.5 mm**

---

## Repository Structure

Suggested layout:

```text
.
├── gen_png.py
├── build_step.py
├── build_step_colored.py
├── colorize_step_cq.py
├── charuco_board.yaml
├── meta.txt
├── charuco.png
├── charuco_white.step
├── charuco_black.step
├── charuco_board.step
├── charuco_board_colored.step
├── charuco_board_colored.glb
├── charuco_board_step.FCStd
├── charuco_white.stl
├── charuco_black.stl
└── README.md
```

> You can also place outputs in `out/` if you prefer.

---

## Quick Start (A)

## 1) Generate board PNG + metadata

Run `gen_png.py` (project-specific script) to produce:
- `charuco.png`
- `meta.txt` (width, height, pixels/mm)

## 2) Build solids + STEP from PNG

Run FreeCAD script:

```bash
freecadcmd build_step.py
```

Outputs:
- `charuco_white.step`
- `charuco_black.step`
- `charuco_board.step` (both solids)
- `charuco_board_step.FCStd`

## 3) Export/prepare STLs for 2-color printing

Use FreeCAD or your script pipeline to export:
- `charuco_white.stl`
- `charuco_black.stl`

In slicer:
- Load both STLs
- Keep same origin/alignment
- Assign White filament to white body, Black filament to black body
- Use **Print sequence: By layer**

## 4) Optional: colored visualization export

If STEP color is not visible in your viewer:
- Use `colorize_step_cq.py` (CadQuery) to create:
  - `charuco_board_colored.step`
  - `charuco_board_colored.glb`

`*.glb` is best for web viewers.

## 5) Calibration YAML

Use:

```yaml
dict_type: DICT_5X5_100
reference_frame: charuco_board
squares_x: 14
squares_y: 10
square_size: 0.020
marker_size: 0.015
```

---

## Printing Notes

- Recommended for AMS/MMU-style color swap:
  - White base + black pattern as separate solids
  - **By layer** printing
- Add brim for flatness on large plates
- Keep bed well-leveled; this is a metrology target
- Measure printed square size with calipers and, if needed, update YAML dimensions for precise calibration scale

---

## Troubleshooting (B)

## 1) First-layer geometry conflicts (slicer errors)

**Symptom:** "Some objects are too close", "virtual bed out of bounds", or bad 2-color merge.

**Cause:** Overlapping full slabs or duplicate bottoms.

**Fix:** Use complementary solids:
- `white = full_slab - black`
- `black = pattern`
No overlap, perfect interlock.

---

## 2) FreeCAD script is very slow

**Symptom:** `multiFuse` appears stuck for minutes.

**Cause:** Thousands of pixel-run boxes.

**Fixes:**
- Let it finish (expected for large boards)
- Keep `removeSplitter()` to clean faces
- Consider faster geometry strategy (face/contour extrusions) for large designs

---

## 3) `ImportGui` / color export fails in console

**Symptom:** `Cannot load Gui module in console application.`

**Cause:** Your FreeCAD console build cannot load GUI module in headless mode.

**Fix:**
- Use CadQuery/OCP route for colorized export, or
- Do color assignment + STEP export from FreeCAD GUI.

---

## 4) STEP shows no color in online viewer

**Symptom:** STEP appears gray in https://3dviewer.net

**Cause:** Viewer limitation (many web viewers ignore STEP XDE color styling).

**Fix:**
- Verify in CAD tools (FreeCAD/Fusion/etc.)
- Use `.glb` for browser color preview

---

## 5) Charuco pose/calibration seems wrong

**Common causes:**
- `squares_x`/`squares_y` swapped
- Wrong dictionary
- Nominal vs actual printed square size mismatch

**Fix checklist:**
- Confirm `squares_x=14`, `squares_y=10`
- Confirm `DICT_5X5_100`
- Measure printed square with calipers and update YAML (meters)

---

## 6) Python script errors like "unterminated string literal"

**Cause:** Truncated paste/edit of script file.

**Fix:** Re-copy full script and verify file end before running.

---

## Versioned Parameters (Current)

- `squares_x = 14`
- `squares_y = 10`
- `square_size = 0.020` (m)
- `marker_size = 0.015` (m)
- `dict_type = DICT_5X5_100`
- `thickness = 2.5` (mm)

---

## License

If you want this reusable, add a license file (MIT/BSD recommended).
