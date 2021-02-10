from bpy.types import Node
from bpy.props import EnumProperty, BoolProperty

from ..base import ArnoldNode

from arnold import AiNodeSetInt, AiNodeSetBool

class AiWireframe(Node, ArnoldNode):
    ''' Color shader which produces a wire-frame style output (as RGB). '''
    bl_label = "Wireframe"
    bl_icon = 'MATERIAL'

    ai_name = "wireframe"

    edge_type: EnumProperty(
        name="Edge Type",
        items=[
            ('0', 'Triangles', 'Triangles'),
            ('1', 'Polygons', 'Polygons')
        ],
        default='0'
        )
    raster_space: BoolProperty(
        name="Raster Space"
        default=True
        )

    def init(self, context):
        self.inputs.new('AiNodeSocketColorRGB', "Fill Color", identifier="fill_color")
        self.inputs.new('AiNodeSocketColorRGB', "Line Color", identifier="line_color").default_value = (0, 0, 0)
        self.inputs.new('AiNodeSocketFloatPositive', "Line Width", identifier="line_width").default_value = 1

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "edge_type")
        layout.prop(self, "raster_space")

    def sub_export(self, ainode):
        AiNodeSetInt(ainode, "edge_type", int(self.edge_type))
        AiNodeSetBool(ainode, "raster_space", self.raster_space)

def register():
    from bpy.utils import register_class
    register_class(AiWireframe)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiWireframe)