#! python3
# venv: brg-csd

import compas_rhino
from compas.geometry import Polygon
from compas.geometry.triangulation_earclip import earclip_polygon
from compas.datastructures import Mesh
from compas.scene import Scene

#####################################################################
# Select two polygons
#####################################################################

guid = compas_rhino.objects.select_object()
obj = compas_rhino.objects.find_object(guid)
polyline = compas_rhino.conversions.curve_to_compas_polyline(obj.Geometry)
polygon = Polygon(polyline.points[:-1])

guid = compas_rhino.objects.select_object()
obj = compas_rhino.objects.find_object(guid)
polyline = compas_rhino.conversions.curve_to_compas_polyline(obj.Geometry)
cutter = Polygon(polyline.points[:-1])

#####################################################################
# Boolean Difference
#####################################################################
polygon = polygon.boolean_difference(cutter)

#####################################################################
# Triangulate Polygon
#####################################################################
faces = earclip_polygon(polygon)
mesh = Mesh.from_vertices_and_faces(polygon.points, faces)

#####################################################################
# Scene
#####################################################################
scene = Scene()
scene.add(mesh)
scene.draw()
