#! python3
# venv: brg-csd
# r: compas_rv

import compas
from compas.scene import Scene
from compas.datastructures import Mesh
import compas

# Create a mesh from an obj file
mesh = Mesh.from_obj(compas.get("tubemesh.obj"))
print(mesh)

# Create a scene
scene = Scene()
scene.clear_context()

# Add the mesh to the scene
scene.add(mesh)

# Draw the scene
scene.draw()
