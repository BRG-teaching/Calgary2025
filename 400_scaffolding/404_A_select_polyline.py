#! python3
# venv: brg-csd

import compas_rhino

guid = compas_rhino.objects.select_object()
obj = compas_rhino.objects.find_object(guid)

# Convert obj to compas polyline, obj (RhinoObject) has attribute Geometry.
