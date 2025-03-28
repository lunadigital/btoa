import bpy
from bpy.app.handlers import persistent
from .utils import ops_utils

def ensure_node_tree_exists(datablock):
    if not datablock.arnold.node_tree:
        name = ops_utils.make_nodetree_name(datablock.name)
        ntree = bpy.data.node_groups.new(name=name, type='ArnoldShaderTree')
        datablock.arnold.node_tree = ntree

        if isinstance(datablock, bpy.types.Material):
            ops_utils.init_material_nodetree(ntree)
        elif isinstance(datablock, bpy.types.World):
            ops_utils.init_world_nodetree(ntree)
        
        for ob in bpy.data.objects:
            if ob.material_slots:
                for slot in ob.material_slots:
                    if datablock.name == slot.name:
                        slot.material = datablock
                        ob.update_tag()
                        datablock.update_tag()
                        return

@persistent
def initialize_shader_graphs(dummy):
    engine = bpy.context.scene.render.engine

    if engine == "ARNOLD":
        for material in bpy.data.materials:
            ensure_node_tree_exists(material)

        for world in bpy.data.worlds:
            ensure_node_tree_exists(world)

def register():
    bpy.app.handlers.depsgraph_update_pre.append(initialize_shader_graphs)

def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(initialize_shader_graphs)