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
from compas.geometry import Transformation

from compas.datastructures import Mesh
from compas.scene import Scene
from compas import json_load
from compas import json_dump
import pathlib

from compas_rhino.conversions import plane_to_rhino
from compas_rhino.conversions import brep_to_compas
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc

scene = Scene()
# scene.clear_context()

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


def create_3d_text(text, plane, group_name, height=8.0, extrusion_distance=0.5):
    """Create 3D text geometry in Rhino and add it to a group.
    
    Args:
        text (str): The text to create
        plane: Rhino plane for text placement
        group_name (str): Name of the group to add text objects to
        height (float): Text height
        extrusion_distance (float): Depth of the 3D text
    
    Returns:
        list: List of COMPAS Brep objects representing the 3D text
    """
    # Create 2D text
    text_obj = rs.AddText(text, plane, height, justification=2)
    
    # Explode text into curves
    text_curves = rs.ExplodeText(text_obj, True)
    
    # Create surfaces from the curves
    text_surfaces = rs.AddPlanarSrf(text_curves)
    
    # Convert surfaces to Rhino geometry
    rhino_surfaces = [rs.coercesurface(srf) for srf in text_surfaces]
    
    # Create extruded 3D text
    text_3d = []
    text_breps = []  # Store the Brep objects for boolean operation
    
    for srf in rhino_surfaces:
        brep = rg.Brep.CreateFromOffsetFace(srf, extrusion_distance, 0.01, True, True)
        text_3d.append(sc.doc.Objects.AddBrep(brep))
        text_breps.append(brep_to_compas(brep))
    
    # Clean up temporary objects
    rs.DeleteObjects(text_curves + text_surfaces + [text_obj])
    
    # Group the 3D text objects
    rs.AddObjectsToGroup(text_3d, group_name)
    
    return text_breps


# Create a grid layout for the blocks
grid_size = 120  # spacing between blocks
blocks_per_row = int(len(block_breps)**0.5) + 1  # approximate square grid

print(len(blocks), blocks_per_row)

for i, block in enumerate(blocks):

    top_face_frame = block.face_frame(1)
    top_face_frame.flip()

    # Calculate grid position
    row = i // blocks_per_row
    col = i % blocks_per_row
    
    # Create target frame with Z pointing up (top face will be down)
    target_point = [col * grid_size, row * grid_size, 0]
    target_frame = Frame.worldXY()
    target_frame.point = target_point
    
    transformation = Transformation.from_frame_to_frame(top_face_frame, target_frame) 

    # Transform blocks to target position
    block_breps[i].transform(transformation)
    block.transform(transformation)


# Add labels, has to be done manually for now.

group_name = "Labels"
rs.AddGroup(group_name)

for i, block in enumerate(blocks):
    block: Mesh
    plane = block.face_plane(0)
    plane = plane_to_rhino(plane)
    text_breps = create_3d_text(str(i), plane, group_name)


for block in block_breps:
    scene.add(block)

scene.draw()