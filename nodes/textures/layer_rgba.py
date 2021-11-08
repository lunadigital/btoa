import bpy
from bpy.props import BoolProperty

from .layered_texture import AiLayeredTexture

class AiLayerRGBA(AiLayeredTexture):
    '''
    The layer_RGBA shader can be used to linearly layer up to eight
    shaders together, enabling you to create complex shading effects.
    Layers are applied in order (bottom to top) according to a blending
    mode specified in the operation. The layer alpha can optionally be
    a separate input. A use for this shader could include adding text
    to an image for example. 
    '''
    bl_label = "Layer RGBA"

    ai_name = "layer_rgba"

    clamp: BoolProperty(name="Clamp Result")

    def init(self, context):
        super().init(context)

        for i in range(1, 9):
            self.inputs.new('AiNodeSocketRGBA', "Layer {}".format(i), identifier="input{}".format(i))
            self.inputs.new('AiNodeSocketFloatNormalized', "Mix", identifier="mix{}".format(i))

        self.outputs.new('AiNodeSocketRGBA', name="RGBA", identifier="output")

    def template_layer_properties(self, layout, layer):
        super().template_layer_properties(layout, layer)

        col = layout.column()
        col.prop(layer, "operation")
        col.prop(layer, "alpha_operation")
        col.enabled = layer.enabled

    def draw_buttons(self, context, layout):
        super().draw_buttons(context, layout)

        layout.separator()
        layout.prop(self, "clamp")
        layout.separator()

    def sub_export(self, node):
        super().sub_export(node)

        for layer, i in zip(self.layers, range(1, 9)):
            node.set_string("operation{}".format(i), layer.operation)
            node.set_string("alpha_operation{}".format(i), layer.alpha_operation)
            
def register():
    bpy.utils.register_class(AiLayerRGBA)

def unregister():
    bpy.utils.unregister_class(AiLayerRGBA)