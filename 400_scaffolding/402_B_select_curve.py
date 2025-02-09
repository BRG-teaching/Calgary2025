#! python3
# venv: brg-csd

import compas_rhino
from compas.scene import Scene
from compas.geometry import Transformation, Frame

guid = compas_rhino.objects.select_object()
curve = compas_rhino.conversions.curveobject_to_compas(guid)
print(curve)

# Add code below: 1) copy geometry, transform it and add it to scene.
frame = Frame(curve.points[0], [1, 0, 0], [0, 1, 0])
T = Transformation.from_frame_to_frame(frame, Frame.worldXY())
curve.transform(T)

scene = Scene()
scene.add(curve)
scene.draw()
