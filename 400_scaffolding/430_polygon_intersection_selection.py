#! python3
# venv: brg-csd
# compas

import compas_rhino.objects
import compas_rhino.conversions
import rhinoscriptsyntax as rs
from compas.scene import Scene
from compas.geometry import Polygon, Point, Line, Transformation, Frame, intersection_polyline_plane
from compas.datastructures import Mesh
from compas.geometry.triangulation_earclip import earclip_polygon


def get_polygon(prompt):
    """Prompt user to select a polyline and return it as a COMPAS polygon."""
    guid = compas_rhino.objects.select_object()
    obj = compas_rhino.objects.find_object(guid)
    polyline = compas_rhino.conversions.curve_to_compas_polyline(obj.Geometry)
    polygon = Polygon(polyline.points[:-1])
    return polygon


def find_common_line(poly0, poly1):
    """Find the common intersection line between two polygons."""

    points0 = intersection_polyline_plane(poly0, poly1.plane)
    points1 = intersection_polyline_plane(poly1, poly0.plane)

    if len(points0) < 2 or len(points1) < 2:
        print("No two points found.")
        return None

    line0, line1 = Line(points0[0], points0[1]), Line(points1[0], points1[1])

    if line0 == line1:
        return line0

    # Determine the common points
    common_point0 = Point(*points0[0]) if line1.closest_point(Point(*points0[0]), True)[1] > 0 else Point(*points0[1])
    common_point1 = Point(*points1[0]) if line0.closest_point(Point(*points1[0]), True)[1] > 0 else Point(*points1[1])

    return Line(common_point0, common_point1) if common_point0 and common_point1 else None


def cut_polygon(polygon, common_line, invert_height=False):
    """Cut a polygon along a rectangle defined by the common line."""
    width = 1
    height = common_line.length if invert_height else -common_line.length
    height_factor = 2 if invert_height else -2
    cut_rect = Polygon.from_rectangle(Point(-width * 0.5, height * 0.5, 0), width, abs(height) * height_factor)

    # Transform to XY plane, cut, and transform back
    origin = common_line.start if invert_height else common_line.end
    frame = Frame(origin, polygon.frame.normal.cross(common_line.vector), common_line.vector)
    transform = Transformation.from_frame_to_frame(frame, Frame.worldXY())
    polygon.transform(transform)
    polygon = polygon.boolean_difference(cut_rect)
    polygon.transform(transform.inverse())

    return polygon


# Main Execution
polygon0 = get_polygon("Select first rectangle.")
polygon1 = get_polygon("Select second rectangle.")
common_line = find_common_line(polygon0, polygon1)

if common_line:
    polygon0 = cut_polygon(polygon0, common_line, invert_height=False)
    polygon1 = cut_polygon(polygon1, common_line, invert_height=True)

    # Convert results to meshes and visualize

    mesh0 = Mesh.from_vertices_and_faces(polygon0.points, earclip_polygon(polygon0))
    mesh1 = Mesh.from_vertices_and_faces(polygon1.points, earclip_polygon(polygon1))

    scene = Scene()
    scene.add(polygon0)
    scene.add(polygon1)
    scene.add(mesh0)
    scene.add(mesh1)
    scene.add(common_line)
    scene.draw()
