import bpy
from bpy.types import Node

from ..base import ArnoldNodeOutput
from ... import btoa

class AiShaderOutput(Node, ArnoldNodeOutput):
    '''Output node for Arnold shaders.'''
    bl_label = "Shader Output"
    bl_icon = 'NONE'

    def init(self, context):
        super().init(context)

        self.inputs.new(type="AiNodeSocketSurface", name="Surface", identifier="surface")
        #self.inputs.new(type="NodeSocketShader", name="Volume", identifier="volume")
        self.inputs.new(type="AiNodeSocketSurface", name="Displacement", identifier="displacement")

    def draw_buttons(self, context, layout):
        parent_material = btoa.utils.get_parent_material_from_nodetree(self.id_data)

        if parent_material:
            layout.prop(parent_material, "diffuse_color", text="Viewport")
        
        layout.prop(self, "is_active", toggle=1)

    def export(self):
        return self.inputs["Surface"].export(), None, self.inputs["Displacement"].export()

    def export_surface(self):
        return self.inputs["Surface"].export()[0]

    def export_displacement(self):
        return self.inputs["Displacement"].export()
    
    def has_surface(self):
        return self.inputs["Surface"].is_linked

    def has_displacement(self):
        return self.inputs["Displacement"].is_linked

def register():
    bpy.utils.register_class(AiShaderOutput)

def unregister():
    bpy.utils.unregister_class(AiShaderOutput)