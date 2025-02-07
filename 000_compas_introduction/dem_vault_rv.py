#! python3
# venv: brg-csd
# r: compas_model

import pathlib

import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import KDTree
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Plane
from compas.geometry import bestfit_plane_numpy
from compas.geometry import trimesh_remesh
from compas.itertools import pairwise
from compas.scene import Scene
from compas_tna.diagrams import FormDiagram
from compas_viewer import Viewer
from compas_viewer.config import Config
from scipy.interpolate import griddata


def break_boundary(mesh: Mesh, breakpoints: list[int]) -> tuple[list[list[int]], list[int]]:
    boundary: list[int] = mesh.vertices_on_boundaries()[0]
    if boundary[0] == boundary[-1]:
        del boundary[-1]

    breakpoints = sorted(breakpoints, key=lambda s: boundary.index(s))

    start = boundary.index(breakpoints[0])
    boundary = boundary[start:] + boundary[:start]

    borders = []
    for a, b in pairwise(breakpoints):
        start = boundary.index(a)
        end = boundary.index(b)
        borders.append(boundary[start : end + 1])
    borders.append(boundary[end:] + boundary[:1])

    return borders, breakpoints


# =============================================================================
# Load data
# =============================================================================

IFILE = pathlib.Path(__file__).parent.parent / "data" / "shell_final.json"

rv_session = compas.json_load(IFILE)
rv_scene: Scene = rv_session["scene"]

thrustobject = rv_scene.find_by_name("ThrustDiagram")
thrustdiagram: FormDiagram = thrustobject.mesh

# =============================================================================
# Mesh
#
# - make a copy of the thrustdiagram
# - remove the "TNA" faces cooresponding to boundary openings
# - compute the average edge length for remeshing
# =============================================================================

mesh: Mesh = thrustdiagram.copy(cls=Mesh)

for face in list(mesh.faces_where(_is_loaded=False)):
    mesh.delete_face(face)

length = sum(mesh.edge_length(edge) for edge in mesh.edges()) / mesh.number_of_edges()

# =============================================================================
# Mesh: Borders
# =============================================================================

supports = list(mesh.vertices_where(is_support=True))
borders, supports = break_boundary(mesh, supports)

mesh.attributes["supports"] = supports
mesh.attributes["borders"] = borders

# =============================================================================
# Trimesh
#
# - convert a copy of the mesh to a trimesh using "quads to triangles"
# - note that this doesn't work for other patterns
# =============================================================================

trimesh: Mesh = mesh.copy()
trimesh.quads_to_triangles()

# =============================================================================
# Trimesh: Remeshing
#
# - remesh using CGAL
# - use a percentage of the average edge length of the original mesh as target length
# =============================================================================

M = trimesh.to_vertices_and_faces()
V, F = trimesh_remesh(M, target_edge_length=0.9 * length, number_of_iterations=100)

trimesh = Mesh.from_vertices_and_faces(V, F)

# =============================================================================
# Dual
#
# - construct a dual
# - update default attributes
# - flip the cycles because a dual has opposite cycles compared to the original
# =============================================================================

dual: Mesh = trimesh.dual(include_boundary=True)

dual.update_default_edge_attributes(is_support=False)
dual.update_default_face_attributes(number=None, batch=None)
dual.update_default_vertex_attributes(thickness=0, is_corner=False, is_support=False)

dual.flip_cycles()

# =============================================================================
# Dual: Reconnect corners
#
# - construct a KD tree for nearest neighbour search
# - find the neares neighbours in the dual to the supports of the original
# - snap the dual vertices to the location of the supports
# - mark the corresponding vertices as "corners"
# =============================================================================

vertices = dual.vertices_attributes("xyz")
vertex_index = {vertex: index for index, vertex in enumerate(dual.vertices())}
index_vertex = {index: vertex for index, vertex in enumerate(dual.vertices())}
tree = KDTree(vertices)

for vertex in mesh.vertices_where(is_support=True):
    point = mesh.vertex_point(vertex)
    closest, nnbr, distance = tree.nearest_neighbor(point)
    dual_vertex = index_vertex[nnbr]
    if distance > 5:
        dual.vertex_attributes(dual_vertex, names="xyz", values=point)
    dual.vertex_attribute(dual_vertex, name="is_corner", value=True)

# =============================================================================
# Dual: Collapse 2-valent boundary edges
# =============================================================================

tofix = []

for vertex in dual.vertices_on_boundary():
    if dual.vertex_degree(vertex) > 2:
        continue
    tofix.append(vertex)

for vertex in tofix:
    nbrs = dual.vertex_neighbors(vertex)
    v0 = dual.edge_vector((vertex, nbrs[0]))
    v1 = dual.edge_vector((vertex, nbrs[1]))
    angle = v0.angle(v1, degrees=True)

    if abs(angle - 180) > 30:
        continue

    if dual.has_edge((vertex, nbrs[0])):
        is_corner = dual.vertex_attribute(nbrs[0], name="is_corner")
        dual.collapse_edge((vertex, nbrs[0]), t=1, allow_boundary=True)
    else:
        is_corner = dual.vertex_attribute(nbrs[1], name="is_corner")
        dual.collapse_edge((vertex, nbrs[1]), t=1, allow_boundary=True)

    if is_corner:
        dual.vertex_attribute(vertex, name="is_corner", value=True)

# =============================================================================
# Dual: Boundary smoothing
# =============================================================================

corners = list(dual.vertices_where(is_corner=True))
borders, corners = break_boundary(dual, corners)

curves: list[NurbsCurve] = []
for border in borders:
    vertices = border[::2] if len(border) > 4 else border
    points = dual.vertices_points(vertices=vertices)
    curve: NurbsCurve = NurbsCurve.from_interpolation(points, precision=1)
    curves.append(curve)

for border, curve in zip(borders, curves):
    for vertex in border[1:-1]:
        nbrs = dual.vertex_neighbors(vertex)
        for nbr in nbrs:
            if nbr not in border:
                point = dual.vertex_point(nbr)
                closest = curve.closest_point(point)
                dual.vertex_attributes(vertex, "xyz", closest)
                break

# =============================================================================
# Dual: Edge collapse
# =============================================================================

tocollapse = []

for u, v in dual.edges_on_boundary():
    if dual.vertex_attribute(u, "is_corner") or dual.vertex_attribute(v, "is_corner"):
        continue
    face = dual.halfedge_face((v, u))
    vertices = dual.face_vertices(face)
    if len(vertices) == 4:
        vv = dual.face_vertex_ancestor(face, v)
        uu = dual.face_vertex_descendant(face, u)
        tocollapse.append((u, v))
        tocollapse.append((uu, vv))

for u, v in tocollapse:
    dual.collapse_edge((u, v), allow_boundary=True)

# =============================================================================
# Dual: Borders
# =============================================================================

corners = list(dual.vertices_where(is_corner=True))
borders, corners = break_boundary(dual, corners)

for border in borders:
    if len(border) < 5:
        dual.vertices_attribute(name="is_support", value=True)
        for edge in pairwise(border):
            dual.edge_attribute(edge, name="is_support", value=True)

# =============================================================================
# Blocks: Thickness interpolation griddata
# =============================================================================

points = []
values = []

supports_by_height = sorted(mesh.attributes["supports"], key=lambda v: mesh.vertex_attribute(v, "z"))

for support in supports_by_height[:4]:
    points.append(mesh.vertex_attributes(support, "xy"))
    values.append(30)

for support in supports_by_height[4:]:
    points.append(mesh.vertex_attributes(support, "xy"))
    values.append(20)

for border in mesh.attributes["borders"]:
    if len(border) > 4:
        midspan = border[len(border) // 2]
        points.append(mesh.vertex_attributes(midspan, "xy"))
        values.append(15)

vertices_by_height = sorted(mesh.vertices(), key=lambda v: mesh.vertex_attribute(v, "z"))

for vertex in vertices_by_height[-5:]:
    points.append(mesh.vertex_attributes(vertex, "xy"))
    values.append(10)

# =============================================================================
# Blocks: Thickness interpolation sampling
# =============================================================================

samples = dual.vertices_attributes("xy")
thickness = griddata(points, values, samples)

for vertex, t in zip(dual.vertices(), thickness):
    dual.vertex_attribute(vertex, "thickness", t)

# =============================================================================
# Blocks
# =============================================================================

blocks = []

for face in dual.faces():
    vertices = dual.face_vertices(face)
    normals = [dual.vertex_normal(vertex) for vertex in vertices]
    thickness = dual.vertices_attribute("thickness", keys=vertices)

    middle = dual.face_polygon(face)
    bottom = [point - vector * (0.5 * t) for point, vector, t in zip(middle, normals, thickness)]
    top = [point + vector * (0.5 * t) for point, vector, t in zip(middle, normals, thickness)]

    plane = Plane(*bestfit_plane_numpy(top))

    flattop = []
    for a, b in zip(bottom, top):
        b = plane.intersection_with_line(Line(a, b))
        flattop.append(b)

    sides = []
    for (a, b), (aa, bb) in zip(pairwise(bottom + bottom[:1]), pairwise(flattop + flattop[:1])):
        sides.append([a, b, bb, aa])

    polygons = [bottom[::-1]] + [flattop] + sides

    block = Mesh.from_polygons(polygons)
    block.update_default_face_attributes(is_support=False, is_interface=False)

    for index, (u, v) in enumerate(pairwise(vertices + vertices[:1])):
        is_support = dual.edge_attribute((u, v), name="is_support")
        if is_support:
            face = 2 + index
            block.face_attribute(face, "is_support", True)

    blocks.append(block)

# =============================================================================
# Block: Chamfering
# =============================================================================

# =============================================================================
# Visualisation
# =============================================================================

config = Config()
config.camera.target = [500, 500, 50]
config.camera.position = [500, -500, 100]
config.camera.near = 1
config.camera.far = 10000
config.renderer.gridsize = (1000, 10, 1000, 10)

viewer = Viewer(config=config)
# viewer.scene.add(mesh, show_faces=False, show_edges=True)
# viewer.scene.add(dual, facecolor={face: Color.red() for face in tocollapse})
for block in blocks:
    viewer.scene.add(block, facecolor={face: Color.red() for face in block.faces_where(is_support=True)})
# viewer.scene.add(curves, linewidth=3)

# =============================================================================
# Save
# =============================================================================

OFILE = pathlib.Path(__file__).parent.parent / "data" / "shell_final_blocks.json"
compas.json_dump(blocks, OFILE)

# Save the dual mesh
DUAL_FILE = pathlib.Path(__file__).parent.parent / "data" / "shell_final_dual.json"
compas.json_dump(dual, DUAL_FILE)

bottom_polygons = []

for block in blocks:
    block: Mesh
    bottom_polygons.append(block.face_polygon(0))

bottom_mesh = Mesh.from_polygons(bottom_polygons)

# Save the bottom mesh
BOTTOM_FILE = pathlib.Path(__file__).parent.parent / "data" / "shell_final_bottom.json"
compas.json_dump(bottom_mesh, BOTTOM_FILE)

print(bottom_mesh)

viewer.scene.add(bottom_mesh, facecolor={face: Color.red() for face in bottom_mesh.faces()})

viewer.show()

