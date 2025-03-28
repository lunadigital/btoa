import bpy
from bl_ui.properties_world import WorldButtonsPanel
from ..preferences import ENGINE_ID
from ..utils import ui_utils

class ArnoldWorldPanel(WorldButtonsPanel, bpy.types.Panel):
    COMPAT_ENGINES = {ENGINE_ID}

class ARNOLD_WORLD_PT_context_world(ArnoldWorldPanel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        world = context.world
        space = context.space_data

        if scene:
            row = ui_utils.aiworld_template_ID(layout, context.scene.world)
        elif world:
            layout.template_ID(space, "pin_id")

        if not world.arnold.node_tree:
            layout.operator("arnold.world_init", icon='NODETREE')

class ARNOLD_WORLD_PT_surface(ArnoldWorldPanel):
    bl_label = "Surface"

    def draw(self, context):
        layout = self.layout
        world = context.world
        
        layout.prop(world, "use_nodes", icon='NODETREE')
        layout.separator()

        layout.use_property_split = True

        if world.use_nodes:
            ui_utils.panel_node_draw(layout, world.arnold.node_tree, 'OUTPUT_WORLD', "Surface")
        else:
            layout.prop(world, "color", text="Color")

class ARNOLD_WORLD_PT_shadows(ArnoldWorldPanel):
    bl_idname = "ARNOLD_WORLD_PT_shadows"
    bl_label = "Shadows"

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        data = world.arnold.data

        layout.use_property_split = True

        if world.arnold.node_tree:
            col = layout.column()
            col.prop(data, "shadow_color")
            col.prop(data, "shadow_density")

            col.separator()

            col.prop(data, "cast_shadows")
            col.prop(data, "cast_volumetric_shadows")

class ARNOLD_WORLD_PT_advanced(ArnoldWorldPanel):
    bl_idname = "ARNOLD_WORLD_PT_advanced"
    bl_label = "Advanced"

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        data = world.arnold.data

        layout.use_property_split = True

        if world.arnold.node_tree:
            col = layout.column()
            col.prop(data, "samples")
            col.prop(data, "normalize")

class ARNOLD_WORLD_PT_visibility(ArnoldWorldPanel):
    bl_idname = "ARNOLD_WORLD_PT_visibility"
    bl_label = "Visibility"

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        data = world.arnold.data

        layout.use_property_split = True

        if world.arnold.node_tree:
            col = layout.column()
            col.prop(data, "camera")
            col.prop(data, "diffuse")
            col.prop(data, "specular")
            col.prop(data, "transmission")
            col.prop(data, "sss")
            col.prop(data, "indirect")
            col.prop(data, "volume")
            col.prop(data, "max_bounces")

classes = (
    ARNOLD_WORLD_PT_context_world,
    ARNOLD_WORLD_PT_surface,
    ARNOLD_WORLD_PT_shadows,
    ARNOLD_WORLD_PT_advanced,
    ARNOLD_WORLD_PT_visibility
)

def register():
    from ..utils import register_utils as utils
    utils.register_classes(classes)

def unregister():
    from ..utils import register_utils as utils
    utils.unregister_classes(classes)