#! python3
# venv: brg-csd

import compas_rhino
from compas.geometry import Polygon
from compas.geometry.triangulation_earclip import earclip_polygon
from compas.datastructures import Mesh
from compas.scene import Scene

#####################################################################
# Select two polygons
#####################################################################
