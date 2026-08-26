import os, FreeCAD as App, Mesh

base = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(os.path.join(base, "charuco_board.FCStd"))

ow = doc.getObject("White")
ob = doc.getObject("Black")

out = os.path.join(base, "charuco_board.3mf")
Mesh.export([ow, ob], out)   # both objects into one 3MF
print("saved", out, os.path.exists(out))