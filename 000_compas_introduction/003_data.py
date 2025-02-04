#! python3
# venv: brg-csd
# r: compas_rv

import pathlib
from compas.geometry import Box

# Create a box
box = Box(1)

# Define the file path to save the box to JSON
filepath = pathlib.Path(__file__).parent.parent / "data" / "box.json"

# Save the box to JSON file
box.to_json(filepath)
