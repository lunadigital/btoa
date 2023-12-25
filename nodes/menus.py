import bpy
from bpy.types import Menu
from bl_ui import node_add_menu
from ..utils import ui_utils

def arnold_shader_nodes_poll(context):
    return ui_utils.arnold_is_active(context)

def arnold_object_nodes_poll(context):
    snode = context.space_data
    anode = context.scene.arnold.space_data
    return (snode.tree_type == 'ArnoldShaderTree' and
            anode.shader_type == 'OBJECT' and
            context.object.type != 'LIGHT')

def arnold_world_nodes_poll(context):
    snode = context.space_data
    anode = context.scene.arnold.space_data
    return (snode.tree_type == 'ArnoldShaderTree' and
            anode.shader_type == 'WORLD')

def object_arnold_shader_nodes_poll(context):
    return (arnold_object_nodes_poll(context) and
            arnold_shader_nodes_poll(context))

def world_arnold_shader_nodes_poll(context):
    return (arnold_world_nodes_poll(context) and
            arnold_shader_nodes_poll(context))

class NODE_MT_category_shader_color(Menu):
    bl_idname = "NODE_MT_category_shader_color"
    bl_label = "Color"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiColorCorrect", poll=arnold_shader_nodes_poll(context))
        node_add_menu.add_node_type(layout, "AiColorJitter")
        node_add_menu.add_node_type(layout, "AiComposite")
        node_add_menu.add_node_type(layout, "AiShuffle")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_category_shader_conversion(Menu):
    bl_idname = "NODE_MT_category_shader_conversion"
    bl_label = "Conversion"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiFloatToInteger")
        node_add_menu.add_node_type(layout, "AiFloatToRGB")
        node_add_menu.add_node_type(layout, "AiFloatToRGBA")
        node_add_menu.add_node_type(layout, "AiRGBToFloat")
        node_add_menu.add_node_type(layout, "AiRGBToVector")
        node_add_menu.add_node_type(layout, "AiRGBAToFloat")
        node_add_menu.add_node_type(layout, "AiVectorToRGB")
        node_add_menu.add_node_type(layout, "AiSeparateRGBA")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_category_shader_math(Menu):
    bl_idname = "NODE_MT_category_shader_math"
    bl_label = "Math"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiMultiply")
        node_add_menu.add_node_type(layout, "AiRange")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)
        
class NODE_MT_category_shader_output(Menu):
    bl_idname = "NODE_MT_category_shader_output"
    bl_label = "Output"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiShaderOutput")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_category_shader_surface(Menu):
    bl_idname = "NODE_MT_category_shader_surface"
    bl_label = "Surface"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiStandardSurface")
        node_add_menu.add_node_type(layout, "AiStandardHair")
        node_add_menu.add_node_type(layout, "AiCarPaint")
        node_add_menu.add_node_type(layout, "AiFlat")
        node_add_menu.add_node_type(layout, "AiLambert")
        node_add_menu.add_node_type(layout, "AiMixShader")
        node_add_menu.add_node_type(layout, "AiNormalMap")
        node_add_menu.add_node_type(layout, "AiDisplacement")
        node_add_menu.add_node_type(layout, "AiAmbientOcclusion")
        node_add_menu.add_node_type(layout, "AiCurvature")
        node_add_menu.add_node_type(layout, "AiTwoSided")
        node_add_menu.add_node_type(layout, "AiWireframe")
        node_add_menu.add_node_type(layout, "AiMatte")
        node_add_menu.add_node_type(layout, "AiShadowMatte")
        node_add_menu.add_node_type(layout, "AiRaySwitchRGBA")
        node_add_menu.add_node_type(layout, "AiRaySwitchShader")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_category_shader_textures(Menu):
    bl_idname = "NODE_MT_category_shader_textures"
    bl_label = "Textures"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiCellNoise")
        node_add_menu.add_node_type(layout, "AiFlakes")
        node_add_menu.add_node_type(layout, "AiImage")
        node_add_menu.add_node_type(layout, "AiLayerFloat")
        node_add_menu.add_node_type(layout, "AiLayerRGBA")
        node_add_menu.add_node_type(layout, "AiMixRGBA")
        node_add_menu.add_node_type(layout, "AiNoise")
        node_add_menu.add_node_type(layout, "AiRoundCorners")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_category_shader_utility(Menu):
    bl_idname = "NODE_MT_category_shader_utility"
    bl_label = "Utility"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiBump2d")
        node_add_menu.add_node_type(layout, "AiBump3d")
        node_add_menu.add_node_type(layout, "AiCoordSpace")
        node_add_menu.add_node_type(layout, "AiFacingRatio")
        node_add_menu.add_node_type(layout, "AiUVProjection")
        node_add_menu.add_node_type(layout, "AiFloat")
        node_add_menu.add_node_type(layout, "AiStateFloat")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_category_shader_world(Menu):
    bl_idname = "NODE_MT_category_shader_utility"
    bl_label = "Utility"

    def draw(self, context):
        layout = self.layout

        node_add_menu.add_node_type(layout, "AiSkydome")
        node_add_menu.add_node_type(layout, "AiPhysicalSky")

        node_add_menu.draw_assets_for_catalog(layout, self.bl_label)

class NODE_MT_arnold_node_add_all(Menu):
    bl_idname = "NODE_MT_arnold_node_add_all"
    bl_label = "Add"

    def draw(self, context):
        layout = self.layout

        layout.menu("NODE_MT_category_shader_output")
        layout.separator()
        layout.menu("NODE_MT_category_shader_surface")
        layout.menu("NODE_MT_category_shader_textures")
        layout.separator()
        layout.menu("NODE_MT_category_shader_color")
        layout.menu("NODE_MT_category_shader_conversion")
        layout.menu("NODE_MT_category_shader_math")
        layout.menu("NODE_MT_category_shader_utility")
        layout.separator()
        layout.menu("NODE_MT_category_shader_world")

        node_add_menu.draw_root_assets(layout)

def menu_draw(self, context):
    layout = self.layout
    snode = context.space_data
    
    if snode.tree_type == 'ArnoldShaderTree':
        layout.menu_contents("NODE_MT_arnold_node_add_all")

classes = (
    NODE_MT_category_shader_color,
    NODE_MT_category_shader_conversion,
    NODE_MT_category_shader_math,
    NODE_MT_category_shader_output,
    NODE_MT_category_shader_surface,
    NODE_MT_category_shader_textures,
    NODE_MT_category_shader_utility,
    NODE_MT_category_shader_world,
    NODE_MT_arnold_node_add_all
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    print("Setting up menus")
    bpy.types.NODE_MT_add.append(menu_draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    
    bpy.types.NODE_MT_add.remove(menu_draw)