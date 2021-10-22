import bpy
from .layered_texture import AiLayeredTexture

class AiLayerFloat(AiLayeredTexture):
    ''' Combines 8 float layers linearly. Layers are applied in order (bottom to top). '''
    bl_label = "Layer Float"

    ai_name = "layer_float"

    def init(self, context):
        super().init(context)
        
        for i in range(1, 9):
            self.inputs.new('AiNodeSocketFloatUnbounded', "Layer {}".format(i), identifier="input{}".format(i))

        self.outputs.new('AiNodeSocketFloatUnbounded', name="Float", identifier="output")

def register():
    bpy.utils.register_class(AiLayerFloat)

def unregister():
    bpy.utils.unregister_class(AiLayerFloat)