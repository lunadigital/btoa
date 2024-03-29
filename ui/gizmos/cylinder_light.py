import bpy
from bpy.types import Gizmo, GizmoGroup
from mathutils import Matrix

cylinder_light_shape = (
    # Horizontal lines
    (0, -1, 1), (0, 1, 1),
    (0, -1, -1), (0, 1, -1),
    # Back-left arc
    (-1, -1, 0), (-0.980785, -1, 0.195091),
    (-0.980785, -1, 0.195091), (-0.923879, -1, 0.382684),
    (-0.923879, -1, 0.382684), (-0.831469, -1, 0.555571),
    (-0.831469, -1, 0.555571), (-0.707106, -1, 0.707107),
    (-0.707106, -1, 0.707107), (-0.55557, -1, 0.83147),
    (-0.55557, -1, 0.83147), (-0.382683, -1, 0.92388),
    (-0.382683, -1, 0.92388), (-0.195089, -1, 0.980786),
    (-0.195089, -1, 0.980786), (0, -1, 1),
    # Back-right arc
    (1, -1, 0), (0.980785, -1, 0.195091),
    (0.980785, -1, 0.195091), (0.923879, -1, 0.382684),
    (0.923879, -1, 0.382684), (0.831469, -1, 0.555571),
    (0.831469, -1, 0.555571), (0.707106, -1, 0.707107),
    (0.707106, -1, 0.707107), (0.55557, -1, 0.83147),
    (0.55557, -1, 0.83147), (0.382683, -1, 0.92388),
    (0.382683, -1, 0.92388), (0.195089, -1, 0.980786),
    (0.195089, -1, 0.980786), (0, -1, 1),
    # Front-left arc
    (-1, 1, 0), (-0.980785, 1, 0.195091),
    (-0.980785, 1, 0.195091), (-0.923879, 1, 0.382684),
    (-0.923879, 1, 0.382684), (-0.831469, 1, 0.555571),
    (-0.831469, 1, 0.555571), (-0.707106, 1, 0.707107),
    (-0.707106, 1, 0.707107), (-0.55557, 1, 0.83147),
    (-0.55557, 1, 0.83147), (-0.382683, 1, 0.92388),
    (-0.382683, 1, 0.92388), (-0.195089, 1, 0.980786),
    (-0.195089, 1, 0.980786), (0, 1, 1),
    # Front-right arc
    (1, 1, 0), (0.980785, 1, 0.195091),
    (0.980785, 1, 0.195091), (0.923879, 1, 0.382684),
    (0.923879, 1, 0.382684), (0.831469, 1, 0.555571),
    (0.831469, 1, 0.555571), (0.707106, 1, 0.707107),
    (0.707106, 1, 0.707107), (0.55557, 1, 0.83147),
    (0.55557, 1, 0.83147), (0.382683, 1, 0.92388),
    (0.382683, 1, 0.92388), (0.195089, 1, 0.980786),
    (0.195089, 1, 0.980786), (0, 1, 1),
    # Back-left arc mirrored
    (-1, -1, 0), (-0.980785, -1, -0.195091),
    (-0.980785, -1, -0.195091), (-0.923879, -1, -0.382684),
    (-0.923879, -1, -0.382684), (-0.831469, -1, -0.555571),
    (-0.831469, -1, -0.555571), (-0.707106, -1, -0.707107),
    (-0.707106, -1, -0.707107), (-0.55557, -1, -0.83147),
    (-0.55557, -1, -0.83147), (-0.382683, -1, -0.92388),
    (-0.382683, -1, -0.92388), (-0.195089, -1, -0.980786),
    (-0.195089, -1, -0.980786), (0, -1, -1),
    # Back-right arc mirrored
    (1, -1, 0), (0.980785, -1, -0.195091),
    (0.980785, -1, -0.195091), (0.923879, -1, -0.382684),
    (0.923879, -1, -0.382684), (0.831469, -1, -0.555571),
    (0.831469, -1, -0.555571), (0.707106, -1, -0.707107),
    (0.707106, -1, -0.707107), (0.55557, -1, -0.83147),
    (0.55557, -1, -0.83147), (0.382683, -1, -0.92388),
    (0.382683, -1, -0.92388), (0.195089, -1, -0.980786),
    (0.195089, -1, -0.980786), (0, -1, -1),
    # Front-left arc mirrored
    (-1, 1, 0), (-0.980785, 1, -0.195091),
    (-0.980785, 1, -0.195091), (-0.923879, 1, -0.382684),
    (-0.923879, 1, -0.382684), (-0.831469, 1, -0.555571),
    (-0.831469, 1, -0.555571), (-0.707106, 1, -0.707107),
    (-0.707106, 1, -0.707107), (-0.55557, 1, -0.83147),
    (-0.55557, 1, -0.83147), (-0.382683, 1, -0.92388),
    (-0.382683, 1, -0.92388), (-0.195089, 1, -0.980786),
    (-0.195089, 1, -0.980786), (0, 1, -1),
    # Front-right arc mirrored
    (1, 1, 0), (0.980785, 1, -0.195091),
    (0.980785, 1, -0.195091), (0.923879, 1, -0.382684),
    (0.923879, 1, -0.382684), (0.831469, 1, -0.555571),
    (0.831469, 1, -0.555571), (0.707106, 1, -0.707107),
    (0.707106, 1, -0.707107), (0.55557, 1, -0.83147),
    (0.55557, 1, -0.83147), (0.382683, 1, -0.92388),
    (0.382683, 1, -0.92388), (0.195089, 1, -0.980786),
    (0.195089, 1, -0.980786), (0, 1, -1),
)

class AiCylinderLightWidget(Gizmo):
    bl_idname = "VIEW3D_GT_auto_facemap"
    
    def update_gizmo_matrix(self, context):
        light = context.object
        data = light.data

        # Gizmo scale is dependent on UI scale
        ui_scale = context.preferences.system.ui_scale
        r = data.size / ui_scale * 0.5
        s = (light.scale.y * data.size_y) / ui_scale * 0.5
        
        smatrix = Matrix.Diagonal([r, s, r]).to_4x4()
        self.matrix_offset = smatrix

    def draw(self, context):
        self.update_gizmo_matrix(context)
        self.draw_custom_shape(self.custom_shape)

    def setup(self):
        if not hasattr(self, "custom_shape"):
            self.custom_shape = self.new_custom_shape('LINES', cylinder_light_shape)

    def exit(self, context, cancel):
        context.area.header_text_set(None)
        if cancel:
            pass

class AiCylinderLightWidgetGroup(GizmoGroup):
    bl_idname = "OBJECT_GGT_cylinder_light"
    bl_label = "Cylinder Light Widget"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT', 'SCALE'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return (ob and ob.type == 'LIGHT' and ob.data.type and ob.data.type == 'AREA' and ob.data.shape and ob.data.shape == 'RECTANGLE' and context.engine == 'ARNOLD')

    def setup(self, context):
        ob = context.object
        mpr = self.gizmos.new(AiCylinderLightWidget.bl_idname)

        mpr.color = 0.0, 0.0, 0.0
        mpr.alpha = 1

        self.energy_widget = mpr

    def refresh(self, context):
        ob = context.object
        mpr = self.energy_widget
        mpr.matrix_basis = ob.matrix_world.normalized()

classes = (
    AiCylinderLightWidget,
    AiCylinderLightWidgetGroup
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)