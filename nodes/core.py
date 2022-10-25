import bpy
from bpy.types import NodeTree, ShaderNodeTree, Node
from bpy.props import BoolProperty

from bl_ui.space_node import NODE_HT_header, NODE_MT_editor_menus
from nodeitems_utils import NodeCategory, NodeItem

from .. import btoa
from ..utils import ui_utils

class ArnoldShaderTree(ShaderNodeTree):
    bl_idname = "ArnoldShaderTree"
    bl_label = "Arnold Shader Editor"
    bl_icon = 'MATERIAL'

    _draw_header_func = None

    '''
    Custom node trees don't trigger dependency graph updates, which makes
    it hard to pass updates to the render engine when materials change. We're
    forcing a depsgraph update with a Blender property hack similar to how
    BlendLuxCore handles it. Additional reading:

    https://github.com/LuxCoreRender/BlendLuxCore/blob/master/nodes/base.py#:~:text=def%20update(self,update%3Dacknowledge_connection)
    https://developer.blender.org/T66521
    https://devtalk.blender.org/t/custom-nodes-not-showing-as-updated-in-interactive-mode/6762/2
    '''
    def update(self):
        self.refresh = True

    def reset_refresh(self, context):
        self["refresh"] = False

    refresh: bpy.props.BoolProperty(update=reset_refresh)

    @classmethod
    def poll(cls, context):
        return ui_utils.arnold_is_active(context)

    @classmethod
    def get_from_context(cls,  context):
        space_data = context.scene.arnold.space_data
        if space_data.shader_type == 'OBJECT':    
            ob = context.object

            if ob and ob.type != 'CAMERA':
                mat = ob.active_material

                if ob.active_material is not None and ob.active_material.arnold.node_tree is not None:
                    return ob.active_material.arnold.node_tree, ob.active_material, ob.active_material
        
        elif space_data.shader_type == 'WORLD':
            return context.scene.world.arnold.node_tree, context.scene.world, context.scene.world
        
        return None, None, None

    @classmethod
    def register(cls):
        if cls._draw_header_func is None:
            '''
            This is a modified version of NODE_HT_header.draw()
            We want to match Blender's default UI as closely as possible but
            tailor it to Arnold instead.
            '''
            def draw(self, context):
                if ui_utils.arnold_is_active(context):
                    layout = self.layout

                    scene = context.scene
                    snode = context.space_data
                    arnold_space_data = scene.arnold.space_data
                    snode_id = snode.id
                    id_from = snode.id_from
                    tool_settings = context.tool_settings
                    is_compositor = snode.tree_type == 'CompositorNodeTree'

                    layout.template_header()

                    if snode.tree_type == 'ArnoldShaderTree':
                        layout.prop(arnold_space_data, "shader_type", text="")
                
                        ob = context.object
                        if arnold_space_data.shader_type == 'OBJECT' and ob:
                            ob_type = ob.type

                            NODE_MT_editor_menus.draw_collapsible(context, layout)

                            layout.separator_spacer()

                            types_that_support_material = {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META',
                                                        'GPENCIL', 'VOLUME', 'HAIR', 'POINTCLOUD'}
                            # disable material slot buttons when pinned, cannot find correct slot within id_from (#36589)
                            # disable also when the selected object does not support materials
                            has_material_slots = not snode.pin and ob_type in types_that_support_material

                            if ob_type not in ('LIGHT', 'CAMERA'):
                                row = ui_utils.aishader_template_ID(layout, ob.active_material)
                                row.enabled = has_material_slots

                        if arnold_space_data.shader_type == 'WORLD':
                            NODE_MT_editor_menus.draw_collapsible(context, layout)

                            layout.separator_spacer()

                            row = ui_utils.aiworld_template_ID(layout, scene.world)
                            row.enabled = not snode.pin

                    elif snode.tree_type == 'TextureNodeTree':
                        layout.prop(snode, "texture_type", text="")

                        NODE_MT_editor_menus.draw_collapsible(context, layout)

                        if snode_id:
                            layout.prop(snode_id, "use_nodes")

                        layout.separator_spacer()

                        if id_from:
                            if snode.texture_type == 'BRUSH':
                                layout.template_ID(id_from, "texture", new="texture.new")
                            else:
                                layout.template_ID(id_from, "active_texture", new="texture.new")

                    elif snode.tree_type == 'CompositorNodeTree':

                        NODE_MT_editor_menus.draw_collapsible(context, layout)

                        if snode_id:
                            layout.prop(snode_id, "use_nodes")

                    elif snode.tree_type == 'SimulationNodeTree':
                        row = layout.row(align=True)
                        row.prop(snode, "simulation", text="")
                        row.operator("simulation.new", text="", icon='ADD')
                        simulation = snode.simulation
                        if simulation:
                            row.prop(snode.simulation, "use_fake_user", text="")

                    else:
                        # Custom node tree is edited as independent ID block
                        NODE_MT_editor_menus.draw_collapsible(context, layout)

                        layout.separator_spacer()

                        layout.template_ID(snode, "node_tree", new="node.new_node_tree")

                    # Put pin next to ID block
                    if not is_compositor:
                        layout.prop(snode, "pin", text="", emboss=False)

                    layout.separator_spacer()

                    # Put pin on the right for Compositing
                    if is_compositor:
                        layout.prop(snode, "pin", text="", emboss=False)

                    layout.operator("node.tree_path_parent", text="", icon='FILE_PARENT')

                    # Backdrop
                    if is_compositor:
                        row = layout.row(align=True)
                        row.prop(snode, "show_backdrop", toggle=True)
                        sub = row.row(align=True)
                        sub.active = snode.show_backdrop
                        sub.prop(snode, "backdrop_channels", icon_only=True, text="", expand=True)

                    # Snap
                    row = layout.row(align=True)
                    row.prop(tool_settings, "use_snap", text="")
                    row.prop(tool_settings, "snap_node_element", icon_only=True)
                    if tool_settings.snap_node_element != 'GRID':
                        row.prop(tool_settings, "snap_target", text="")
                else:
                    cls._draw_header_func(self, context)

            cls._draw_header_func = NODE_HT_header.draw
            NODE_HT_header.draw = draw
    
    @classmethod
    def unregister_draw_cb(cls):
        if cls._draw_header_func is not None:
            NODE_HT_header.draw = cls._draw_header_func
            cls._draw_header_func = None

    def get_output_node(self):
        '''
        This is supposed to be in ShaderNodeTree, but apparently 
        doesn't get implemented in subclasses because it throws an error
        '''
        for node in self.nodes:
            ntype = getattr(node, "bl_idname", None)
            if ntype == 'AiShaderOutput' and node.is_active:
                return node
        
        return None

    def export(self):
        output = self.get_output_node()
        return output.export()

    def export_active_surface(self):
        output = self.get_output_node()
        return output.export_surface()

    def export_active_displacement(self):
        output = self.get_output_node()
        return output.export_displacement()
    
    def has_surface(self):
        output = self.get_output_node()
        return output.has_surface()

    def has_displacement(self):
        output = self.get_output_node()
        return output.has_displacement()

class ArnoldNode:
    bl_icon = 'NONE'

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == ArnoldShaderTree.bl_idname

    def sub_export(self, ainode):
        '''
        Used to set custom properties in a node if available
        Must be implemented by subclasses
        '''
        pass

    def export(self):
        node = btoa.ArnoldNode(self.ai_name)

        self.sub_export(node)

        for i in self.inputs:
            socket_value, value_type, output_type = i.export()
            
            if socket_value is not None and value_type is not None:
                if value_type == 'BTNODE':
                    socket_value.link(i.identifier, node, output_type)
                else:
                    btoa.BTOA_SET_LAMBDA[value_type](node, i.identifier, socket_value)

        return node, 'BTNODE'

class ArnoldNodeOutput:
    bl_label = "Output"

    def _get_active(self):
        return not self.mute
    
    def _set_active(self, value=True):
        for node in self.id_data.nodes:
            if isinstance(node, ArnoldNodeOutput):
                node.mute = (self != node)
    
    is_active: BoolProperty(
        name="Active",
        description="Active Output",
        get=_get_active,
        set=_set_active
        )
    
    def init(self, context):
        self._set_active()
    
    def copy(self, node):
        self._set_active()

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
        surface = self.inputs["Surface"].export() if "Surface" in self.inputs.keys() else None
        volume = None # Not implemented yet
        displacement = self.inputs["Displacement"].export() if "Displacement" in self.inputs.keys() else None
        
        return surface, volume, displacement

    def export_surface(self):
        return self.inputs["Surface"].export()[0]

    def export_displacement(self):
        return self.inputs["Displacement"].export()
    
    def has_surface(self):
        return self.inputs["Surface"].is_linked

    def has_displacement(self):
        return self.inputs["Displacement"].is_linked

class ArnoldNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return ui_utils.arnold_is_active(context)

class ArnoldWorldNodeCategory(ArnoldNodeCategory):
    @classmethod
    def poll(cls, context):
        return (
            super().poll(context) and
            context.space_data.tree_type == 'ArnoldShaderTree' and
            context.scene.arnold.space_data.shader_type == 'WORLD'
        )

class ArnoldObjectNodeCategory(ArnoldNodeCategory):
    @classmethod
    def poll(cls, context):
        return (
            super().poll(context) and
            context.space_data.tree_type == 'ArnoldShaderTree' and
            context.scene.arnold.space_data.shader_type == 'OBJECT' and
            context.object.type != 'LIGHT'
        )

world_node_categories = [
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_OUTPUTS',
        "Output",
        items=[
            NodeItem("AiShaderOutput")
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_COLOR',
        "Color",
        items=[
            NodeItem("AiColorCorrect"),
            NodeItem("AiColorJitter"),
            NodeItem("AiComposite"),
            NodeItem("AiShuffle")
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_CONVERSION',
        "Conversion",
        items=[
            NodeItem("AiFloatToInteger"),
            NodeItem("AiFloatToRGB"),
            NodeItem("AiFloatToRGBA"),
            NodeItem("AiRGBToFloat"),
            NodeItem("AiRGBToVector"),
            NodeItem("AiRGBAToFloat"),
            NodeItem("AiSeparateRGBA"),
            NodeItem("AiVectorToRGB"),
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_LIGHTS',
        "Lights",
        items=[
            NodeItem("AiSkydome"),
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_MATH',
        "Math",
        items=[
            NodeItem("AiMultiply"),
            NodeItem("AiRange")
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_SURFACE',
        "Surface",
        items=[
            NodeItem("AiFlat"),
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_TEXTURES',
        "Textures",
        items=[
            NodeItem("AiCellNoise"),
            NodeItem("AiCheckerboard"),
            NodeItem("AiImage"),
            NodeItem("AiLayerFloat"),
            NodeItem("AiLayerRGBA"),
            NodeItem("AiMixRGBA"),
            NodeItem("AiNoise"),
            NodeItem("AiPhysicalSky")
        ]
    ),
    ArnoldWorldNodeCategory(
        'ARNOLD_NODES_WORLD_UTILITY',
        "Utility",
        items=[
            NodeItem("AiFloat"),
        ]
    ),
]

object_node_categories = [
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_OUTPUTS',
        "Output",
        items=[
            NodeItem("AiShaderOutput")
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_COLOR',
        "Color",
        items=[
            NodeItem("AiColorCorrect"),
            NodeItem("AiColorJitter"),
            NodeItem("AiComposite"),
            NodeItem("AiShuffle")
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_CONVERSION',
        "Conversion",
        items=[
            NodeItem("AiFloatToInteger"),
            NodeItem("AiFloatToRGB"),
            NodeItem("AiFloatToRGBA"),
            NodeItem("AiRGBToFloat"),
            NodeItem("AiRGBToVector"),
            NodeItem("AiRGBAToFloat"),
            NodeItem("AiSeparateRGBA"),
            NodeItem("AiVectorToRGB"),
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_MATH',
        "Math",
        items=[
            NodeItem("AiMultiply"),
            NodeItem("AiRange")
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_SURFACE',
        "Surface",
        items=[
            NodeItem("AiAmbientOcclusion"),
            NodeItem("AiBump2d"),
            NodeItem("AiBump3d"),
            NodeItem("AiCarPaint"),
            NodeItem("AiCurvature"),
            NodeItem("AiDisplacement"),
            NodeItem("AiFlat"),
            NodeItem("AiLambert"),
            NodeItem("AiMatte"),
            NodeItem("AiMixShader"),
            NodeItem("AiNormalMap"),
            NodeItem("AiRaySwitchRGBA"),
            NodeItem("AiRaySwitchShader"),
            NodeItem("AiShadowMatte"),
            NodeItem("AiStandardHair"),
            NodeItem("AiStandardSurface"),
            NodeItem("AiTwoSided"),
            NodeItem("AiWireframe")
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_TEXTURES',
        "Textures",
        items=[
            NodeItem("AiCellNoise"),
            NodeItem("AiCheckerboard"),
            NodeItem("AiFlakes"),
            NodeItem("AiImage"),
            NodeItem("AiLayerFloat"),
            NodeItem("AiLayerRGBA"),
            NodeItem("AiMixRGBA"),
            NodeItem("AiNoise"),
            NodeItem("AiRoundCorners")
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_UTILITY',
        "Utility",
        items=[
            NodeItem("AiCoordSpace"),
            NodeItem("AiFacingRatio"),
            NodeItem("AiUVProjection"),
            NodeItem("AiFloat"),
        ]
    ),
]

classes = (
    ArnoldShaderTree,
    AiShaderOutput,
)

def register():
    from bpy.utils import register_class
    from nodeitems_utils import register_node_categories
    for cls in classes:
        register_class(cls)

    register_node_categories('ARNOLD_WORLD_NODES', world_node_categories)
    register_node_categories('ARNOLD_OBJECT_NODES', object_node_categories)

def unregister():
    from bpy.utils import unregister_class
    from nodeitems_utils import unregister_node_categories

    ArnoldShaderTree.unregister_draw_cb()

    for cls in classes:
        unregister_class(cls)

    unregister_node_categories('ARNOLD_WORLD_NODES')
    unregister_node_categories('ARNOLD_OBJECT_NODES')