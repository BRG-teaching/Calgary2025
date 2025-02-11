#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas import json_load
from compas.scene import Scene
from compas import json_dump
from compas.colors import Color

# Define input file path
IFILE = pathlib.Path(__file__).parent.parent / "data" / "301_mesh.json"

# Load mesh and convert quads to triangles
mesh: Mesh = json_load(IFILE)
mesh.quads_to_triangles()

# Create dual mesh and flip cycles
dual: Mesh = mesh.dual(include_boundary=True)
dual.flip_cycles()

# Get support points from original mesh
supports = [mesh.vertex_point(vertex) for vertex in mesh.vertices_where(is_support=True)]

# Create scene for visualization
scene = Scene()
scene.clear_context()

# Initialize list to track vertices to delete
to_delete = []

# Process vertices in dual mesh
for vertex in dual.vertices():
    dual_point = dual.vertex_point(vertex)
    if dual_point in supports:
        # Mark support vertices and color them red
        dual.vertex_attribute(vertex, "is_support", True)
        scene.add(dual.vertex_point(vertex), color=Color.red())
    elif dual.is_vertex_on_boundary(vertex):
        # Process boundary vertices
        dual.vertex_attribute(vertex, "is_boundary", True)
        if dual.vertex_degree(vertex) == 2:
            # Color degree-2 boundary vertices green and mark for deletion
            scene.add(dual.vertex_point(vertex), color=Color.green())
            to_delete.append(vertex)
        else:
            # Color other boundary vertices blue
            scene.add(dual.vertex_point(vertex), color=Color.blue())

# Remove marked vertices by collapsing edges
for vertex in to_delete:
    nbrs = dual.vertex_neighbors(vertex)
    dual.collapse_edge((vertex, nbrs[0]), allow_boundary=True, t=1.0)

# Add dual mesh to scene and display
scene.add(dual)
scene.draw()

# Define output file path and save dual mesh
OFILE = pathlib.Path(__file__).parent.parent / "data" / "302_dual.json"
json_dump(dual, OFILE)
