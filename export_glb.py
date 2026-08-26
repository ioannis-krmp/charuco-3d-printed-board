import os
import cadquery as cq
from cadquery import Assembly, Color

base = os.path.dirname(os.path.abspath(__file__))
white = cq.importers.importStep(os.path.join(base, "charuco_white.step"))
black = cq.importers.importStep(os.path.join(base, "charuco_black.step"))

asm = Assembly(name="charuco_board")
asm.add(white, name="White", color=Color(0.95, 0.95, 0.95))
asm.add(black, name="Black", color=Color(0.05, 0.05, 0.05))

out = os.path.join(base, "charuco_board_colored.glb")
asm.export(out)   # .glb inferred from extension
print("wrote", out, os.path.exists(out))