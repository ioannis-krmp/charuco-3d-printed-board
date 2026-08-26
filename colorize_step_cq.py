import os
import cadquery as cq
from cadquery import Assembly, Color
from cadquery.occ_impl.exporters.assembly import exportAssembly

base = os.path.dirname(os.path.abspath(__file__))
in_white = os.path.join(base, "charuco_white.step")
in_black = os.path.join(base, "charuco_black.step")
out_step = os.path.join(base, "charuco_board_colored.step")

white = cq.importers.importStep(in_white)
black = cq.importers.importStep(in_black)
print("imported white & black")

asm = Assembly(name="charuco_board")
asm.add(white, name="White", color=Color(0.95, 0.95, 0.95))
asm.add(black, name="Black", color=Color(0.05, 0.05, 0.05))

exportAssembly(asm, out_step, mode="default")
print("wrote", out_step, "exists:", os.path.exists(out_step))
