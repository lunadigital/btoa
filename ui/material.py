from bl_ui.properties_material import MaterialButtonsPanel
from bpy.types import Panel

from . import utils
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
            rows = 1 if is_sortable else 4

            layout.template_list('MATERIAL_UL_matslots', "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = layout.column(align=True)
            col.operator('object.material_slot_add', icon='ADD', text="")
            col.operator('object.material_slot_remove', icon='REMOVE', text="")

            #col.menu('MATERIAL_MT_specials', icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator('object.material_slot_move', icon='TRIA_UP', text="").direction = 'UP'
                col.operator('object.material_slot_move', icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator('object.material_slot_assign', text="Assign")
                row.operator('object.material_slot_select', text="Select")
                row.operator('object.material_slot_deselect', text="Deselect")
            
        #split = layout.split(percentage=0.68)

        if ob:
            # Note that we don't use layout.template_ID() because we can't
            # control the copy operator in that template.
            # So we mimic our own template_ID.
            row = utils.aishader_template_ID(layout, ob.active_material)

            if slot:
                row = row.row()
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            layout.template_ID(space, "pin_id")
            layout.separator()

classes = (
    ARNOLD_MATERIAL_PT_context_material,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)