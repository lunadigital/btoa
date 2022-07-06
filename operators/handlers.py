import bpy
from bpy.app.handlers import persistent
from . import utils

def ensure_node_tree_exists(datablock):
    if not datablock.arnold.node_tree:
        name = utils.make_nodetree_name(datablock.name)
        ntree = bpy.data.node_groups.new(name=name, type='ArnoldShaderTree')
        datablock.arnold.node_tree = ntree

        if isinstance(datablock, bpy.types.Material):
            utils.init_mat_node_tree(ntree)
        elif isinstance(datablock, bpy.types.World):
            utils.init_world_node_tree(ntree)

@persistent
def initialize_shader_graphs(dummy):
    engine = bpy.context.scene.render.engine

    if engine == "ARNOLD":
        for material in bpy.data.materials:
            ensure_node_tree_exists(material)

        for world in bpy.data.worlds:
            ensure_node_tree_exists(world)

def register():
    bpy.app.handlers.depsgraph_update_post.append(initialize_shader_graphs)

def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(initialize_shader_graphs)