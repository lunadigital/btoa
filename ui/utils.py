import bpy

''' Utility functions for UI components '''

def aishader_template_ID(layout, material):
    row = layout.row(align=True)
    row.operator('arnold.material_select', icon='MATERIAL', text="")

    if material:
        row.prop(material, "name", text="")
        if material.users > 1:
            # TODO this thing is too wide
            row.operator('arnold.material_copy', text=str(material.users))
        row.prop(material, 'use_fake_user', text="")
        row.operator('arnold.material_copy', text="", icon='DUPLICATE')
        row.operator('arnold.material_unlink', text="", icon='X')
    else:
        row.operator('arnold.material_new', text="New", icon='ADD')
    return row