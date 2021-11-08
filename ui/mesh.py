import bpy
from bl_ui.properties_object import ObjectButtonsPanel
from .. import engine

class OBJECT_PT_arnold_shape_visibility(ObjectButtonsPanel, bpy.types.Panel):
    bl_idname = "OBJECT_PT_arnold_shape"
    bl_label = "Arnold"
    bl_parent_id = "OBJECT_PT_visibility"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}

    @classmethod
    def poll(self, context):
        return context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        ob = context.object

        layout.use_property_split = True

        layout.prop(ob.arnold, "camera")
        layout.prop(ob.arnold, "shadow")
        layout.prop(ob.arnold, "diffuse_transmission")
        layout.prop(ob.arnold, "specular_transmission")
        layout.prop(ob.arnold, "volume")
        layout.prop(ob.arnold, "diffuse_reflection")
        layout.prop(ob.arnold, "specular_reflection")
        layout.prop(ob.arnold, "sss")

classes = (
    OBJECT_PT_arnold_shape_visibility,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)