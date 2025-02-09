#! python3
# venv: brg-csd

import compas_rhino
from compas.scene import Scene
from compas.geometry import Translation

guid = compas_rhino.objects.select_object()
curve = compas_rhino.conversions.curveobject_to_compas(guid)
print(curve)

# Add code below: 1) copy geometry, transfrom to XY frame and add it to scene.
