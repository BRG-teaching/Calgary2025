#! python3
# venv: brg-csd
# r: compas_rv

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Polygon
from compas.geometry import boolean_difference_mesh_mesh
from compas.scene import Scene

# Create a box and a sphere
box = Box(2)
sphere = Sphere(radius=1.0, point=[1, 1, 1])
result = box.to_brep() - sphere.to_brep()

# Create a scene and add the result and polygons to it
scene = Scene()
scene.clear_context()
scene.add(result)
scene.draw()