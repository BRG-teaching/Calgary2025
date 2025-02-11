#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas import json_load
from compas.scene import Scene
from compas import json_dump
from compas.colors import Color

IFILE = pathlib.Path(__file__).parent.parent / "data" / "301_mesh.json"

mesh: Mesh = json_load(IFILE)
mesh.quads_to_triangles()


dual: Mesh = mesh.dual(include_boundary=True)
dual.flip_cycles()

supports = [mesh.vertex_point(vertex) for vertex in mesh.vertices_where(is_support=True)]

scene = Scene()
scene.clear_context()

to_delete = []

for vertex in dual.vertices():
    dual_point = dual.vertex_point(vertex)
    if dual_point in supports:
        dual.vertex_attribute(vertex, "is_support", True)
        scene.add(dual.vertex_point(vertex), color=Color.red())
    elif dual.is_vertex_on_boundary(vertex):
        dual.vertex_attribute(vertex, "is_boundary", True)
        if dual.vertex_degree(vertex) == 2:
            scene.add(dual.vertex_point(vertex), color=Color.green())
            to_delete.append(vertex)
        else:
            scene.add(dual.vertex_point(vertex), color=Color.blue())

for vertex in to_delete:
    nbrs = dual.vertex_neighbors(vertex)
    dual.collapse_edge((vertex, nbrs[0]), allow_boundary=True, t=1.0)


scene.add(dual)
scene.draw()

OFILE = pathlib.Path(__file__).parent.parent / "data" / "302_dual.json"
json_dump(dual, OFILE)

