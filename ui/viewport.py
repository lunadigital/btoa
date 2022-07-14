from bpy.types import VIEW3D_HT_header

def viewport_mult_func(self, context):
    if context.scene.render.engine == 'ARNOLD':
        self.layout.prop(context.scene.arnold, "viewport_scale", text="")

def register():
    VIEW3D_HT_header.append(viewport_mult_func)

def unregister():
    VIEW3D_HT_header.remove(viewport_mult_func)