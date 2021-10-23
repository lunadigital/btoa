import bpy
from bpy.types import Node, Object
from bpy.props import BoolProperty, PointerProperty

from ..base import ArnoldNode

import math
import mathutils

class AiPhysicalSky(Node, ArnoldNode):
    '''
    This shader implements a variation of the Hosek-Wilkie sky radiance
    model, including the direct solar radiance function.
    '''
    bl_label = "Physical Sky"
    bl_icon = 'NONE'
    
    ai_name = "physical_sky"

    enable_sun: BoolProperty(name="Enable Sun", default=True)
    use_degrees: BoolProperty(name="Use Degrees", default=True)
    sun_direction: PointerProperty(name="Sun Direction", type=Object)

    def init(self, context):
        self.inputs.new('AiNodeSocketFloatPositiveToTen', "Turbidity", identifier="turbidity").default_value = 3
        self.inputs.new('AiNodeSocketRGB', "Ground Albedo", identifier="ground_albedo").default_value = (0.1, 0.1, 0.1)
        self.inputs.new('AiNodeSocketFloatHalfRotation', "Elevation", identifier="elevation").default_value = math.pi / 4 # 45deg
        self.inputs.new('AiNodeSocketFloatFullRotation', "Azimuth", identifier="azimuth").default_value = math.pi / 2 # 90deg
        self.inputs.new('AiNodeSocketFloatPositive', "Intensity", identifier="intensity").default_value = 1

        self.inputs.new('AiNodeSocketRGB', "Sky Tint", identifier="sky_tint").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketRGB', "Sun Tint", identifier="sun_tint").default_value = (1, 1, 1)
        self.inputs.new('AiNodeSocketFloatPositive', "Sun Size", identifier="sun_size").default_value = 0.51

        self.outputs.new('AiNodeSocketSurface', name="RGB", identifier="output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "enable_sun")

        layout.prop(self, "use_degrees")
        
        row = layout.row()
        row.prop(self, "sun_direction")
        row.enabled = not self.use_degrees

    def sub_export(self, node):
        node.set_bool("enable_sun", self.enable_sun)
        node.set_bool("use_degrees", self.use_degrees)
        
        if self.sun_direction:
            rot = self.sun_direction.rotation_euler.copy()

            # We need to swap the Y and Z axes, and add a quarter-turn on the X
            # axis and half turn on the new Y axis so everything lines up with
            # Blender's coordinate system
            vec = mathutils.Euler(
                (rot.x + math.radians(90), math.radians(180) - rot.z, rot.y),
                'XYZ'
                )
            
            # Get the right axis, up axis, and back axis. We only care
            # about the back axis for now.
            right, up, back = vec.to_quaternion().to_matrix().transposed()

            node.set_vector("sun_direction", *back)
            
def register():
    bpy.utils.register_class(AiPhysicalSky)

def unregister():
    bpy.utils.unregister_class(AiPhysicalSky)