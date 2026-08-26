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

## Setup (Ubuntu 24.04)

This project uses two separate Python runtimes:

- **`uv`-managed venv** — for `gen_png.py` (OpenCV) and the CadQuery scripts (`colorize_step_cq.py`, `export_glb.py`). Run these with `uv run python <script>.py`.
- **FreeCAD's own bundled Python** — for `build_step.py`, `build_stl.py`, `build_step_colored.py`, since they `import FreeCAD, Part, Mesh` (and `ImportGui`), which are not pip-installable and only exist inside FreeCAD itself. Run these with `freecadcmd <script>.py`, **not** `uv run`.

### 1) Install system dependencies

```bash
# git, if not already installed
sudo apt update
sudo apt install -y git

# FreeCAD 0.21 (provides the `freecadcmd` binary used below)
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo apt update
sudo apt install -y freecad
```

> The Ubuntu 24.04 `universe` repo also ships a `freecad` package, but the PPA above is what this project was built and tested against (`FreeCAD 0.21.2`). If you already have a working FreeCAD 0.21.x install (`freecadcmd --version`), you can skip the PPA.

Install `uv` (manages the Python venv + dependencies, no system Python packages needed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# then restart your shell, or: source $HOME/.local/bin/env
```

`uv` will automatically download and use Python 3.11 (pinned in `.python-version`) — you don't need to install Python yourself.

### 2) Clone and install project dependencies

```bash
git clone git@github.com:ioannis-krmp/charuco-3d-printed-board.git
cd charuco-3d-printed-board
uv sync
```

`uv sync` creates `.venv/` and installs everything from `pyproject.toml`/`uv.lock`: `opencv-contrib-python`, `cadquery`, `manifold3d`, `numpy`, `trimesh`.

### 3) Verify the install

```bash
# venv deps
uv run python -c "import cv2, cadquery; print('cv2', cv2.__version__, '| cadquery', cadquery.__version__)"

# FreeCAD
freecadcmd --version
freecadcmd -c "import FreeCAD, Part, Mesh; print('FreeCAD OK', FreeCAD.Version()[0]+'.'+FreeCAD.Version()[1])"
```

If both commands print versions without errors, you're ready to run the pipeline below.

---

## Repository Structure

Suggested layout:

```text
.
├── gen_png.py
├── build_step.py
├── build_stl.py
├── build_step_colored.py
├── colorize_step_cq.py
├── export_glb.py
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
├── pyproject.toml
├── uv.lock
├── PROJECT_HISTORY.md
└── README.md
```

> You can also place outputs in `out/` if you prefer.
>
> `pyproject.toml`/`uv.lock` pin the `uv`-managed dependencies (see [Setup](#setup-ubuntu-2404)); `PROJECT_HISTORY.md` is a narrative log of what was tried, what failed, and why — read it if you hit one of the FreeCAD/color issues below and want the backstory.

---

## Quick Start (A)

Run these from the repo root, in this order. Board parameters (`SQUARES_X`, `SQUARE_LEN_MM`, `THICK_MM`, dictionary, etc.) are hardcoded near the top of each script — edit them there if you want a different board than the [current spec](#board-spec-current-project); just keep the values consistent across all scripts and the calibration YAML.

## 1) Generate board PNG + metadata

```bash
uv run python gen_png.py
```

Reads the parameters at the top of `gen_png.py` (14×10 squares, 20mm, `DICT_5X5_100`, 4 px/mm) and produces:
- `charuco.png` — the flat board image (1120×800 px for the current spec)
- `meta.txt` — 3 lines: pixel width, pixel height, pixels-per-mm (consumed by the FreeCAD scripts below)

## 2) Build CAD-editable STEP solids

```bash
freecadcmd build_step.py
```

Converts `charuco.png` into two complementary BREP solids (`white = full_slab - black`), cleans faces with `removeSplitter()`, and exports:
- `charuco_white.step`, `charuco_black.step` — individual solids
- `charuco_board.step` — both solids in one STEP assembly
- `charuco_board_step.FCStd` — editable FreeCAD document

**This is slow** — it's building thousands of per-pixel-run boxes and fusing them with `multiFuse`. Expect several minutes for a 14×10 board; it prints `row N/H` progress and `A:`…`J:` stage markers, so it's working even when it looks stuck. Let it finish.

## 3) Build STLs for 2-color printing

```bash
freecadcmd build_stl.py
```

Same complementary-solid geometry as step 2, but meshed and exported as STL, plus its own `.FCStd`:
- `charuco_white.stl`, `charuco_black.stl`
- `charuco_board.FCStd`

Also slow for the same reason as step 2 — this rebuilds the geometry from scratch rather than reusing the STEP output.

In your slicer:
- Load both STLs
- Keep same origin/alignment (they were exported from the same coordinate system, don't re-center either one)
- Assign White filament to `charuco_white.stl`, Black filament to `charuco_black.stl`
- Use **Print sequence: By layer**

## 4) Colored visualization exports (STEP + GLB)

STEP color via FreeCAD's console (`ImportGui`) doesn't work on a headless/console build — see [Troubleshooting #3](#3-importgui--color-export-fails-in-console). The working path is CadQuery, run through `uv`, using the STEP solids from step 2:

```bash
uv run python colorize_step_cq.py   # -> charuco_board_colored.step
uv run python export_glb.py         # -> charuco_board_colored.glb
```

`.glb` is the reliable one for checking color in a browser/web viewer — see [Troubleshooting #4](#4-step-shows-no-color-in-online-viewer) for why the colored STEP may still look gray in some viewers.

Optional — `freecadcmd build_step_colored.py` also exists and will get as far as saving a colored `charuco_board_colored.FCStd`, but is **expected to fail** on its final `ImportGui.export()` call with `Cannot load Gui module in console application`; that's a known FreeCAD console limitation, not a bug in the script (see [Troubleshooting #3](#3-importgui--color-export-fails-in-console) and `PROJECT_HISTORY.md`). Use it only if you want the colored `.FCStd`; use `colorize_step_cq.py` for the colored STEP itself.

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

Keep `squares_x`/`squares_y`/`square_size`/`marker_size`/`dict_type` here in sync with whatever you set at the top of `gen_png.py` (note the unit difference: mm in the script, meters in the YAML).

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
