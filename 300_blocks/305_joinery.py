#! python3
# venv: brg-csd

import pathlib
import compas
from compas.datastructures import Mesh
from compas.geometry import Sphere, Brep
from compas.scene import Scene


# Define input file path and load dual mesh
IFILE = pathlib.Path(__file__).parent.parent / "data" / "304_dual.json"
dual: Mesh = compas.json_load(IFILE)

# Convert block meshes to Brep objects
block_breps = {face: Brep.from_mesh(dual.face_attribute(face, "block")) for face in dual.faces()}

# Process each edge in the dual mesh
for edge in dual.edges():
    # Get faces connected to the edge
    face1, face2 = dual.edge_faces(edge)
    if face1 is not None and face2 is not None:
        # Create local coordinate system
        line = dual.edge_line(edge)
        z_axis = line.direction
        x_axis = dual.vertex_normal(edge[0]) + dual.vertex_normal(edge[1])
        y_axis = x_axis.cross(z_axis)

        # Create points at 30% and 70% along the edge
        p1 = line.point_at(0.3)
        p2 = line.point_at(0.7)

        # Create larger spheres for subtraction (male joint)
        sphere1a = Sphere(2.5, point=p1)
        sphere1b = Sphere(2.5, point=p2)

        # Create smaller spheres for addition (female joint)
        sphere2a = Sphere(2.3, point=p1)
        sphere2b = Sphere(2.3, point=p2)

        # Get blocks for both faces
        block1 = block_breps[face1]
        block2 = block_breps[face2]

        # Create male-female joint by boolean operations
        # Subtract larger spheres from first block (male)
        block1 = block1 - sphere1a.to_brep()
        block1 = block1 - sphere1b.to_brep()
        # Add smaller spheres to second block (female)
        block2 = block2 + sphere2a.to_brep()
        block2 = block2 + sphere2b.to_brep()

        # Store modified blocks back in dictionary
        block_breps[face1] = block1
        block_breps[face2] = block2

# Create and setup visualization scene
scene = Scene()
scene.clear_context()
scene.add(dual)
# Add all blocks to scene
for block in block_breps.values():
    scene.add(block)
scene.draw()
