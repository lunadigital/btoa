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

classes = (
    ARNOLD_WORLD_PT_context_world,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)