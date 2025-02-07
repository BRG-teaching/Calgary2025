#! python 3
from Rhino.NodeInCode import Components as ncc 

import Rhino

def get_meshes():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select Mesh")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh  # Filter to curves
    go.EnablePreSelect(True, True)
    go.SubObjectSelect = False
    go.DeselectAllBeforePostSelect = False
    res = go.GetMultiple(1, 0)
    
    if go.CommandResult() == Rhino.Commands.Result.Success:
        selected_meshes = [go.Object(i).Mesh() for i in range(go.ObjectCount) if go.Object(i).Mesh()]
        return selected_meshes

meshes = get_meshes()

if meshes:
    mesh = meshes[0]
    T,D,C = ncc.NodeInCodeFunctions.Kangaroo2Component_TriRemesh(mesh, None, None, None, 88, 25)
    print(D)
    Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(T[0])
    # Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(D[0])