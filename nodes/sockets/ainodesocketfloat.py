from bpy.types import NodeSocket
from bpy.props import FloatProperty

from .ainodesocket import AiNodeSocket
from .constants import Color

class AiNodeSocketFloat(AiNodeSocket):
    default_type = 'FLOAT'
    color = Color.float_texture

    def export_default(self):
        return self.default_value, self.default_type

class AiNodeSocketFloatUnbounded(NodeSocket, AiNodeSocketFloat):
    default_value = FloatProperty()

class AiNodeSocketFloatPositive(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0)

class AiNodeSocketFloatAboveOne(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=1)

class AiNodeSocketFloatNormalized(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, max=1)

# I need a better name for this
# Covers the -1 to 1 range
class AiNodeSocketFloatNormalizedAlt(NodeSocket, AiNodeSocket):
    default_value: FloatProperty(min=-1, max=1)

classes = (
    AiNodeSocketFloatUnbounded,
    AiNodeSocketFloatPositive,
    AiNodeSocketFloatAboveOne,
    AiNodeSocketFloatNormalized,
    AiNodeSocketFloatNormalizedAlt
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)