import bpy

handle = object()

subscribe_to = bpy.types.RenderSettings, "engine"

def toggle_shader_editor():
    engine = bpy.context.scene.render.engine

    for workspace in bpy.data.workspaces:
        for screen in workspace.screens:
            for area in screen.areas:
                if not area.ui_type:
                    area.ui_type = 'ArnoldShaderTree' if engine == 'ARNOLD' else 'ShaderNodeTree'

def register():
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=handle,
        args=(),
        notify=toggle_shader_editor
    )

    bpy.msgbus.publish_rna(key=subscribe_to)

def unregister():
    bpy.msgbus.clear_by_owner(handle)