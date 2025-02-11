#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas import json_load
from compas.scene import Scene
from compas.geometry import Frame
from compas.geometry import Transformation

# Load the dual mesh from file
IFILE = pathlib.Path(__file__).parent.parent / "data" / "304_dual.json"
dual: Mesh = json_load(IFILE)

# Create and clear visualization scene
scene = Scene()
scene.clear_context()

# List to store blocks and their frames
blocks = []

# Process each face in the dual mesh
for face in dual.faces():
    # Get the block mesh and its top face frame
    block = dual.face_attribute(face, "block")
    top_face = list(block.faces_where(is_top=True))[0]
    frame = block.face_frame(top_face)
    
    # Add block and frame to scene
    scene.add(block)
    scene.add(frame, scale=50)

    # Store block and frame for later use
    blocks.append((block, frame))

# Define grid layout parameters
grid_size = 120  # spacing between blocks
blocks_per_row = int(len(blocks) ** 0.5) + 1  # approximate square grid

# Arrange blocks in a grid layout
for i, (block, frame) in enumerate(blocks):
    # Calculate grid position
    row = i // blocks_per_row
    col = i % blocks_per_row

    # Create target frame at grid position
    target_point = [col * grid_size + 1200, row * grid_size, 0]
    target_frame = Frame.worldXY()
    target_frame.point = target_point

    # Flip frame to correct orientation
    frame.flip()

    # Transform block to target position
    T = Transformation.from_frame_to_frame(frame, target_frame)
    block_transformed = block.transformed(T)

    # Add transformed block and target frame to scene
    scene.add(block_transformed)
    scene.add(target_frame, scale=50)

# Display the scene
scene.draw()