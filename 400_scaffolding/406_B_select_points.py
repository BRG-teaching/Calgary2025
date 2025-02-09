#! python3
# venv: brg-csd

import compas_rhino

guids = compas_rhino.objects.select_objects()

# Convert guids to points
points = []
for guid in guids:
    points.append(compas_rhino.conversions.pointobject_to_compas(guid))
print(points)
