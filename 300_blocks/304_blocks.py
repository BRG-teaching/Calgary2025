#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas.geometry import Plane
from compas.geometry import Polygon
from compas import json_load
from compas.scene import Scene
from compas import json_dump


# Define input file path
IFILE = pathlib.Path(__file__).parent.parent / "data" / "303_dual.json"

# Load dual mesh from file
dual: Mesh = json_load(IFILE)

# Create and clear visualization scene
scene = Scene()
scene.clear_context()

# Iterate through faces in dual mesh
for face_key in dual.faces():
    # Initialize lists to store points for block geometry
    top_points = []
    flat_top_points = []
    bottom_points = []
    
    # Process vertices of current face
    for vertex in dual.face_vertices(face_key):
        # Get vertex normal and thickness
        normal = dual.vertex_normal(vertex)
        thickness = dual.vertex_attribute(vertex, "thickness")
        
        # Calculate inner and outer points based on thickness
        point_in = dual.vertex_point(vertex) - normal * thickness / 2
        point_out = dual.vertex_point(vertex) + normal * thickness / 2

        # Store points for block construction
        top_points.append(point_out)
        bottom_points.append(point_in)

    # Create plane from top points and project points onto it
    plane = Plane.from_points(top_points)
    for point in top_points:
        projected_point = plane.projected_point(point, normal)
        flat_top_points.append(projected_point)

    # Create polygons for top and bottom faces
    top_polygon = Polygon(flat_top_points)
    bottom_polygon = Polygon(bottom_points)

    # Create side polygons by connecting top and bottom faces
    side_polygons = []
    for (a, b), (aa, bb) in zip(zip(bottom_polygon, bottom_polygon[1:] + bottom_polygon[:1]), zip(top_polygon, top_polygon[1:] + top_polygon[:1])):
        side_polygons.append(Polygon([a, b, bb, aa]))

    # Reverse bottom polygon vertices for correct orientation
    bottom_polygon = Polygon(bottom_polygon[::-1])

    # Create block mesh from polygons and set attributes
    block = Mesh.from_polygons([top_polygon] + [bottom_polygon] + side_polygons)
    block.face_attribute(0, "is_top", True)
    block.face_attribute(1, "is_bottom", True)
    block.name = f"Block {face_key}"

    # Store block in dual mesh and add to scene
    dual.face_attribute(face_key, "block", block)
    scene.add(block)

# Display the scene
scene.draw()

# Define output file path and save dual mesh
OFILE = pathlib.Path(__file__).parent.parent / "data" / "304_dual.json"
json_dump(dual, OFILE)
