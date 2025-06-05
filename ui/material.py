import bpy
from bl_ui.properties_material import MaterialButtonsPanel

from . import presets
from ..preferences import ENGINE_ID
from ..utils import ui_utils

class ArnoldMaterialPanel(MaterialButtonsPanel, bpy.types.Panel):
    COMPAT_ENGINES = {ENGINE_ID}

    @classmethod
    def poll(cls, context):
        return ui_utils.arnold_is_active(context) and (context.material or context.object)

class ARNOLD_MATERIAL_PT_context_material(ArnoldMaterialPanel):
    bl_label = ""
    bl_options = {'HIDE_HEADER'}

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
            split = ui_utils.aishader_template_ID(layout, ob.active_material)
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

        if mat and not mat.arnold.node_tree:
            layout.operator("arnold.material_init", icon='NODETREE')
            return

class ARNOLD_MATERIAL_PT_surface(ArnoldMaterialPanel):
    bl_label = "Surface"

    def draw_header_preset(self, context):
        material = context.object.active_material

        if material and material.arnold:
            node = material.arnold.node_tree.get_output_node().inputs["Surface"].links[0].from_node

            if len(node.inputs) == 42: # If AiStandardSurface, or the meaning of life and everything 
                presets.ARNOLD_PT_MaterialPresets.draw_panel_header(self.layout)

    def draw(self, context):
        layout = self.layout
        mat = context.material
        
        if mat:
            layout.prop(mat, "use_nodes", icon='NODETREE')
            layout.separator()

            layout.use_property_split = True

            if mat.use_nodes:
                ui_utils.panel_node_draw(layout, mat.arnold.node_tree, 'OUTPUT_MATERIAL', "Surface")
            else:
                layout.prop(mat, "diffuse_color", text="Base Color")
                layout.prop(mat, "metallic")
                layout.prop(mat, "specular_intensity", text="Specular")
                layout.prop(mat, "roughness")

class ARNOLD_MATERIAL_PT_convert(ArnoldMaterialPanel):
    bl_label = "Convert"

    def draw(self, context):
        layout = self.layout
        mat = context.material
        
        if mat:
            #layout.use_property_split = True
            layout.label(text="Overwrites Existing Node Network", icon="ERROR")
            layout.operator("arnold.material_convert")

classes = (
    ARNOLD_MATERIAL_PT_context_material,
    ARNOLD_MATERIAL_PT_surface,
    ARNOLD_MATERIAL_PT_convert,
)

def register():
    from ..utils import register_utils as utils
    utils.register_classes(classes)

def unregister():
    from ..utils import register_utils as utils
    utils.unregister_classes(classes)