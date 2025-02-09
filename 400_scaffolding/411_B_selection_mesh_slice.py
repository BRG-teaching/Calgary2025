#! python3
# venv: brg-csd

import compas_rhino
from compas.geometry import Polygon

guid = compas_rhino.objects.select_mesh()
mesh = compas_rhino.conversions.meshobject_to_compas(guid)
print(mesh)

guid = compas_rhino.objects.select_object()
obj = compas_rhino.objects.find_object(guid)
polyline = compas_rhino.conversions.curve_to_compas_polyline(obj.Geometry)
polygon = Polygon(polyline.points[:-1])
plane = polygon.plane
print(plane)

