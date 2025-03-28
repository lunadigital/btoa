import bpy
from bl_ui.properties_object import ObjectButtonsPanel
from ..utils import ui_utils

class ArnoldObjectPanel(ObjectButtonsPanel, bpy.types.Panel):
    @classmethod
    def poll(self, context):
        return ui_utils.arnold_is_active(context) and context.object.type == 'MESH'
    
class OBJECT_PT_arnold_shape_visibility(ArnoldObjectPanel):
    bl_parent_id = "OBJECT_PT_visibility"
    bl_label = "Arnold"
    bl_options = {'DEFAULT_CLOSED'}

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

class OBJECT_PT_arnold_subdivisions(ArnoldObjectPanel):
    bl_label = "Subdivision"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        
        layout.use_property_split = True

        layout.prop(ob.arnold, "subdiv_type")
        layout.prop(ob.arnold, "subdiv_iterations")
        layout.prop(ob.arnold, "subdiv_frustum_ignore")

class OBJECT_PT_arnold_adaptive_subdivisions(ArnoldObjectPanel):
    bl_parent_id = 'OBJECT_PT_arnold_subdivisions'
    bl_label = "Adaptive Subdivision"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        ob = context.object
        
        layout.use_property_split = True

        layout.prop(ob.arnold, "subdiv_adaptive_error")
        layout.prop(ob.arnold, "subdiv_adaptive_metric")
        layout.prop(ob.arnold, "subdiv_adaptive_space")

class OBJECT_PT_arnold_subdivisions_advanced(ArnoldObjectPanel):
    bl_parent_id = 'OBJECT_PT_arnold_subdivisions'
    bl_label = "Advanced"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        ob = context.object
        
        layout.use_property_split = True

        layout.prop(ob.arnold, "subdiv_uv_smoothing")
        layout.prop(ob.arnold, "subdiv_smooth_derivs")

classes = (
    OBJECT_PT_arnold_shape_visibility,
    OBJECT_PT_arnold_subdivisions,
    OBJECT_PT_arnold_adaptive_subdivisions,
    OBJECT_PT_arnold_subdivisions_advanced
)

def register():
    from ..utils import register_utils
    register_utils.register_classes(classes)

def unregister():
    from ..utils import register_utils
    register_utils.unregister_classes(classes)