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

from compas_model.models import Model
from compas.datastructures import Mesh
from compas.scene import Scene
from compas import json_load
import pathlib

# Deserialize Mesh
filepath = pathlib.Path(__file__).parent.parent / "data" / "010_prepared_mesh.json"
mesh = json_load(filepath)


scene = Scene()
scene.clear_context()


model = Model()
distance = 20
mesh_out: Mesh = mesh.offset(distance * 0.5)
mesh_in: Mesh = mesh.offset(-distance * 0.5)
block_meshes = []

elements = []

for face in mesh.faces():
    vertices = mesh.face_vertices(face)
    plane_out = Plane.from_points(mesh_out.vertices_points(vertices))
    plane_in = Plane.from_points(mesh_in.vertices_points(vertices))

    new_out_points = []
    new_in_points = []
    for vertex in vertices:
        pt_in = mesh_in.vertex_point(vertex)
        pt_out = mesh_out.vertex_point(vertex)
        line = Line(pt_in, pt_out)
        intersection_out = plane_out.intersection_with_line(line)
        intersection_in = plane_in.intersection_with_line(line)
        new_out_points.append(intersection_out)
        new_in_points.append(intersection_in)

    # Create a mesh block by connecting the two polygons
    block_vertices = new_out_points + new_in_points
    block_faces = []
    is_side_face = []
    n = len(new_out_points)

    # Create the side faces
    for i in range(n):
        i1 = i
        i2 = (i + 1) % n
        i3 = i2 + n
        i4 = i1 + n
        block_faces.append([i4, i3, i2, i1])
        is_side_face.append(True)

    # Add top and bottom faces
    top_face = list(range(n))
    bottom_face = [i + n for i in reversed(range(n))]
    block_faces.append(top_face)
    block_faces.append(bottom_face)
    is_side_face.append(False)
    is_side_face.append(False)

    block_mesh = Mesh.from_vertices_and_faces(block_vertices, block_faces)
    for face in block_mesh.faces():
        block_mesh.face_attribute(face, "is_side_face", is_side_face[face])

    brep = Brep.from_mesh(block_mesh)
    block_meshes.append(brep)

for i, element in enumerate(model.elements()):
    assert element == elements[i]
    scene.add(element.modelgeometry)


for edge in mesh.edges():
    face1, face2 = mesh.edge_faces(edge)
    if face1 is not None and face2 is not None:
        line = mesh.edge_line(edge)
        z_axis = line.direction
        x_axis = mesh.vertex_normal(edge[0]) + mesh.vertex_normal(edge[1])
        y_axis = x_axis.cross(z_axis)
        p = mesh.edge_midpoint(edge)
        frame = Frame(p, x_axis, y_axis)

        sphere = Sphere(5, frame)
        xsize = 2
        ysize = 2
        zsize = line.length * 0.75
        tolerance = 0.2
        box0 = Box(xsize + tolerance, ysize + tolerance, zsize + tolerance, frame)
        box1 = Box(xsize, ysize, zsize, frame)

        block_meshes[face1] = block_meshes[face1] - box0.to_brep()
        block_meshes[face2] = block_meshes[face2] + box1.to_brep()

# Vizualization
for block in block_meshes:
    scene.add(block)


scene.draw()
