#! python3
# venv: brg-csd
# r: compas_rv

import compas_rhino.objects
import compas_rhino.conversions
from compas.datastructures import Mesh
from compas.scene import Scene
from compas.geometry import Point, Polyline, Vector, subtract_vectors, Line, distance_point_point, Polygon


# Select Mesh
guids = compas_rhino.objects.select_meshes()
polygons = []
for guid in guids:
    mesh = compas_rhino.conversions.meshobject_to_compas(guid)
    polygons.extend(mesh.to_polygons())

# Join Mesh
mesh = Mesh.from_polygons(polygons)

# Get Corners
corner_points = []
for v in mesh.vertices_where({"z":[0,0.1]}):
    p = mesh.vertex_point(v)
    corner_points.append(p)

# Triangulate / Remesh

def tangent_of_closest_curve(polylines : list[Polyline], point : Point):
    
    cp_distance = float('inf')
    cp_line = None
    for polyline in polylines:
        for i in range(len(polyline)-1):
            line = Line(polyline[i], polyline[i+1])
            cp, t = line.closest_point(point, True)
            local_distance = distance_point_point(point, cp)

            if local_distance < cp_distance:
                cp_distance = local_distance
                cp_line = line
    return cp_line.vector

def triangulate_by_curves(mesh: Mesh, polylines : list[Polyline] = []):
    
    faces2 = []
    vertices, faces = mesh.to_vertices_and_faces()

    for i in range(len(faces)):
        if(len(faces[i]) == 4):
            if len(polylines) == 0:
                faces2.append([faces[i][0], faces[i][1], faces[i][2]])
                faces2.append([faces[i][2], faces[i][3], faces[i][0]])
            else:
                
                c = mesh.face_center(i)
                tangent = tangent_of_closest_curve(polylines, c)
                # tangent = Vector(*[0.0, 1.0, 0.0])

                fa = Vector(*vertices[faces[i][0]])
                fb = Vector(*vertices[faces[i][1]])
                fc = Vector(*vertices[faces[i][2]])
                fd = Vector(*vertices[faces[i][3]])

                fc_fa = fc-fa
                fa_fc = fa-fc
                fb_fd = fb-fd
                fd_fb = fd-fb

                angle0 = min(tangent.angle(fc_fa), tangent.angle(fa_fc))
                angle1 = min(tangent.angle(fb_fd), tangent.angle(fd_fb))

                if angle1 > angle0:
                    faces2.append([faces[i][0], faces[i][1], faces[i][2]])
                    faces2.append([faces[i][2], faces[i][3], faces[i][0]])
                else:
                    faces2.append([faces[i][1], faces[i][2], faces[i][3]])
                    faces2.append([faces[i][3], faces[i][0], faces[i][1]])   


        if(len(faces[i]) == 3):
            faces2.append(faces[i])

    return Mesh.from_vertices_and_faces(vertices, faces2)

pts = mesh.aabb().points
polyline = Polyline([pts[0], pts[1], pts[2], pts[3], pts[0]])
mesh_triangulated = triangulate_by_curves(mesh, [polyline])

# Mesh Dual
dual = mesh_triangulated.dual(include_boundary=True)

# Simplify

def simplify_mesh(mesh : Mesh, corners : list[Point]):
    polygons = []
    for face in mesh.faces():
        
        if mesh.is_face_on_boundary(face):
            points = []
            vertices = mesh.face_vertices(face)
            for v in vertices:
                p = mesh.vertex_point(v)
                if mesh.vertex_degree(v) == 2:
                    for c in corners:
                        if (distance_point_point(p, c) < 0.01):
                            points.append(p)
                            break
                else:
                    points.append(p)
            polygons.append(Polygon(points))
        else:
            polygons.append(mesh.face_polygon(face))
       
    return Mesh.from_polygons(polygons)

mesh_simplified = simplify_mesh(dual, corner_points)

# Vizualization
scene = Scene()
scene.add(mesh)
scene.add(mesh_simplified)
scene.draw()