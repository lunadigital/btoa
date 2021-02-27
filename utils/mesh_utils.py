import bmesh

def bake_mesh(ob):
    mesh = ob.to_mesh()

    # Create a blank UV map if none exist
    if len(mesh.uv_layers) == 0:
        mesh.uv_layers.new(name='UVMap')

    # Triangulate mesh to remove ngons
    bm = bmesh.new()
    bm.from_mesh(mesh)

    bmesh.ops.triangulate(bm, faces=bm.faces[:])

    bm.to_mesh(mesh)
    bm.free()

    # Calculate normals and return
    try:
        mesh.calc_tangents()
        return mesh
    except:
        return None