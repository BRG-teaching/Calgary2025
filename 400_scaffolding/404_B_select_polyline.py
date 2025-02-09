#! python3
# venv: brg-csd

import compas_rhino

guid = compas_rhino.objects.select_object()
obj = compas_rhino.objects.find_object(guid)
polyline = compas_rhino.conversions.curve_to_compas_polyline(obj.Geometry)
print(polyline)
