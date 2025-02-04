#! python3
# venv: brg-csd
# r: compas_rv

"""
1. Make a box.
2. Add the box to a scene.
3. Draw the scene.
4. Change color.
5. Delete previous objects.
"""

from compas.geometry import Box
from compas.scene import Scene
import compas
print(compas.__version__)

# Create a box
box = Box(1, 1, 1)

# Create a scene and add the box to it
scene = Scene()
scene.add(box)

# Draw the scene
scene.draw()