from bl_ui.properties_material import MaterialButtonsPanel
from bpy.types import Panel

from . import utils
from . import presets
from .. import engine

class ARNOLD_MATERIAL_PT_context_material(MaterialButtonsPanel, Panel):
    COMPAT_ENGINES = {engine.ArnoldRenderEngine.bl_idname}
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return (context.material or context.object) and engine.ArnoldRenderEngine.is_active(context)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            is_sortable = len(ob.material_slots) > 1
            rows = 4 if is_sortable else 1

            row = layout.row()

            row.template_list('MATERIAL_UL_matslots', "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator('object.material_slot_add', icon='ADD', text="")
            col.operator('object.material_slot_remove', icon='REMOVE', text="")

            col.menu('MATERIAL_MT_context_menu', icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator('object.material_slot_move', icon='TRIA_UP', text="").direction = 'UP'
                col.operator('object.material_slot_move', icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator('object.material_slot_assign', text="Assign")
                row.operator('object.material_slot_select', text="Select")
                row.operator('object.material_slot_deselect', text="Deselect")
        
        split = layout.split(factor=0.65)

        if ob:
            # Note that we don't use layout.template_ID() because we can't
            # control the copy operator in that template.
            # So we mimic our own template_ID.
            split = utils.aishader_template_ID(layout, ob.active_material)
            row = split.row()

            if slot:
                row = row.row()
                icon_link = 'MESH_DATA' if slot.link == 'DATA' else 'OBJECT_DATA'
                row.prop(slot, "link", icon=icon_link, icon_only=True)
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()

        if not mat.arnold.node_tree:
            layout.operator("arnold.material_init", icon='NODETREE')
            return

class ARNOLD_MATERIAL_PT_surface(MaterialButtonsPanel, Panel):
    bl_label = "Surface"

    @classmethod
    def poll(cls, context):
        return (context.material or context.object) and engine.ArnoldRenderEngine.is_active(context)

    def draw_header_preset(self, context):
        material = context.object.active_material

        if material.arnold:
            node = material.arnold.node_tree.get_output_node().inputs["Surface"].links[0].from_node

            if len(node.inputs) == 42: # If AiStandardSurface, or the meaning of life and everything 
                presets.ARNOLD_PT_MaterialPresets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True

        mat = context.material
        if not utils.panel_node_draw(layout, mat.arnold, 'OUTPUT_MATERIAL', 'Surface'):
            layout.prop(mat, "diffuse_color")

classes = (
    ARNOLD_MATERIAL_PT_context_material,
    ARNOLD_MATERIAL_PT_surface,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)