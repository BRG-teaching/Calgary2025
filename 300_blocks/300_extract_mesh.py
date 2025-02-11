#! python3
# venv: brg-csd

import pathlib

import compas
from compas_tna.diagrams import FormDiagram
from compas.datastructures import Mesh
from compas import json_dump


IFILE = pathlib.Path(__file__).parent.parent / "data" / "shell_final.json"

session = compas.json_load(IFILE)
scene = session["scene"]

thrustobject = scene.find_by_name("ThrustDiagram")
thrustdiagram: FormDiagram = thrustobject.mesh

mesh = thrustdiagram.copy(cls=Mesh)

# Clean up the un-loaded faces
for face in list(mesh.faces_where(_is_loaded=False)):
    mesh.delete_face(face)

# Clear the scene and add the mesh
scene.clear()
scene.clear_context()
scene.add(mesh)
scene.draw()

# Save the mesh
OFILE = pathlib.Path(__file__).parent.parent / "data" / "300_mesh.json"
json_dump(mesh, OFILE)
