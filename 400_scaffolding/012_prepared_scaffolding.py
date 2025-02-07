#! python3
# venv: brg-csd
# r: compas_rv

import compas_rhino.objects
import compas_rhino.conversions
from compas.datastructures import Mesh
from compas.scene import Scene
from compas.geometry import Point, Polyline, Vector, Line, distance_point_point, Polygon, Frame, Transformation, bounding_box,Box, Plane, intersection_polyline_plane
from compas import json_dump
import pathlib
import Rhino
import rhinoscriptsyntax as rs
from math import ceil
from compas.geometry import trimesh_slice

scene = Scene()

# Select Mesh
guids = compas_rhino.objects.select_meshes()
polygons = []
for guid in guids:
    mesh = compas_rhino.conversions.meshobject_to_compas(guid)
    polygons.extend(mesh.to_polygons())

mesh = Mesh.from_polygons(polygons)

# Select Boundary Polygon
guid = rs.GetObject("Select a polyline", rs.filter.curve)
rh_pline = obj = compas_rhino.objects.find_object(guid).Geometry.ToPolyline()
polyline = compas_rhino.conversions.polyline_to_compas(rh_pline)

# Select Primary Direction
guid = rs.GetObject("Select a line", rs.filter.curve)
rh_line = compas_rhino.objects.find_object(guid).Geometry
line = Line([rh_line.PointAtStart.X, rh_line.PointAtStart.Y, rh_line.PointAtStart.Z], [rh_line.PointAtEnd.X, rh_line.PointAtEnd.Y, rh_line.PointAtEnd.Z])

def get_section_frames(mesh, polyline, line, division_distance_u=1, division_distance_v=1.5):

    # orient object to xy
    origin = line.start
    x_axis = line.direction
    y_axis = x_axis.cross([0,0,-1])
    frame = Frame(origin, x_axis, y_axis)
    T = Transformation.from_frame_to_frame(frame, Frame.worldXY())
    mesh_ = mesh.transformed(T)
    polyline_ = polyline.transformed(T)
    line_ = line.transformed(T)

    # Get aabb of the polygon and interpolate their sides
    aabb = Box.from_points(bounding_box(polyline_))
    divisions_u = int(ceil(aabb.xsize/division_distance_u))
    divisions_v = int(ceil(aabb.ysize/division_distance_v))


    # Slice the Mesh
    origin = aabb.corner(0)
    x_axis = Vector.Xaxis()
    y_axis = Vector.Yaxis()
    planes_u = []
    for i in range(divisions_u):
        plane_u = Plane(origin+x_axis*i*division_distance_u, x_axis)
        planes_u.append(plane_u)

    planes_v = []
    for i in range(divisions_v):
        plane_v = Plane(origin+y_axis*i*division_distance_v, y_axis)
        planes_v.append(plane_v)

    
    polylines_u = trimesh_slice(mesh_.to_vertices_and_faces(), planes_u)
    polylines_v = trimesh_slice(mesh_.to_vertices_and_faces(), planes_v)

    # Create geometry key for 2D point and their Z coordinate:
    gkeys = {}
    polylines_u_projected = []
    for polyline in polylines_u:
        polyline_u_projected = []
        for point in polyline:
            gkeys[str(round(point[0],3))+","+str(round(point[1], 3))+","+str(round(point[2], 3))] = point[2]
            polyline_u_projected.append([point[0], point[1], 0])
        polylines_u_projected.append(polyline_u_projected)
        
    
    polylines_v_projected = []
    for polyline in polylines_v:
        polyline_v_projected = []
        for point in polyline:
            gkeys[str(round(point[0],3))+","+str(round(point[1], 3))+","+str(round(point[2], 3))] = point[2]
            polyline_v_projected.append([point[0], point[1], 0])
        polylines_v_projected.append(polyline_v_projected)

    # Boolean intersect the lines.


    # Polygons
    polylines_u_vertical = []
    polylines_u_vertical_planes = []
    polylines_u_vertical_cuts = {}
    for i in range(len(polylines_u)):
        polyline = Polyline(polylines_u[i] + polylines_u_projected[i][::-1] )
        polylines_u_vertical.append(polyline)
        normal = Vector(0,0,1).cross(Vector(*polyline[1])-Vector(*polyline[0]))
        polylines_u_vertical_planes.append(Plane(polyline[0],normal))
        polylines_u_vertical_cuts[i] = []


    polylines_v_vertical = []
    polylines_v_vertical_planes = []
    polylines_v_vertical_cuts = {}
    for i in range(len(polylines_v)):
        polyline = Polyline(polylines_v[i] + polylines_v_projected[i][::-1] )
        polylines_v_vertical.append(polyline)
        normal = Vector(0,0,1).cross(Vector(*polyline[1])-Vector(*polyline[0]))
        polylines_v_vertical_planes.append(Plane(polyline[0],normal))
        polylines_v_vertical_cuts[i] = []

    # Intersection Polygons

    thickness = 0.1
    boolean_offset_vector = Vector(0,0,0.5)
    gap_vector = Vector(0,0,0.05)

    for i in range(len(polylines_u_vertical)):
        for j in range(len(polylines_v_vertical)):
            result = intersection_polyline_plane(polylines_u_vertical[i], polylines_v_vertical_planes[j])
            if not result:
                continue 
            if len(result) != 2:
                continue 

            if result[0][2] > result[1][2]:
                result[0], result[1] = result[1], result[0]
            
            
            p0 = Point(*result[0]) - boolean_offset_vector
            p1 = Point(*result[1]) + boolean_offset_vector

            pmid = Point((result[0][0]+result[1][0])*0.5, (result[0][1]+result[1][1])*0.5, (result[0][2]+result[1][2])*0.5)


            offset_dir = (p0-pmid).cross(polylines_u_vertical_planes[i].normal).unitized()
            print(gap_vector)
            polyline_u = Polyline([
                p0 + offset_dir * thickness*0.5,
                pmid+ offset_dir * thickness*0.5 + gap_vector*0.5,
                pmid- offset_dir * thickness*0.5+ gap_vector*0.5,
                p0- offset_dir * thickness*0.5,
            ])

            offset_dir = (p1-pmid).cross(polylines_v_vertical_planes[j].normal).unitized()
            polyline_v = Polyline([
                p1 + offset_dir * thickness*0.5,
                pmid+ offset_dir * thickness*0.5- gap_vector*0.5,
                pmid- offset_dir * thickness*0.5- gap_vector*0.5,
                p1- offset_dir * thickness*0.5,
            ])

            polylines_u_vertical_cuts[i].append(polyline_u)
            polylines_v_vertical_cuts[j].append(polyline_v)










    # Vizualization
    # for polyline in polylines_u:
    #     scene.add(Polyline(polyline))
    # for polyline in polylines_v:
    #     scene.add(Polyline(polyline))

    # for polyline in polylines_u_projected:
    #     scene.add(Polyline(polyline))
    # for polyline in polylines_v_projected:
    #     scene.add(Polyline(polyline))

    # for polyline in polylines_u_vertical:
    #     scene.add(polyline)

    # for polyline in polylines_v_vertical:
    #     scene.add(polyline)
    
    for key, value in polylines_u_vertical_cuts.items():


        a = Polygon(polylines_u_vertical[key])
        T = Transformation.from_frame_to_frame(a.frame, Frame.worldXY())
        T_I = Transformation.from_frame_to_frame(Frame.worldXY(), a.frame)
        a.transform(T)


        for o in value:
            b = Polygon(o.points)
            a = a.boolean_difference(b.transformed(T))
        
        a.transform(T_I)

        scene.add(Polyline(a.points+[a.points[0]]))


    for key, value in polylines_v_vertical_cuts.items():


        a = Polygon(polylines_v_vertical[key])
        T = Transformation.from_frame_to_frame(a.frame, Frame.worldXY())
        T_I = Transformation.from_frame_to_frame(Frame.worldXY(), a.frame)
        a.transform(T)


        for o in value:
            b = Polygon(o.points)
            a = a.boolean_difference(b.transformed(T))
        
        a.transform(T_I)
        scene.add(Polyline(a.points+[a.points[0]]))

    # for key, value in polylines_v_vertical_cuts.items():
    #     for o in value:
    #         scene.add(o)



    










    scene.add(mesh_)
    scene.add(polyline_)
    scene.add(line_)
    scene.add(aabb)





get_section_frames(mesh, polyline, line)

scene.draw()