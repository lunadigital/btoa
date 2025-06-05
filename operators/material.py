import bpy
from bpy.props import IntProperty, EnumProperty

from ..utils import ops_utils

class ArnoldMaterialOperator(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return ops_utils.poll_object(context)

class ARNOLD_OT_material_new(ArnoldMaterialOperator):
    bl_idname = 'arnold.material_new'
    bl_label = "New"
    bl_description = "Create a new material and node tree"
    bl_options = {'UNDO'}

    def execute(self, context):
        mat = bpy.data.materials.new(name="Material")
        tree_name = ops_utils.make_nodetree_name(mat.name)
        node_tree = bpy.data.node_groups.new(name=tree_name, type='ArnoldShaderTree')
        
        ops_utils.init_material_nodetree(node_tree)
        mat.arnold.node_tree = node_tree
        mat.use_nodes = True

        ob = context.object # might need to make this context.view_layer.objects.active
        if ob.material_slots:
            ob.material_slots[ob.active_material_index].material = mat
        else:
            ob.data.materials.append(mat)
        
        # For viewport render, we have to update the object
        # because the newly created material is not yet assigned there
        ob.update_tag()

        return {'FINISHED'}
    
class ARNOLD_OT_material_unlink(ArnoldMaterialOperator):
    bl_idname = "arnold.material_unlink"
    bl_label = ""
    bl_description = "Unlink data-block"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        ob = context.object
        if ob.material_slots:
            ob.material_slots[ob.active_material_index].material = None
        return {'FINISHED'}

class ARNOLD_OT_material_copy(ArnoldMaterialOperator):
    bl_idname = "arnold.material_copy"
    bl_label = "Copy"
    bl_description = "Create a copy of the material and node tree"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        current_mat = context.object.active_material
        new_mat = current_mat.copy()
        current_node_tree = current_mat.arnold.node_tree

        if current_node_tree:
            new_node_tree = current_node_tree.copy()
            new_node_tree.name = ops_utils.make_nodetree_name(new_mat.name)
            new_node_tree.use_fake_user = True

            new_mat.arnold.node_tree = new_node_tree

        context.object.active_material = new_mat

        return {'FINISHED'}

class ARNOLD_OT_material_set(ArnoldMaterialOperator):
    bl_idname = "arnold.material_set"
    bl_label = ""
    bl_description = "Assign this node tree"
    bl_options = {'UNDO'}

    material_index: IntProperty()

    def execute(self, context):
        mat = bpy.data.materials[self.material_index]
        context.object.active_material = mat

        return {'FINISHED'}

class ARNOLD_OT_material_select(ArnoldMaterialOperator):
    ''' Material selection dropdown with search '''
    bl_idname = "arnold.material_select"
    bl_label = ""
    bl_property = "material"

    callback_strings = []

    def callback(self, context):
        items = []

        for index, mat in enumerate(bpy.data.materials):
            name = ops_utils.get_name_with_lib(mat)
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

    def execute(self, context):
        index = int(self.material)
        mat = bpy.data.materials[index]
        context.object.active_material = mat
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

class ARNOLD_OT_material_convert(ArnoldMaterialOperator):
    bl_idname = 'arnold.material_convert'
    bl_label = "Convert from Cycles"
    bl_description = "Convert a Cycles node network to Arnold"
    bl_options = {'UNDO'}

    nodemap = {
        "OUTPUT_MATERIAL": "AiShaderOutput",
        "BSDF_PRINCIPLED": "AiStandardSurface",
        "TEX_IMAGE": "AiImage",
        "NORMAL_MAP": "AiNormalMap",
    }

    inmap = {
        "Base Color": "base_color",
        "Metallic": "metalness",
        "Roughness": "specular_roughness",
        "IOR": "specular_IOR",
        "Alpha": "opacity",
        "Normal": "normal",
        "Weight": None,
        "Subsurface Weight": "subsurface",
        "Subsurface Radius": "subsurface_radius",
        "Subsurface Scale": "subsurface_scale",
        "Subsurface IOR": None,
        "Subsurface Anisotropy": "subsurface_anisotropy",
        "Specular IOR Level": None,
        "Specular Tint": "specular_color",
        "Anisotropic": "specular_anisotropy",
        "Anisotropic Rotation": "specular_rotation",
        "Tangent": "tangent",
        "Transmission Weight": "transmission",
        "Coat Weight": "coat",
        "Coat Roughness": "coat_roughness",
        "Coat IOR": "coat_IOR",
        "Coat Tint": "coat_color",
        "Coat Normal": "coat_normal",
        "Sheen Weight": "sheen",
        "Sheen Roughness": "sheen_roughness",
        "Sheen Tint": "sheen_color",
        "Emission Color": "emission_color",
        "Emission Strength": "emission",
        "Thin Film Thickness": "thin_film_thickness",
        "Thin Film IOR": "thin_film_IOR",
        "Displacement": "displacement",
        "Thickness": None,
        "Vector": None, # image texture vector
        "Strength": "strength", # normal map strength
        "Surface": "surface",
        "Color": "input", # Normal map color
    }

    def get_socket_value(self, socket):
        if socket.is_linked:
            return socket.links[0].from_node
        elif hasattr(socket, "default_value"):
            return socket.default_value

        return None

    def process_node(self, ntree, cycles_node, previous=None, index=0):
        # Create node
        result = ntree.nodes.new(self.nodemap[cycles_node.type])
        result.location = cycles_node.location
        
        if previous:
            ntree.links.new(result.outputs[0], previous.inputs[index])

        # Check inputs for data
        for input in cycles_node.inputs:
            value = self.get_socket_value(input)

            if isinstance(value, bpy.types.Node) and self.inmap[input.name]:
                id = self.inmap[input.name].replace("_", " ").title()
                self.process_node(ntree, value, result, result.inputs.find(id))
            
            elif value is not None:
                param = input.default_value
                
                is_vector_data = isinstance(input, (bpy.types.NodeSocketColor, bpy.types.NodeSocketVector))
                if is_vector_data:
                    param = input.default_value[0:3]
                
                if input.name == "Alpha":
                    param = [input.default_value] * 3
                
                if input.name == "Displacement":
                    param = [*input.default_value, 1]
                
                if self.inmap[input.name]:
                    result.inputs[self.inmap[input.name]].default_value = param

        # Assign non-socket data
        if isinstance(cycles_node, bpy.types.ShaderNodeTexImage):
            result.image = cycles_node.image

    def execute(self, context):
        ob = context.object
        mat = ob.material_slots[ob.active_material_index].material
        
        cycles_ntree = mat.node_tree
        arnold_ntree = mat.arnold.node_tree
        output = cycles_ntree.get_output_node("ALL")

        arnold_ntree.nodes.clear()

        self.process_node(arnold_ntree, output)

        return {'FINISHED'}

classes = (
    ARNOLD_OT_material_new,
    ARNOLD_OT_material_unlink,
    ARNOLD_OT_material_copy,
    ARNOLD_OT_material_set,
    ARNOLD_OT_material_select,
    ARNOLD_OT_material_convert,
)

def register():
    from ..utils import register_utils as utils
    utils.register_classes(classes)

def unregister():
    from ..utils import register_utils as utils
    utils.unregister_classes(classes)
