import bpy
from bpy.types import Node
from bpy.props import BoolProperty

from ..base import ArnoldNode

class AiRoundCorners(Node, ArnoldNode):
    '''
    Modifies the shading normals near edges to
    give the appearance of a round corner.
    '''
    bl_label = "Round Corners"
    bl_icon = 'NONE'
    
    ai_name = "round_corners"

    # trace_set

    inclusive: BoolProperty(name="Inclusive", default=True)
    self_only: BoolProperty(name="Self Only")
    object_space: BoolProperty(name="Object Space", default=True)

    def init(self, context):
        self.inputs.new("AiNodeSocketIntAboveOne", "Samples", identifier="samples").default_value = 6
        self.inputs.new("AiNodeSocketFloatNormalized", "Radius", identifier="radius").default_value = 0.01
        self.inputs.new("AiNodeSocketVector", "Normal", identifier="normal")
        # trace_set
        # inclusive
        # self_only
        # object_space

        self.outputs.new("AiNodeSocketVector", "Vector")

    def draw_buttons(self, context, layout):
        layout.prop(self, "inclusive")
        layout.prop(self, "self_only")
        layout.prop(self, "object_space")
    
    def sub_export(self, node):
        node.set_bool("inclusive", self.inclusive)
        node.set_bool("self_only", self.self_only)
        node.set_bool("object_space", self.object_space)
        
classes = (
    AiRoundCorners,
)
register, unregister = bpy.utils.register_classes_factory(classes)