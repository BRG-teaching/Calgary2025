#! python3
# venv: brg-csd

import compas_rhino
from compas.scene import Scene
from compas.geometry import Translation

guid = compas_rhino.objects.select_mesh()
mesh = compas_rhino.conversions.meshobject_to_compas(guid)
print(mesh)

# Copy mesh, transform it and add to scene.