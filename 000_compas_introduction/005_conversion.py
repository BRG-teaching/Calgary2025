#! python3
# venv: brg-csd
# r: compas_rv

from compas.colors import Color
from compas.geometry import Box
from compas.scene import Scene

# Create a box
box = Box(1)

# Convert the box to different representations
poly = box.to_polyhedron()
mesh = box.to_mesh()
brep = box.to_brep()

# Create a scene and add the polyhedron to it
scene = Scene()
scene.clear_context()
scene.add(
    poly,
    facecolor=Color.green(),
    linecolor=Color.blue(),
    show_points=True,
    pointsize=10,
    pointcolor=Color.red(),
)

# Draw the scene
scene.draw()