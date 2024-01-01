import bpy
from bpy.types import Menu
from bl_ui import node_add_menu
from ..utils import ui_utils

# Am I an Arnold node?
def arnold_shader_nodes_poll(context):
    return ui_utils.arnold_is_active(context)

# Am I an object/material node?
def arnold_object_nodes_poll(context):
    snode = context.space_data
    anode = context.scene.arnold.space_data
    return (snode.tree_type == 'ArnoldShaderTree' and
            anode.shader_type == 'OBJECT' and
            context.object.type != 'LIGHT')

# Am I a world node?
def arnold_world_nodes_poll(context):
    snode = context.space_data
    anode = context.scene.arnold.space_data
    return (snode.tree_type == 'ArnoldShaderTree' and
            anode.shader_type == 'WORLD')

# Show only in material shader graphs
def object_arnold_shader_nodes_poll(context):
    return (arnold_object_nodes_poll(context) and
            arnold_shader_nodes_poll(context))

# Show only in world shader graphs
def world_arnold_shader_nodes_poll(context):
    return (arnold_world_nodes_poll(context) and
            arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_color(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_color"
    bl_label = "Color"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiColorCorrect", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiColorJitter", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiComposite", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiShuffle", poll=arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_conversion(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_conversion"
    bl_label = "Convert"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiFloatToInteger", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiFloatToRGB", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiFloatToRGBA", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRGBToFloat", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRGBToVector", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRGBAToFloat", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiVectorToRGB", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiSeparateRGBA", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiSeparateXYZ", poll=arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_math(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_math"
    bl_label = "Math"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiMultiply", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRange", poll=arnold_shader_nodes_poll(context))
        
class NODE_MT_category_arnold_shader_output(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_output"
    bl_label = "Output"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiShaderOutput", poll=arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_surface(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_surface"
    bl_label = "Surface"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiStandardSurface", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiStandardHair", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiCarPaint", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiFlat", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiLambert", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiMixShader", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiNormalMap", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiDisplacement", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiAmbientOcclusion", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiCurvature", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiTwoSided", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiWireframe", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiMatte", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiShadowMatte", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRaySwitchRGBA", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRaySwitchShader", poll=arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_textures(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_textures"
    bl_label = "Textures"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiCellNoise", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiFlakes", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiImage", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiLayerFloat", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiLayerRGBA", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiMixRGBA", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiNoise", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiRoundCorners", poll=object_arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_utility(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_utility"
    bl_label = "Utility"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiBump2d", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiBump3d", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiCoordSpace", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiFacingRatio", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiUVProjection", poll=object_arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiFloat", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiStateFloat", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiStateInt", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiStateVector", poll=arnold_shader_nodes_poll(context))

class NODE_MT_category_arnold_shader_world(Menu):
    bl_idname = "NODE_MT_category_arnold_shader_world"
    bl_label = "World"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiSkydome")
        node_add_menu.add_node_type(layout, "AiPhysicalSky")

class NODE_MT_arnold_node_add_all(Menu):
    bl_idname = "NODE_MT_arnold_node_add_all"
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout

        layout.menu("NODE_MT_category_arnold_shader_output")
        layout.separator()
        layout.menu("NODE_MT_category_arnold_shader_surface")
        layout.menu("NODE_MT_category_arnold_shader_textures")

        if world_arnold_shader_nodes_poll(context):
            layout.menu("NODE_MT_category_arnold_shader_world")

        layout.separator()
        layout.menu("NODE_MT_category_arnold_shader_color")
        layout.menu("NODE_MT_category_arnold_shader_conversion")
        layout.menu("NODE_MT_category_arnold_shader_math")
        layout.menu("NODE_MT_category_arnold_shader_utility")

def menu_draw(self, context):
    layout = self.layout
    snode = context.space_data
    
    if snode.tree_type == 'ArnoldShaderTree':
        layout.menu_contents("NODE_MT_arnold_node_add_all")

classes = (
    NODE_MT_category_arnold_shader_color,
    NODE_MT_category_arnold_shader_conversion,
    NODE_MT_category_arnold_shader_math,
    NODE_MT_category_arnold_shader_output,
    NODE_MT_category_arnold_shader_surface,
    NODE_MT_category_arnold_shader_textures,
    NODE_MT_category_arnold_shader_utility,
    NODE_MT_category_arnold_shader_world,
    NODE_MT_arnold_node_add_all
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.NODE_MT_add.append(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    
    bpy.types.NODE_MT_add.remove(menu_draw)