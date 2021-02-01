import bpy
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty

from . import utils

class ARNOLD_OT_material_new(Operator):
    bl_idname = 'arnold.material_new'
    bl_label = "New"
    bl_description = "Create a new material and node tree"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return utils.poll_object(context)

    def execute(self, context):
        mat = bpy.data.materials.new(name="Material")
        tree_name = utils.make_nodetree_name(mat.name)
        node_tree = bpy.data.node_groups.new(name=tree_name, type='ArnoldShaderTree')
        utils.init_mat_node_tree(node_tree)
        mat.arnold.node_tree = node_tree

        ob = context.object # might need to make this context.view_layer.objects.active
        if ob.material_slots:
            ob.material_slots[ob.active_material_index].material = mat
        else:
            ob.data.materials.append(mat)
        
        # For viewport render, we have to update the object
        # because the newly created material is not yet assigned there
        ob.update_tag()

        return {'FINISHED'}
    
class ARNOLD_OT_material_unlink(Operator):
    bl_idname = "arnold.material_unlink"
    bl_label = ""
    bl_description = "Unlink data-block"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return utils.poll_object(context)
    
    def execute(self, context):
        ob = context.object # might need to make this context.view_layer.objects.active
        if ob.material_slots:
            ob.material_slots[ob.active_material_index].material = None
        return {'FINISHED'}

class ARNOLD_OT_material_copy(Operator):
    bl_idname = "arnold.material_copy"
    bl_label = "Copy"
    bl_description = "Create a copy of the material and node tree"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return utils.poll_object(context)
    
    def execute(self, context):
        current_mat = context.object.active_material # might need to make this context.view_layer.objects.active
        
        new_mat = current_mat.copy()

        current_node_tree = current_mat.arnold.node_tree

        if current_node_tree:
            new_node_tree = current_node_tree.copy()
            new_node_tree.name = utils.make_nodetree_name(new_mat.name)
            new_node_tree.use_fake_user = True

            new_mat.arnold.node_tree = new_node_tree

        context.object.active_material = new_mat # might need to make this context.view_layer.objects.active

        return {'FINISHED'}

class ARNOLD_OT_material_set(Operator):
    bl_idname = "arnold.material_set"
    bl_label = ""
    bl_description = "Assign this node tree"
    bl_options = {'UNDO'}

    material_index: IntProperty()

    @classmethod
    def poll(cls, context):
        return utils.poll_object(context)

    def execute(self, context):
        mat = bpy.data.materials[self.material_index]
        context.object.active_material = mat

        return {'FINISHED'}

class ARNOLD_OT_material_select(Operator):
    ''' Material selection dropdown with search '''
    bl_idname = "arnold.material_select"
    bl_label = ""
    bl_property = "material"

    callback_strings = []

    def callback(self, context):
        items = []

        for index, mat in enumerate(bpy.data.materials):
            name = utils.get_name_with_lib(mat)
            items.append((str(index), name, ""))

        # There is a known bug with using a callback,
        # Python must keep a reference to the strings
        # returned or Blender will misbehave or even crash.
        ARNOLD_OT_material_select.callback_strings = items

        return items
    
    material: EnumProperty(
        name="Materials",
        items=callback
    )

    @classmethod
    def poll(cls, context):
        return utils.poll_object(context)

    def execute(self, context):
        index = int(self.material)
        mat = bpy.data.materials[index]
        context.object.active_material = mat
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

classes = (
    ARNOLD_OT_material_new,
    ARNOLD_OT_material_unlink,
    ARNOLD_OT_material_copy,
    ARNOLD_OT_material_set,
    ARNOLD_OT_material_select
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)