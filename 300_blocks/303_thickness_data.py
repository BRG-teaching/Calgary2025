#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas import json_load
from compas.scene import Scene
from compas.colors import Color
from compas.geometry import Sphere
from scipy.interpolate import griddata
from compas import json_dump

IFILE = pathlib.Path(__file__).parent.parent / "data" / "302_dual.json"

dual: Mesh = json_load(IFILE)

scene = Scene()
scene.clear_context()

points = []
values = []

for vertex in dual.vertices():
    if dual.vertex_attribute(vertex, "is_support"):
        point = dual.vertex_attributes(vertex, "xy")
        points.append(point)
        values.append(30.0)


vertices_by_height = sorted(dual.vertices(), key=lambda v: dual.vertex_attribute(v, "z"))

for vertex in vertices_by_height[-5:]:
    points.append(dual.vertex_attributes(vertex, "xy"))
    values.append(10.0)


samples = dual.vertices_attributes("xy")
thickness = griddata(points, values, samples)

for vertex, t in zip(dual.vertices(), thickness):
    dual.vertex_attribute(vertex, "thickness", t)

    color = Color.from_i((t-10)/20)
    scene.add(Sphere(t, point=dual.vertex_point(vertex)),  color=color)

scene.add(dual)
scene.draw()

OFILE = pathlib.Path(__file__).parent.parent / "data" / "303_dual.json"
json_dump(dual, OFILE)

