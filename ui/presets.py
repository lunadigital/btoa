import bpy

from bpy.types import Menu, Operator, Panel

from bpy_extras.node_utils import find_node_input
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel

class ARNOLD_MT_MaterialPresets(Menu):
    bl_label = "Material Presets"
    preset_subdir = 'btoa/materials'
    preset_operator = 'script.execute_preset'
    draw = Menu.draw_preset

class ARNOLD_OT_AddMaterialPreset(AddPresetBase, Operator):
    bl_idname = 'arnold.add_material_preset'
    bl_label = "Add Preset"
    preset_menu = 'ARNOLD_MT_MaterialPresets'

    def get_node_inputs():
        result = []
        
        for i in range(0, 42):
            result.append('node.inputs[' + str(i) + "].default_value")

        result.append('node.transmit_aovs')
        result.append('node.thin_walled')
        result.append('node.caustics')
        result.append('node.internal_reflections')
        result.append('node.exit_to_background')
        result.append('node.subsurface_type')

        return result

    preset_defines = [
        'node = bpy.context.object.active_material.arnold.node_tree.get_output_node().inputs["Surface"].links[0].from_node'
    ]

    preset_values = get_node_inputs()

    preset_subdir = 'btoa/materials'

class ARNOLD_PT_MaterialPresets(PresetPanel, Panel):
    bl_label = "Arnold Material Presets"
    preset_subdir = 'btoa/materials'
    preset_operator = 'script.execute_preset'
    preset_add_operator = 'arnold.add_material_preset'

classes = (
    ARNOLD_MT_MaterialPresets,
    ARNOLD_OT_AddMaterialPreset,
    ARNOLD_PT_MaterialPresets,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)