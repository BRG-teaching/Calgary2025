#! python3
# venv: brg-csd
# r: compas_rv

import compas
from compas.scene import Scene
from compas.datastructures import Mesh
import compas

mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

print(mesh)

scene = Scene()
scene.clear_context()
scene.add(mesh)

scene.draw()
