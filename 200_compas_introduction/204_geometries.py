#! python3
# venv: brg-csd
# r: compas_rv


from compas.scene import Scene
from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Point
from compas.geometry import Line
from compas.geometry import Frame
from compas.colors import Color

# Create a scene and add the box to it
scene = Scene()
scene.clear_context()

# Add a box
box = Box(1, 2, 3, frame=Frame([0, 0, 0]))
scene.add(box, color=Color.green())

# Add a sphere
sphere = Sphere(2, Frame([5, 0, 0]))
scene.add(sphere, color=Color.red())

# Add a point
point = Point(10, 0, 0)
scene.add(point, color=Color.blue())

# Add a line
line = Line([15, 0, 0], [15, 0, 5])
scene.add(line, color=Color.yellow())

# Draw the scene
scene.draw()
