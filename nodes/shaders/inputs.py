import bpy
from bpy.props import *
from .. import core
from ...bridge import FloatData, VectorData
from ...utils import register_utils

'''
AiFloat

This is a dummy node that mimics the Cycles/EEVEE "Value" node for outputing a single float value.
'''
class AiFloat(bpy.types.Node):
    bl_label = "Float"

    value: FloatProperty(name="Float")

    def init(self, context):
        self.outputs.new('AiNodeSocketFloatUnbounded', "Float")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "value", text="")
    
    # Overriding export() because this isn't a native Arnold struct
    def export(self):
        return FloatData(self.value)

'''
AiVector

This is a dummy node that outputs a 3D vector value.
'''
class AiVector(bpy.types.Node):
    bl_label = "Vector"

    value: FloatVectorProperty(name="Vector")

    def init(self, context):
        self.outputs.new('AiNodeSocketVector', "Vector")
    
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, "value", text="")
    
    # Overriding export() because this isn't a native Arnold struct
    def export(self):
        return VectorData(self.value)

classes = (
    AiFloat,
    AiVector
)

def register():
    register_utils.register_classes(classes)

def unregister():
    register_utils.unregister_classes(classes)