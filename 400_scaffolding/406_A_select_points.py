#! python3
# venv: brg-csd

import compas_rhino
from compas.scene import Scene
from compas.geometry import Translation

guids = compas_rhino.objects.select_objects()

# Convert guids to points
