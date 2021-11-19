import bpy
from bpy_extras.node_utils import find_node_input

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

def aiworld_template_ID(layout, world):
    row = layout.row(align=True)
    row.operator('arnold.world_select', icon='WORLD', text="")

    if world:
        row.prop(world, "name", text="")
        row.prop(world, 'use_fake_user', text="")
        row.operator('arnold.world_copy', text="", icon='DUPLICATE')
        row.operator('arnold.world_unlink', text="", icon='X')
    else:
        row.operator('arnold.world_new', text="New", icon='ADD')
    return row

def panel_node_draw(layout, id_data, output_type, input_name):
    #if not id_data.use_nodes:
    #    layout.operator("cycles.use_shading_nodes", icon='NODETREE')
    #    return False

    ntree = id_data.node_tree

    if ntree is not None:
        node = ntree.get_output_node()
        if node:
            input = find_node_input(node, input_name)
            if input:
                layout.template_node_view(ntree, node, input)
            else:
                layout.label(text="Incompatible output node")
        else:
            layout.label(text="No output node")

        return True
    
    return False