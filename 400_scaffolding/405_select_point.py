#! python3
# venv: brg-csd

import compas_rhino

guid = compas_rhino.objects.select_object()
point = compas_rhino.conversions.pointobject_to_compas(guid)
print(point)
