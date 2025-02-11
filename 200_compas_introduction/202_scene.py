#! python3
# venv: brg-csd
# r: compas_rv

from compas.geometry import Box
from compas.scene import Scene

# Create a box
box = Box(1, 2, 3)

# Create a scene and add the box to it
scene = Scene()
scene.clear_context()
scene.add(box)

# Draw the scene
scene.draw()
