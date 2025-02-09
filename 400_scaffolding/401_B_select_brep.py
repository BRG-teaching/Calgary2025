#! python3
# venv: brg-csd

import compas_rhino
from compas.scene import Scene
from compas.geometry import Translation

guid = compas_rhino.objects.select_object()
brep = compas_rhino.conversions.brepobject_to_compas(guid)
print(brep)

# Add code below: 1) copy geometry, transform it and add it to scene.
T = Translation.from_vector([0, 0, 10])
brep.transform(T)

scene = Scene()
scene.add(brep)
scene.draw()
