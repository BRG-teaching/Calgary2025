from compas.datastructures import Mesh
from compas.geometry import Plane
from compas.geometry import intersection_line_plane
from compas.geometry import Line
from compas_viewer import Viewer
from compas.geometry import Polygon
from compas.geometry import Sphere

from compas_model.models import Model
from compas_model.elements import Element
from compas_model.interactions import BooleanModifier

class BlockElement(Element):
    pass

viewer = Viewer()

model = Model()


mesh = Mesh.from_obj('temp/shell.obj')
mesh.quads_to_triangles()
mesh:Mesh = mesh.dual()

mesh_out:Mesh = mesh.offset(0.1)
mesh_in:Mesh = mesh.offset(-0.1)

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
        block_faces.append([i1, i2, i3, i4])
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
        block_mesh.face_attribute(face, 'is_side_face', is_side_face[face])

    # for face in block_mesh.faces():
    #     if block_mesh.face_attribute(face, 'is_side_face'):
    #         polygon = block_mesh.face_polygon(face)
    #         viewer.scene.add(polygon)


    element = BlockElement(block_mesh)
    model.add_element(element)
    elements.append(element)



for i, element in enumerate(model.elements()):
    assert element == elements[i]
    viewer.scene.add(element.modelgeometry)



class SlotModifier(BooleanModifier):
    def apply(self, target):
        print(self, "->", target)

for edge in mesh.edges():
    face1, face2 = mesh.edge_faces(edge)
    if face1 is not None and face2 is not None:
        mid_pt = mesh.edge_midpoint(edge)
        sphere = Sphere(0.05, point=mid_pt)
        viewer.scene.add(sphere)
        
        elements = list(model.elements())

        element1 = elements[face1]
        element2 = elements[face2]

        print(element1, element2)

        model.add_interaction(element1, element2)
        model.add_modifier(element1, element2, SlotModifier)




# viewer.scene.add(mesh)
viewer.show()