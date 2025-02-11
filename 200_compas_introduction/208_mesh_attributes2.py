#! python3
# venv: brg-csd
# r: compas_rv

import pathlib
from compas.scene import Scene
from compas.geometry import Sphere
from compas.colors import Color
from compas import json_load
from compas import json_dump

filepath = pathlib.Path(__file__).parent.parent / "data" / "mesh_attributes1.json"
mesh = json_load(filepath)

scene = Scene()
scene.clear_context()
scene.add(mesh)

for vertex_key in mesh.vertices():

    curvature = mesh.vertex_attribute(vertex_key, "curvature")
    if curvature is not None:
        point = mesh.vertex_point(vertex_key)
        sphere = Sphere(abs(curvature) * 2, point=point)
        scene.add(sphere, color=Color.red())

        mesh.vertex_attribute(vertex_key, "sphere", sphere)

# Draw the scene
scene.draw()


filepath = pathlib.Path(__file__).parent.parent / "data" / "mesh_attributes2.json"
json_dump(mesh, filepath)