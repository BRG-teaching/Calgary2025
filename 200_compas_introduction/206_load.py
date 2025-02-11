#! python3
# venv: brg-csd
# r: compas_rv

import pathlib
from compas.geometry import Box
from compas.scene import Scene

# Define the file path to load the box from JSON
filepath = pathlib.Path(__file__).parent.parent / "data" / "box.json"

# Load the box from JSON file
box = Box.from_json(filepath)

# Create a scene and add the box to it
scene = Scene()
scene.clear_context()
scene.add(box)

# Draw the scene
scene.draw()
