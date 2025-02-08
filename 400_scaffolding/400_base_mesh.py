#! python3
# venv: brg-csd

import pathlib

import compas
from compas.scene import Scene


# =============================================================================
# Load data
# =============================================================================

IFILE = pathlib.Path(__file__).parent.parent / "data" / "dem_vault_rv_scaffolding.json"
data = compas.json_load(IFILE)
mesh = data["idos"]
blocks = data["blocks"]

# =============================================================================
# Vizualize
# =============================================================================
print(mesh)
scene = Scene()
scene.add(mesh)
# for o in blocks:
#     scene.add(o)
scene.draw()