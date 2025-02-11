#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas import json_load
from compas.scene import Scene
from compas.geometry import Frame
from compas.geometry import Transformation

IFILE = pathlib.Path(__file__).parent.parent / "data" / "304_dual.json"
dual: Mesh = json_load(IFILE)

scene = Scene()
scene.clear_context()

blocks = []

for face in dual.faces():
    block = dual.face_attribute(face, "block")
    top_face = list(block.faces_where(is_top=True))[0]
    frame = block.face_frame(top_face)
    
    scene.add(block)
    scene.add(frame, scale=20)

    blocks.append((block, frame))



grid_size = 120  # spacing between blocks
blocks_per_row = int(len(blocks) ** 0.5) + 1  # approximate square grid

for i, (block, frame) in enumerate(blocks):
    row = i // blocks_per_row
    col = i % blocks_per_row

    target_point = [col * grid_size + 1200, row * grid_size, 0]
    target_frame = Frame.worldXY()
    target_frame.point = target_point

    frame.flip()

    T = Transformation.from_frame_to_frame(frame, target_frame)
    block_transformed = block.transformed(T)

    scene.add(block_transformed)
scene.draw()