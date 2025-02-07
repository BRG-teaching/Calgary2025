#! python3
# venv: brg-csd

import pathlib

import compas
from compas.datastructures import Mesh
from compas.itertools import pairwise
from compas.scene import Scene
from compas import json_dump


def break_boundary(mesh: Mesh, breakpoints: list[int]) -> tuple[list[list[int]], list[int]]:
    boundary: list[int] = mesh.vertices_on_boundaries()[0]
    if boundary[0] == boundary[-1]:
        del boundary[-1]

    breakpoints = sorted(breakpoints, key=lambda s: boundary.index(s))

    start = boundary.index(breakpoints[0])
    boundary = boundary[start:] + boundary[:start]

    borders = []
    for a, b in pairwise(breakpoints):
        start = boundary.index(a)
        end = boundary.index(b)
        borders.append(boundary[start : end + 1])
    borders.append(boundary[end:] + boundary[:1])

    return borders, breakpoints


# =============================================================================
# Load data
# =============================================================================


IFILE = pathlib.Path(__file__).parent.parent / "data" / "006_mesh.json"
dual = compas.json_load(IFILE)

# =============================================================================
# Dual: Edge collapse
# =============================================================================

tocollapse = []

for u, v in dual.edges_on_boundary():
    if dual.vertex_attribute(u, "is_corner") or dual.vertex_attribute(v, "is_corner"):
        continue
    face = dual.halfedge_face((v, u))
    vertices = dual.face_vertices(face)
    if len(vertices) == 4:
        vv = dual.face_vertex_ancestor(face, v)
        uu = dual.face_vertex_descendant(face, u)
        tocollapse.append((u, v))
        tocollapse.append((uu, vv))

for u, v in tocollapse:
    dual.collapse_edge((u, v), allow_boundary=True)

# =============================================================================
# Serialize
# =============================================================================

json_dump(dual, pathlib.Path(__file__).parent.parent / "data" / "007_mesh.json")

# =============================================================================
# Visualisation
# =============================================================================

scene = Scene()
scene.clear_context()
scene.add(dual)
scene.draw()
