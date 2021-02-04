from bpy.types import NodeSocket
from bpy.props import FloatVectorProperty

from . import utils

class Color:
    material = (0.39, 0.78, 0.39, 1.0)
    color_texture = (0.78, 0.78, 0.16, 1.0)
    float_texture = (0.63, 0.63, 0.63, 1.0)
    vector_texture = (0.39, 0.39, 0.78, 1.0)
    fresnel_texture = (0.33, 0.6, 0.85, 1.0)
    volume = (1.0, 0.4, 0.216, 1.0)
    mat_emission = (0.9, 0.9, 0.9, 1.0)
    mapping_2d = (0.65, 0.55, 0.75, 1.0)
    mapping_3d = (0.50, 0.25, 0.60, 1.0)
    shape = (0.0, 0.68, 0.51, 1.0)

class ArnoldNodeSocket:
    bl_label = ""

    color = (1, 1, 1, 1)

    default_type = None

    def draw_prop(self, context, layout, node, text):
        ''' This method can be overridden by subclasses as-needed '''
        layout.prop(self, "default_value", text=text, slider=self.slider)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            self.draw_prop(context, layout, node, text)
    
    def draw_color(self, context, node):
        return self.color

    def export_default(self):
        ''' Subclasses have to implement this method '''
        return None

    def export(self):
        link = utils.get_link(self)

        if link:
            return link.from_node.export()
        elif hasattr(self, "default_value"):
            return self.export_default()
        else:
            return None

class ArnoldNodeSocketSurface(NodeSocket, ArnoldNodeSocket):
    bl_label = "Surface"

    color = Color.material

    default_value: None

    def draw_prop(self, context, layout, node, text):
        row = layout.row()
        row.label(text=text)

class ArnoldNodeSocketColor(NodeSocket, ArnoldNodeSocket):
    bl_label = "Color"

    color = Color.color_texture

    default_value: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.8, 0.8, 0.8),
        min=0,
        max=1
    )

    def draw_prop(self, context, layout, node, text):
        row = layout.row()
        row.alignment = 'LEFT'
        row.label(text=text)
        row.prop(self, "default_value", text="")
    
    def export_default(self):
        return list(self.default_value), self.default_type

classes = (
    ArnoldNodeSocketSurface,
    ArnoldNodeSocketColor
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)