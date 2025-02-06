#! python3
# venv: brg-csd
# r: compas_rv, compas_model

from compas.datastructures import Mesh
from compas.geometry import Plane
from compas.geometry import Line
from compas.geometry import Sphere
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Brep

from compas.datastructures import Mesh
from compas.scene import Scene
from compas import json_load
from compas import json_dump
import pathlib

scene = Scene()

# Load dual
filepath = pathlib.Path(__file__).parent.parent / "data" / "shell_final_dual.json"
dual = json_load(filepath)

# Deserialize Mesh
filepath = pathlib.Path(__file__).parent.parent / "data" / "shell_final_blocks.json"
blocks = json_load(filepath)


mesh = dual
block_meshes = []
fkey_index = {}

block_breps = [Brep.from_mesh(block) for block in blocks]

fkey_index = {}
for i_face, face in enumerate(dual.faces()):
    fkey_index[face] = i_face

for edge in mesh.edges():
    face1, face2 = mesh.edge_faces(edge)
    if face1 is not None and face2 is not None:
        line = mesh.edge_line(edge)
        z_axis = line.direction
        x_axis = mesh.vertex_normal(edge[0]) + mesh.vertex_normal(edge[1])
        y_axis = x_axis.cross(z_axis)
        
        # Create frames at 0.3 and 0.7 along the edge
        p1 = line.point_at(0.3)
        p2 = line.point_at(0.7)
        frame1 = Frame(p1, x_axis, y_axis)
        frame2 = Frame(p2, x_axis, y_axis)

        sphere1a = Sphere(3, frame1)
        sphere1b = Sphere(3, frame2)

        sphere2a = Sphere(2.5, frame1) 
        sphere2b = Sphere(2.5, frame2)
        # xsize = 2
        # ysize = 2
        # zsize = line.length * 0.75
        # tolerance = 0.2
        # box0 = Box(xsize + tolerance, ysize + tolerance, zsize + tolerance, frame)
        # box1 = Box(xsize, ysize, zsize, frame)

        # block_breps[fkey_index[face1]] = block_breps[fkey_index[face1]] - box0.to_brep()
        # block_breps[fkey_index[face2]] = block_breps[fkey_index[face2]] + box1.to_brep()

        # make two spheres along the edge
        block_breps[fkey_index[face1]] = block_breps[fkey_index[face1]] - sphere1a.to_brep()
        block_breps[fkey_index[face1]] = block_breps[fkey_index[face1]] - sphere1b.to_brep()
        block_breps[fkey_index[face2]] = block_breps[fkey_index[face2]] + sphere2a.to_brep()
        block_breps[fkey_index[face2]] = block_breps[fkey_index[face2]] + sphere2b.to_brep()

        


# scene.add(dual)

for block in block_breps:
    scene.add(block)

scene.draw()
