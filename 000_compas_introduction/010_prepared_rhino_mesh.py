#! python3
# venv: brg-csd
# r: compas_rv

import compas_rhino.objects
import compas_rhino.conversions
from compas.datastructures import Mesh
from compas.scene import Scene

# Select Mesh
guids = compas_rhino.objects.select_meshes()
polygons = []
for guid in guids:
    mesh = compas_rhino.conversions.meshobject_to_compas(guid)
    polygons.extend(mesh.to_polygons())

# Join Mesh
mesh = Mesh.from_polygons(polygons)




# Triangulate

# Mesh Dual

# Offset

# Create Blocks

# Vizualization
scene = Scene()
scene.add(mesh)
scene.draw()