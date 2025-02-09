#! python3
# venv: brg-csd

import compas_rhino
from compas.scene import Scene
from compas.geometry import Translation

# Change the code to select multiple lines
guids = compas_rhino.objects.select_objects()
lines = []
for guid in guids:
    obj = compas_rhino.objects.find_object(guid)
    line = compas_rhino.conversions.curve_to_compas_line(obj.Geometry)
    lines.append(line)
print(lines)
