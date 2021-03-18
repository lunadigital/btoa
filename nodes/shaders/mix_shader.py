from bpy.types import Node
from bpy.props import BoolProperty, EnumProperty

from ..base import ArnoldNode

class AiMixShader(Node, ArnoldNode):
    ''' Used to blend two shaders together. '''
    bl_label = "Mix Shader"
    bl_icon = 'MATERIAL'

    ai_name = "mix_shader"

    mode: EnumProperty(
        name="Mode",
        description="",
        items=[
            ('0', "Blend", "Blend"),
            ('1', "Add", "Add")
        ]
    )

    add_transparency: BoolProperty(
        name="Add Transparency",
        description=""
    )

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatNormalized', "Mix", identifier="mix").default_value = 0.5
        self.inputs.new('AiNodeSocketSurface', name="Shader", identifier="shader1")
        self.inputs.new('AiNodeSocketSurface', name="Shader", identifier="shader2")

        self.outputs.new('AiNodeSocketSurface', name="Closure", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")
        layout.prop(self, "add_transparency")
        
    def sub_export(self, node):
        node.set_int("mode", int(self.mode))
        node.set_bool("add_transparency", self.add_transparency)

def register():
    from bpy.utils import register_class
    register_class(AiMixShader)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(AiMixShader)