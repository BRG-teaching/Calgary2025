#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas.geometry import Plane
from compas.geometry import Polygon
from compas import json_load
from compas.scene import Scene
from compas import json_dump


IFILE = pathlib.Path(__file__).parent.parent / "data" / "303_dual.json"

dual: Mesh = json_load(IFILE)

scene = Scene()
scene.clear_context()

for face_key in dual.faces():
    top_points = []
    flat_top_points = []
    bottom_points = []
    for vertex in dual.face_vertices(face_key):
        normal = dual.vertex_normal(vertex)
        thickness = dual.vertex_attribute(vertex, "thickness")
        point_in = dual.vertex_point(vertex) - normal * thickness / 2
        point_out = dual.vertex_point(vertex) + normal * thickness / 2

        top_points.append(point_out)
        bottom_points.append(point_in)

    plane = Plane.from_points(top_points)
    for point in top_points:
        projected_point = plane.projected_point(point, normal)
        flat_top_points.append(projected_point)

    top_polygon = Polygon(flat_top_points)
    bottom_polygon = Polygon(bottom_points)

    side_polygons = []
    for (a, b), (aa, bb) in zip(zip(bottom_polygon, bottom_polygon[1:] + bottom_polygon[:1]), zip(top_polygon, top_polygon[1:] + top_polygon[:1])):
        side_polygons.append(Polygon([a, b, bb, aa]))

    bottom_polygon = Polygon(bottom_polygon[::-1])

    block = Mesh.from_polygons([top_polygon] + [bottom_polygon] + side_polygons)
    block.face_attribute(0, "is_top", True)
    block.face_attribute(1, "is_bottom", True)
    block.name = f"Block {face_key}"

    dual.face_attribute(face_key, "block", block)
    scene.add(block)

scene.draw()

OFILE = pathlib.Path(__file__).parent.parent / "data" / "304_dual.json"
json_dump(dual, OFILE)
