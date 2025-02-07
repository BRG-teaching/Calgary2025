#! python3
# venv: brg-csd
# r: compas_model

import pathlib

import compas
from compas.datastructures import Mesh
from compas.scene import Scene
from compas import json_dump

# =============================================================================
# Load data
# =============================================================================

IFILE = pathlib.Path(__file__).parent.parent / "data" / "002_mesh.json"
trimesh = compas.json_load(IFILE)

# =============================================================================
# Dual
#
# - construct a dual
# - update default attributes
# - flip the cycles because a dual has opposite cycles compared to the original
# =============================================================================

dual: Mesh = trimesh.dual(include_boundary=True)

dual.update_default_edge_attributes(is_support=False)
dual.update_default_face_attributes(number=None, batch=None)
dual.update_default_vertex_attributes(thickness=0, is_corner=False, is_support=False)

dual.flip_cycles()


# =============================================================================
# Serialize
# =============================================================================

json_dump(dual, pathlib.Path(__file__).parent.parent / "data" / "003_mesh.json")

# =============================================================================
# Visualisation
# =============================================================================

scene = Scene()
scene.clear_context()
scene.add(dual, show_vertices=True)
scene.draw()
