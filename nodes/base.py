import bpy
from bpy.types import NodeTree, ShaderNodeTree
from bpy.props import BoolProperty

from bl_ui.space_node import NODE_HT_header, NODE_MT_editor_menus
from nodeitems_utils import NodeCategory, NodeItem

from .. import engine
from .. import btoa

from arnold import *

class ArnoldWorldTree(NodeTree):
    bl_idname = "ArnoldWorldTree"
    bl_label = "Arnold World"
    bl_icon = 'WORLD'

    _draw_header = None

    @classmethod
    def poll(cls, context):
        return engine.ArnoldRenderEngine.is_active(context)

    @classmethod
    def get_from_context(cls, context):
        scene = context.scene
        world = scene.world

        if scene and world:
            return (world.node_tree, world, world)
        
        return (None, None, None)
    
    @classmethod
    def register(cls):
        # Hack to show our own header UI for world nodes
        if cls._draw_header is None:
            
            def draw(self, context):
                if engine.ArnoldRenderEngine.is_active(context):
                    snode = context.space_data
                    if snode.tree_type == ArnoldWorldTree.bl_idname:
                        ########################################
                        # copied from space_node.py:36

                        layout = self.layout

                        row = layout.row(align=True)
                        row.template_header()

                        NODE_MT_editor_menus.draw_collapsible(context, layout)

                        layout.prop(snode, "tree_type", text="", expand=True)

                        # end copy
                        ########################################

                        ########################################
                        # copied from space_node.py:72

                        row = layout.row()
                        row.enabled = not snode.pin
                        row.template_ID(context.scene, "world", new="world.new")
                        if snode.id:
                            row.prop(snode.id, "use_nodes")

                        # end copy
                        ########################################

                        ########################################
                        # copied from space_node.py:113

                        layout.prop(snode, "pin", text="")
                        layout.operator("node.tree_path_parent", text="", icon="FILE_PARENT")

                        layout.separator()

                        # Auto-offset nodes
                        layout.prop(snode, "use_insert_offset", text="")

                        # Snap
                        row = layout.row(align=True)
                        row.prop(context.tool_settings, "use_snap", text="")
                        row.prop(context.tool_settings, "snap_node_element", icon_only=True)
                        if context.tool_settings.snap_node_element != 'GRID':
                            row.prop(context.tool_settings, "snap_target", text="")

                        row = layout.row(align=True)
                        row.operator("node.clipboard_copy", text="", icon='COPYDOWN')
                        row.operator("node.clipboard_paste", text="", icon='PASTEDOWN')

                        layout.template_running_jobs()

                        # end copy
                        ########################################

                        return
                cls._draw_header(self, context)

            cls._draw_header = NODE_HT_header.draw
            NODE_HT_header.draw = draw
    
    @classmethod
    def unregister_draw_cb(cls):
        if cls._draw_header is not None:
            NODE_HT_header.draw = cls._draw_header
            cls._draw_header = None

class ArnoldShaderTree(ShaderNodeTree):
    bl_idname = "ArnoldShaderTree"
    bl_label = "Arnold Shader Editor"
    bl_icon = 'MATERIAL'

    @classmethod
    def poll(cls, context):
        return engine.ArnoldRenderEngine.is_active(context)

    @classmethod
    def get_from_context(cls,  context):
        ''' Switches the displayed node tree when user selects object/material '''
        ob = context.object

        if ob and ob.type not in {'LIGHT', 'CAMERA'}:
            mat = ob.active_material

            if mat:
                node_tree = mat.arnold.node_tree

                if node_tree:
                    return node_tree, mat, mat
        
        return None, None, None

    def get_output_node(self):
        '''
        This is supposed to be in ShaderNodeTree, but apparently 
        doesn't get implemented in subclasses because it throws an error
        '''
        for node in self.nodes:
            ntype = getattr(node, "bl_idname", None)
            if ntype == 'AiShaderOutput':
                return node
        
        return None

    def export(self):
        output = self.get_output_node()
        return output.export()

class ArnoldNode:
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
        node = AiNode(self.ai_name)

        self.sub_export(node)

        for i in self.inputs:
            socket_value, value_type = i.export()
            
            if socket_value is not None and value_type is not None:
                if value_type == 'AINODE':
                    AiNodeLink(node, i.identifier, socket_value)
                else:
                    btoa.AiNodeSet[value_type](node, i.identifier, socket_value)

        return node, 'AINODE'

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

class ArnoldNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return {
            engine.ArnoldRenderEngine.is_active(context) and
            context.space_data.tree_type == 'ShaderNodeTree'
        }

class ArnoldWorldNodeCategory(ArnoldNodeCategory):
    @classmethod
    def poll(cls, context):
        return {
            engine.ArnoldRenderEngine.is_active(context) and
            context.space_data.tree_type == ArnoldWorldTree.bl_idname
        }

class ArnoldObjectNodeCategory(ArnoldNodeCategory):
    @classmethod
    def poll(cls, context):
        return (
            super().poll(context) and
            context.view_layer.objects.active.type != 'LIGHT'
        )

node_categories = [
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_OUTPUTS',
        "Output",
        items=[
            NodeItem("AiShaderOutput")
        ]
    ),
    ArnoldObjectNodeCategory(
        'ARNOLD_NODES_OBJECT_SHADERS',
        "Shader",
        items=[
            NodeItem("AiAmbientOcclusion"),
            NodeItem("AiCarPaint"),
            NodeItem("AiFlat"),
            NodeItem("AiLambert"),
            NodeItem("AiStandardSurface")
        ]
        )
]

classes = (
    ArnoldWorldTree,
    ArnoldShaderTree
)

def register():
    from bpy.utils import register_class
    from nodeitems_utils import register_node_categories
    for cls in classes:
        register_class(cls)

    register_node_categories('ARNOLD_NODES', node_categories)

def unregister():
    from bpy.utils import unregister_class
    from nodeitems_utils import unregister_node_categories
    for cls in classes:
        unregister_class(cls)

    unregister_node_categories('ARNOLD_NODES')