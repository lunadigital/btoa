import bpy
from bl_ui.properties_world import WorldButtonsPanel
from bpy.types import Panel

from . import utils
from .. import engine

class ARNOLD_WORLD_PT_context_world(WorldButtonsPanel, Panel):
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return engine.ArnoldRenderEngine.is_active(context)

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        world = context.world
        space = context.space_data

        if scene:
            row = utils.aiworld_template_ID(layout, context.scene.world)
        elif world:
            layout.template_ID(space, "pin_id")

        if world.arnold.node_tree is None:
            layout.operator("arnold.world_init")

class ARNOLD_WORLD_PT_shadows(WorldButtonsPanel, bpy.types.Panel):
    bl_idname = "ARNOLD_WORLD_PT_shadows"
    bl_label = "Shadows"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        data = world.arnold.data

        layout.use_property_split = True

        if world.arnold.node_tree is not None:
            col = layout.column()
            col.prop(data, "shadow_color")
            col.prop(data, "shadow_density")

            col.separator()

            col.prop(data, "cast_shadows")
            col.prop(data, "cast_volumetric_shadows")

class ARNOLD_WORLD_PT_advanced(WorldButtonsPanel, bpy.types.Panel):
    bl_idname = "ARNOLD_WORLD_PT_advanced"
    bl_label = "Advanced"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        data = world.arnold.data

        layout.use_property_split = True

        if world.arnold.node_tree is not None:
            col = layout.column()
            col.prop(data, "samples")
            col.prop(data, "normalize")

class ARNOLD_WORLD_PT_visibility(WorldButtonsPanel, bpy.types.Panel):
    bl_idname = "ARNOLD_WORLD_PT_visibility"
    bl_label = "Visibility"
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    def draw(self, context):
        layout = self.layout
        world = context.scene.world
        data = world.arnold.data

        layout.use_property_split = True

        if world.arnold.node_tree is not None:
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
    ARNOLD_WORLD_PT_shadows,
    ARNOLD_WORLD_PT_advanced,
    ARNOLD_WORLD_PT_visibility
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)