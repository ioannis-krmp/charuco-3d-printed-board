import cv2
import numpy as np

# ---------- parameters ----------
SQUARES_X, SQUARES_Y = 14, 10
SQUARE_LEN_MM = 20.0
MARKER_LEN_MM = 15.0
PIXELS_PER_MM = 4
DICT = cv2.aruco.DICT_5X5_100
# -------------------------------

print("A: build board")
d = cv2.aruco.getPredefinedDictionary(DICT)
try:
    board = cv2.aruco.CharucoBoard((SQUARES_X, SQUARES_Y), SQUARE_LEN_MM, MARKER_LEN_MM, d)
except Exception:
    board = cv2.aruco.CharucoBoard_create(SQUARES_X, SQUARES_Y, SQUARE_LEN_MM, MARKER_LEN_MM, d)

w = int(round(SQUARES_X * SQUARE_LEN_MM * PIXELS_PER_MM))
h = int(round(SQUARES_Y * SQUARE_LEN_MM * PIXELS_PER_MM))

try:
    img = board.generateImage((w, h), marginSize=0, borderBits=1)
except Exception:
    img = board.draw((w, h), marginSize=0, borderBits=1)

# ensure single-channel grayscale
if img.ndim == 3:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imwrite("charuco.png", img)

with open("meta.txt", "w") as f:
    f.write(f"{w}\n{h}\n{PIXELS_PER_MM}\n")

print("B: saved charuco.png", w, h)
print("C: saved meta.txt")