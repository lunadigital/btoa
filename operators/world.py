import bpy
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty

from . import utils

class ARNOLD_OT_world_new(Operator):
    bl_idname = 'arnold.world_new'
    bl_label = "New"
    bl_description = "Create a new world and node tree"
    bl_options = {'UNDO'}

    def execute(self, context):
        world = bpy.data.worlds.new(name="World")
        tree_name = utils.make_nodetree_name(world.name)
        node_tree = bpy.data.node_groups.new(name=tree_name, type='ArnoldShaderTree')
        
        utils.init_world_node_tree(node_tree)
        world.arnold.node_tree = node_tree

        context.scene.world = world

        return {'FINISHED'}

class ARNOLD_OT_world_init(Operator):
    bl_idname = 'arnold.world_init'
    bl_label = "Initialize Arnold Nodes"
    bl_description = "Initializes an Arnold node tree on an existing world"
    bl_options = {'UNDO'}

    def execute(self, context):
        world = context.scene.world
        tree_name = utils.make_nodetree_name(world.name)
        node_tree = bpy.data.node_groups.new(name=tree_name, type='ArnoldShaderTree')
        
        utils.init_world_node_tree(node_tree)
        world.arnold.node_tree = node_tree

        return {'FINISHED'}

class ARNOLD_OT_world_unlink(Operator):
    bl_idname = "arnold.world_unlink"
    bl_label = ""
    bl_description = "Unlink data-block"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        context.scene.world = None
        return {'FINISHED'}

class ARNOLD_OT_world_copy(Operator):
    bl_idname = "arnold.world_copy"
    bl_label = "Copy"
    bl_description = "Create a copy of the world and node tree"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        current_world = context.scene.world
        
        new_world = current_world.copy()

        current_node_tree = current_world.arnold.node_tree

        if current_node_tree:
            new_node_tree = current_node_tree.copy()
            new_node_tree.name = utils.make_nodetree_name(new_world.name)
            new_node_tree.use_fake_user = True

            new_world.arnold.node_tree = new_node_tree

        context.scene.world = new_world

        return {'FINISHED'}

class ARNOLD_OT_world_select(Operator):
    ''' World selection dropdown with search '''
    bl_idname = "arnold.world_select"
    bl_label = ""
    bl_property = "world"

    callback_strings = []

    def callback(self, context):
        items = []

        for index, world in enumerate(bpy.data.worlds):
            print(index, world)
            name = utils.get_name_with_lib(world)
            items.append((str(index), name, ""))

        # There is a known bug with using a callback,
        # Python must keep a reference to the strings
        # returned or Blender will misbehave or even crash.
        ARNOLD_OT_world_select.callback_strings = items

        return items
    
    worlds: EnumProperty(
        name="Worlds",
        items=callback
    )

    def execute(self, context):
        index = int(self.worlds)
        world = bpy.data.worlds[index]
        context.scene.world = world
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

classes = (
    ARNOLD_OT_world_new,
    ARNOLD_OT_world_init,
    ARNOLD_OT_world_unlink,
    ARNOLD_OT_world_copy,
    ARNOLD_OT_world_select
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)