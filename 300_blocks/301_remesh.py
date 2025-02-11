#! python3
# venv: brg-csd
# r: compas_model

import pathlib
import compas
from compas.datastructures import Mesh
from compas.scene import Scene
from compas import json_dump
from compas.datastructures.mesh.remesh import trimesh_remesh
from compas.geometry import Line
from compas.geometry import normal_triangle
from compas.geometry import KDTree
from compas_model.geometry import intersection_ray_triangle

# Define input file path and load mesh
IFILE = pathlib.Path(__file__).parent.parent / "data" / "300_mesh.json"
mesh: Mesh = compas.json_load(IFILE)

# Create a copy of the mesh and convert quads to triangles
trimesh: Mesh = mesh.copy()
trimesh.quads_to_triangles()

# Calculate average edge length of original mesh
length = sum(mesh.edge_length(edge) for edge in mesh.edges()) / mesh.number_of_edges()
print("Average edge length:", length)


# Define projection callback function for remeshing
def project(mesh: Mesh, k, args):
    # Iterate through vertices
    for vertex in mesh.vertices():
        # Skip boundary vertices
        if mesh.is_vertex_on_boundary(vertex):
            continue
        # Get vertex coordinates
        point = mesh.vertex_point(vertex)
        # Find nearest neighbor in KD tree
        _, nbr, _ = tree.nearest_neighbor(point)
        # Get triangles connected to nearest vertex
        triangles = vertex_triangles[nbr]
        # Check intersection with each triangle
        for triangle in triangles:
            normal = normal_triangle(triangle)
            ray = Line.from_point_direction_length(point, normal, 10)
            result = intersection_ray_triangle(ray, triangle)
            if result:
                # Update vertex position to intersection point
                mesh.vertex_attributes(vertex, "xyz", result)
                break


# Create mapping of vertices to indices
vertex_index = {vertex: index for index, vertex in enumerate(trimesh.vertices())}
# Create mapping of vertices to connected triangles
vertex_triangles = {vertex_index[vertex]: [trimesh.face_points(face) for face in trimesh.vertex_faces(vertex)] for vertex in trimesh.vertices()}
# Get vertex coordinates for KD tree
vertices = trimesh.vertices_attributes("xyz")
# Create KD tree from vertices
tree = KDTree(vertices)

# Get fixed (boundary) and free vertices
fixed = list(trimesh.vertices_on_boundary())
free = set(list(trimesh.vertices())) - set(fixed)

# Perform remeshing with projection
trimesh_remesh(trimesh, length, kmax=300, tol=0.1, allow_boundary_split=False, callback=project)

# Save remeshed result
json_dump(trimesh, pathlib.Path(__file__).parent.parent / "data" / "301_mesh.json")

# Visualize result
scene = Scene()
scene.clear_context()
scene.add(trimesh)
scene.draw()
