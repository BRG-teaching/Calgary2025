#! python3
# venv: brg-csd
# r: compas_rv

import pathlib
from compas.scene import Scene
from compas.colors import Color
from compas import json_load

filepath = pathlib.Path(__file__).parent.parent / "data" / "mesh_attributes2.json"
mesh = json_load(filepath)

scene = Scene()
scene.clear_context()
scene.add(mesh)

# Iterate over the vertices
for vertex_key in mesh.vertices():

    # Get the sphere
    sphere = mesh.vertex_attribute(vertex_key, "sphere")

    # If the sphere is not None, add it to the scene
    if sphere is not None:
        scene.add(sphere, color=Color.blue())

# Draw the scene
scene.draw()
