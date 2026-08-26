import os, traceback
import numpy as np
import FreeCAD as App
import Part, Mesh

print("A: start")

# ---------- geometry parameters ----------
THICK_MM = 2.5            # total board thickness (full, for BOTH colors)
BORDER_MM = 0.0
# -----------------------------------------

base = os.path.dirname(os.path.abspath(__file__))
png_path  = os.path.join(base, "charuco.png")
meta_path = os.path.join(base, "meta.txt")
out_fcstd = os.path.join(base, "charuco_board.FCStd")
out_wstl  = os.path.join(base, "charuco_white.stl")
out_bstl  = os.path.join(base, "charuco_black.stl")

def load_png_gray(path):
    import struct, zlib
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Not a PNG"
    pos = 8
    width = height = bitd = colort = None
    idat = b""
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos+4])[0]; pos += 4
        ctype = data[pos:pos+4]; pos += 4
        chunk = data[pos:pos+ln]; pos += ln
        pos += 4
        if ctype == b"IHDR":
            width, height, bitd, colort = struct.unpack(">IIBB", chunk[:10])
        elif ctype == b"IDAT":
            idat += chunk
        elif ctype == b"IEND":
            break
    assert bitd == 8, f"Only 8-bit PNG supported (got {bitd})"
    channels = {0:1, 2:3, 6:4}.get(colort)
    assert channels, f"Unsupported color type {colort}"
    raw = zlib.decompress(idat)
    stride = width * channels
    out = np.zeros((height, width), dtype=np.uint8)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if ft == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i-channels]) & 255
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(stride):
                a = line[i-channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                a = line[i-channels] if i >= channels else 0
                b = prev[i]
                c = prev[i-channels] if i >= channels else 0
                pp = a + b - c
                pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        prev = line
        arr = np.frombuffer(bytes(line), dtype=np.uint8).reshape(width, channels)
        out[y] = arr[:, 0]
    return out

try:
    with open(meta_path) as f:
        w = int(f.readline()); h = int(f.readline()); ppm = float(f.readline())
    print("B: meta", w, h, ppm)

    img = load_png_gray(png_path)
    assert img.shape == (h, w), f"PNG size {img.shape} != meta ({h},{w})"
    print("C: image loaded", img.shape)

    mm_per_px = 1.0 / ppm
    board_w = w * mm_per_px + 2 * BORDER_MM
    board_h = h * mm_per_px + 2 * BORDER_MM

    # Build BLACK pattern as full-thickness boxes (run-length per row)
    black_boxes = []
    for y in range(h):
        if y % 100 == 0:
            print(f"row {y}/{h}")
        row = img[y]
        x = 0
        while x < w:
            if row[x] < 128:
                xs = x
                while x < w and row[x] < 128:
                    x += 1
                dx = (x - xs) * mm_per_px
                dy = mm_per_px
                x_mm = BORDER_MM + xs * mm_per_px
                y_mm = BORDER_MM + (h - 1 - y) * mm_per_px
                b = Part.makeBox(dx, dy, THICK_MM)
                b.translate(App.Vector(x_mm, y_mm, 0))
                black_boxes.append(b)
            else:
                x += 1

    print("D: black boxes", len(black_boxes))
    if not black_boxes:
        raise RuntimeError("No black boxes generated")

    print("E: fuse black (this can take a while)...")
    black_shape = black_boxes[0]
    if len(black_boxes) > 1:
        black_shape = black_shape.multiFuse(black_boxes[1:])
    print("   black fused")

    print("F: white = full slab CUT by black (boolean)")
    full = Part.makeBox(board_w, board_h, THICK_MM)
    white_shape = full.cut(black_shape)
    print("   white cut done")

    print("G: doc")
    doc = App.newDocument("charuco_board")
    ow = doc.addObject("Part::Feature", "White")
    ob = doc.addObject("Part::Feature", "Black")
    ow.Shape = white_shape
    ob.Shape = black_shape
    doc.recompute()

    print("H: save FCStd", out_fcstd)
    doc.saveAs(out_fcstd)

    print("I: export STLs")
    Mesh.export([ow], out_wstl)
    print("W STL exists?", os.path.exists(out_wstl))
    Mesh.export([ob], out_bstl)
    print("B STL exists?", os.path.exists(out_bstl))

    doc.save()
    print("J: done")
    print(out_fcstd)
    print(out_wstl)
    print(out_bstl)

except Exception as e:
    print("ERROR:", e)
    traceback.print_exc()
    raise