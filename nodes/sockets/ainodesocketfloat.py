import math
from bpy.types import NodeSocket
from bpy.props import *
from .ainodesocket import AiNodeSocket, SocketColor
from ...bridge.types import FloatData

class AiNodeSocketFloat(AiNodeSocket):
    color = SocketColor.FLOAT

    def export_default(self):
        return FloatData(self.default_value)

class AiNodeSocketFloatNoSlider(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty()
    slider = False

class AiNodeSocketFloatUnbounded(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(soft_min=-1, soft_max=1)

class AiNodeSocketFloatPositive(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, soft_max=1)

class AiNodeSocketFloatPositiveSmall(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, soft_max=1, precision=3)

class AiNodeSocketFloatAboveOne(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, soft_max=1)

class AiNodeSocketFloatNormalized(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, max=1)

class AiNodeSocketFloatPositiveToTen(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, soft_max=10)

# I need a better name for this
# Covers the -1 to 1 range
class AiNodeSocketFloatNormalizedAlt(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=-1, max=1)

class AiNodeSocketUVScale(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0.00001, soft_max=2, default=1)

class AiNodeSocketUVOffset(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(soft_min=-1, soft_max=1)

# Special socket for AiPhysicalSky. It's limited to the range 0-90deg.
class AiNodeSocketFloatHalfRotation(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, max=math.pi, unit='ROTATION')

    def export_default(self):
        return FloatData(math.degrees(self.default_value))

# Special socket for AiPhysicalSky. It's limited to the range 0-360deg.
class AiNodeSocketFloatFullRotation(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, max=(math.pi * 2), unit='ROTATION')

    def export_default(self):
        return FloatData(math.degrees(self.default_value))

class AiNodeSocketSkydomeIntensity(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0, default=1)
    slider = False

class AiNodeSocketSkydomeExposure(NodeSocket, AiNodeSocketFloat):
    default_value: FloatProperty(min=0)
    slider = False

classes = (
    AiNodeSocketFloatNoSlider,
    AiNodeSocketFloatUnbounded,
    AiNodeSocketFloatPositive,
    AiNodeSocketFloatPositiveSmall,
    AiNodeSocketFloatAboveOne,
    AiNodeSocketFloatNormalized,
    AiNodeSocketFloatNormalizedAlt,
    AiNodeSocketFloatHalfRotation,
    AiNodeSocketFloatFullRotation,
    AiNodeSocketFloatPositiveToTen,
    AiNodeSocketUVOffset,
    AiNodeSocketUVScale,
    AiNodeSocketSkydomeIntensity,
    AiNodeSocketSkydomeExposure
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)