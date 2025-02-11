#! python3
# venv: brg-csd

import pathlib

from compas.datastructures import Mesh
from compas import json_load
from compas.scene import Scene
from compas.colors import Color
from compas.geometry import Sphere
from scipy.interpolate import griddata
from compas import json_dump

# Define input file path
IFILE = pathlib.Path(__file__).parent.parent / "data" / "302_dual.json"

# Load dual mesh from file
dual: Mesh = json_load(IFILE)

# Create and clear visualization scene
scene = Scene()
scene.clear_context()

# Initialize lists to store points and their thickness values
points = []
values = []

# Add support points with thickness of 30.0
for vertex in dual.vertices():
    if dual.vertex_attribute(vertex, "is_support"):
        point = dual.vertex_attributes(vertex, "xy")
        points.append(point)
        values.append(30.0)

# Sort vertices by height and get the 5 highest points
vertices_by_height = sorted(dual.vertices(), key=lambda v: dual.vertex_attribute(v, "z"))

# Add the 5 highest points with thickness of 10.0
for vertex in vertices_by_height[-5:]:
    points.append(dual.vertex_attributes(vertex, "xy"))
    values.append(10.0)

# Get xy coordinates of all vertices for interpolation
samples = dual.vertices_attributes("xy")
# Interpolate thickness values for all vertices
thickness = griddata(points, values, samples)

# Assign thickness values and visualize with spheres
for vertex, t in zip(dual.vertices(), thickness):
    # Store thickness value as vertex attribute
    dual.vertex_attribute(vertex, "thickness", t)
    
    # Create color based on thickness and add sphere to scene
    color = Color.from_i((t-10)/20)
    scene.add(Sphere(t, point=dual.vertex_point(vertex)),  color=color)

# Add dual mesh to scene and display
scene.add(dual)
scene.draw()

# Define output file path and save dual mesh
OFILE = pathlib.Path(__file__).parent.parent / "data" / "303_dual.json"
json_dump(dual, OFILE)
