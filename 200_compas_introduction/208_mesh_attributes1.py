#! python3
# venv: brg-csd
# r: compas_rv

import pathlib
import compas
from compas.scene import Scene
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.colors import Color
from compas import json_dump

mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

scene = Scene()
scene.clear_context()
scene.add(mesh)

# Get a list of boundary vertices
boundary_vertices = mesh.vertices_on_boundary()

# Iterate over the vertices
for vertex_key in mesh.vertices():

    # If the vertex is a boundary vertex, color it red
    if vertex_key in boundary_vertices:
        point = mesh.vertex_point(vertex_key)
        scene.add(point, color=Color.red())

    # If the vertex is not a boundary vertex, color it green
    else:
        point = mesh.vertex_point(vertex_key)
        scene.add(point, color=Color.green())

        # Get the curvature of the vertex
        vertex_curvature = mesh.vertex_curvature(vertex_key)

        # Get the normal of the vertex
        vertex_normal = mesh.vertex_normal(vertex_key)

        # Scale the normal by the curvature
        vertex_normal.scale(vertex_curvature * 15)

        # Create a line from the point to the normal
        line = Line(point, point + vertex_normal)
        scene.add(line, color=Color.blue())

        # Add the curvature to the vertex attributes
        mesh.vertex_attribute(vertex_key, "curvature", vertex_curvature)

# Dump the vertex attributes to a JSON file
filepath = pathlib.Path(__file__).parent.parent / "data" / "mesh_attributes1.json"
json_dump(mesh, filepath)

# Draw the scene
scene.draw()
