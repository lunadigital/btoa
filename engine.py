import bpy
import bgl
import numpy
import os
from ctypes import *

from bl_ui.properties_render import RENDER_PT_color_management

from . import btoa

class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True

    def __init__(self):
        self.scene_data = None
        self.draw_data = None

        btoa.start_session()

    def __del__(self):
        btoa.end_session()

    @classmethod
    def is_active(cls, context):
        return context.scene.render.engine == cls.bl_idname

    def is_visible(self, ob):
        visible = False

        # If object is in a visible collection, set
        # visibility to true
        for collection in ob.users_collection:
            if not collection.hide_render:
                visible = True
                break
        
        # If in a visible collection, set visibility with
        # object-level settings
        if visible:
            visible = not ob.hide_render

        return visible

    def update_arnold_options(self, scene, depsgraph):
        options = btoa.Options()
        bl_options = scene.arnold_options

        # Update render resolution
        options.set_int("xres", self.size_x)
        options.set_int("yres", self.size_y)

        # Update camera node
        camera_node = btoa.get_node_by_name(scene.camera.name)
        if camera_node is None: 
            # TODO: Replace with btoa equivalent
            camera_node = btoa.generate_aicamera(scene.camera, depsgraph)
        else:
            # TODO: Replace with btoa equivalent
            btoa.sync_cameras(camera_node, scene.camera, depsgraph)
        
        options.set_pointer("camera", camera_node)

        # Update sampling settings
        options.set_int("AA_samples", bl_options.aa_samples)
        options.set_int("GI_diffuse_samples", bl_options.diffuse_samples)
        options.set_int("GI_specular_samples", bl_options.specular_samples)
        options.set_int("GI_transmission_samples", bl_options.transmission_samples)
        options.set_int("GI_sss_samples", bl_options.sss_samples)
        options.set_int("GI_volume_samples", bl_options.volume_samples)
        options.set_float("AA_sample_clamp", bl_options.sample_clamp)
        options.set_bool("AA_sample_clamp_affects_aovs", bl_options.clamp_aovs)
        options.set_float("indirect_sample_clamp", bl_options.indirect_sample_clamp)
        options.set_float("low_light_threshold", bl_options.low_light_threshold)

        if bl_options.aa_seed > 0:
            options.set_int("AA_seed", bl_options.aa_seed)

        # Update ray depth settings
        AiNodeSetInt(options, "GI_total_depth", bl_options.total_depth)
        AiNodeSetInt(options, "GI_diffuse_depth", bl_options.diffuse_depth)
        AiNodeSetInt(options, "GI_specular_depth", bl_options.specular_depth)
        AiNodeSetInt(options, "GI_transmission_depth", bl_options.transmission_depth)
        AiNodeSetInt(options, "GI_volume_depth", bl_options.volume_depth)
        AiNodeSetInt(options, "auto_transparency_depth", bl_options.transparency_depth)

        # Render settings
        AiNodeSetInt(options, "bucket_size", bl_options.bucket_size)
        AiNodeSetStr(options, "bucket_scanning", bl_options.bucket_scanning)
        AiNodeSetBool(options, "parallel_node_init", bl_options.parallel_node_init)
        AiNodeSetInt(options, "threads", bl_options.threads)

    def update(self, data, depsgraph):
        scene = depsgraph.scene
        self.set_render_size(scene)

        self.update_arnold_options(scene, depsgraph)

        for mat in data.materials:
            if (
                AiNodeLookUpByName(mat.name) is None and
                mat.name != "Dots Stroke" and
                mat.arnold.node_tree is not None
            ):
                snode, vnode, dnode = mat.arnold.node_tree.export()
                AiNodeSetStr(snode[0], "name", mat.name)
  
        for dup in depsgraph.object_instances:
            if dup.is_instance:
                ob = dup.instance_object
            else:
                ob = dup.object

            if ob.type in btoa.BL_CONVERTIBLE_TYPES:
                node = AiNodeLookUpByName(ob.name)
                if node is None:
                    node = btoa.generate_aipolymesh(ob)

                # Run as long as node is not None (ie, as long as it's a valid AiPolyMesh object)
                if node is not None and len(ob.data.materials) > 0 and ob.data.materials[0] is not None:
                    mat_node = AiNodeLookUpByName(ob.data.materials[0].name)
                    AiNodeSetPtr(node, "shader", mat_node)
            
            # Update lights
            if ob.type == 'LIGHT':
                node = AiNodeLookUpByName(ob.name)

                if node is None:
                    node = btoa.generate_ailight(ob)

                # If existing AiNode is an area light, but doesn't match the type in Blender
                elif AiNodeIs(node, "quad_light") or AiNodeIs(node, "disk_light") or AiNodeIs(node, "cylinder_light"):
                    if not AiNodeIs(node, btoa.AI_AREALIGHT_TYPE[ob.data.type]):
                        AiNodeDestroy(node)
                        node = btoa.generate_ailight(ob)

                # If existing AiNode is a non-area light type, but doesn't match the type in Blender
                elif not AiNodeIs(node, btoa.AI_LIGHT_TYPE[ob.data.type]):
                    AiNodeDestroy(node)
                    node = btoa.generate_ailight(ob)

                # If AiNode exists and same type, just update params
                else:
                    btoa.sync_light(node, ob)

        filter = AiNode("gaussian_filter")
        AiNodeSetStr(filter, "name", "gaussianFilter")

        options = AiUniverseGetOptions()

        outputs = AiArrayAllocate(1, 1, AI_TYPE_STRING)
        AiArraySetStr(outputs, 0, "RGBA RGBA gaussianFilter __display_driver")
        AiNodeSetArray(options, "outputs", outputs)

        color_manager = AiNode("color_manager_ocio")
        AiNodeSetStr(color_manager, "config", os.getenv("OCIO"))
        AiNodeSetPtr(options, "color_manager", color_manager)

    def render(self, depsgraph):
        engine = self
        _htiles = {}
        
        def display_callback(x, y, width, height, buffer, data):
            if buffer:
                try:
                    result = _htiles.pop((x, y), None)
                    
                    if result is None:
                        result = engine.begin_result(x, engine.size_y - y - height, width, height)
                    
                    _buffer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
                    rect = numpy.ctypeslib.as_array(_buffer, shape=(width * height, 4))
                    
                    result.layers[0].passes["Combined"].rect = rect
                    engine.end_result(result)
                finally:
                    AiFree(buffer)
            else:
                result = engine.begin_result(x, engine.size_y - y - height, width, height)
                _htiles[(x, y)] = result
            
            if engine.test_break():
                AiRenderAbort()
                while _htiles:
                    (x, y), result = _htiles.popitem()
                    engine.end_result(result, cancel=True)

        cb = btoa.AtDisplayCallback(display_callback)
        
        displayNode = AiNodeLookUpByName("__display_driver")
        if displayNode is None:
            displayNode = AiNode("driver_display_callback")
            AiNodeSetStr(displayNode, "name", "__display_driver")
        
        AiNodeSetPtr(displayNode, "callback", cb)

        AiRender(AI_RENDER_MODE_CAMERA)

        # Fill the render result with a flat color for now.
        # This is where we will make all of our Arnold calls
        # in the future.
        '''if self.is_preview:
            color = [0.1, 0.2, 0.1, 1.0]
        else:
            color = [0.2, 0.1, 0.1, 1.0]

        pixel_count = self.size_x * self.size_y
        rect = [color] * pixel_count

        # Write pixels to RenderResult
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = rect
        self.end_result(result)'''

    def view_update(self, context, depsgraph):
        region = context.region
        view3d = context.space_data
        scene = depsgraph.scene

        dimensions = region.width, region.height

        if not self.scene_data:
            # Assume first-time initialization
            self.scene_data = []
            first_time = True

            # Loop over all datablocks in scene
            for datablock in depsgraph.ids:
                pass
        else:
            first_time = False

            for update in depsgraph.updates:
                print("Datablock updated: ", update.id.name)
            
            if depsgraph.id_type_updated('MATERIAL'):
                print("Materials updated")
            
        if first_time or depsgraph.id_type_updated('OBJECT'):
            for instance in depsgraph.object_instances:
                pass

    def view_draw(self, context, depsgraph):
        region = context.region
        scene = depsgraph.scene

        dimensions = region.width, region.height

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_ONE, bgl.GL_ONE_MINUS_SRC_ALPHA)
        self.bind_display_space_shader(scene)

        if not self.draw_data or self.draw_data.dimensions != dimensions:
            self.draw_data = ArnoldDrawData(dimensions)
        
        self.draw_data.draw()

        self.unbind_display_space_shader()
        bgl.glDisable(bgl.GL_BLEND)
    
    def set_render_size(self, scene):
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

class ArnoldDrawData:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        width, height = dimensions

        pixels = [0.1, 0.2, 0.1, 1.0] * width * height
        pixels = bgl.Buffer(bgl.GL_FLOAT, width * height * 4, pixels)

        self.texture = bgl.Buffer(bgl.GL_INT, 1)

        bgl.glGenTextures(1, self.texture)
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.texture[0])
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA16F, width, height, 0, bgl.GL_RGBA, bgl.GL_FLOAT, pixels)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

        shader_program = bgl.Buffer(bgl.GL_INT, 1)
        bgl.glGetIntegerv(bgl.GL_CURRENT_PROGRAM, shader_program)

        self.vertex_array = bgl.Buffer(bgl.GL_INT, 1)
        bgl.glGenVertexArrays(1, self.vertex_array)
        bgl.glBindVertexArray(self.vertex_array[0])

        texturecoord_location = bgl.glGetAttribLocation(shader_program[0], "texCoord")
        position_location = bgl.glGetAttribLocation(shader_program[0], "pos")

        bgl.glEnableVertexAttribArray(texturecoord_location)
        bgl.glEnableVertexAttribArray(position_location)

        position = [0.0, 0.0, width, 0.0, width, height, 0.0, height]
        position = bgl.Buffer(bgl.GL_FLOAT, len(position), position)
        texcoord = [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]
        texcoord = bgl.Buffer(bgl.GL_FLOAT, len(texcoord), texcoord)

        self.vertex_buffer = bgl.Buffer(bgl.GL_INT, 2)
        
        bgl.glGenBuffers(2, self.vertex_buffer)
        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vertex_buffer[0])
        bgl.glBufferData(bgl.GL_ARRAY_BUFFER, 32, position, bgl.GL_STATIC_DRAW)
        bgl.glVertexAttribPointer(position_location, 2, bgl.GL_FLOAT, bgl.GL_FALSE, 0, None)

        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, self.vertex_buffer[1])
        bgl.glBufferData(bgl.GL_ARRAY_BUFFER, 32, texcoord, bgl.GL_STATIC_DRAW)
        bgl.glVertexAttribPointer(texturecoord_location, 2, bgl.GL_FLOAT, bgl.GL_FALSE, 0, None)

        bgl.glBindBuffer(bgl.GL_ARRAY_BUFFER, 0)
        bgl.glBindVertexArray(0)

    def __del__(self):
        bgl.glDeleteBuffers(2, self.vertex_buffer)
        bgl.glDeleteVertexArrays(1, self.vertex_array)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
        bgl.glDeleteTextures(1, self.texture)

    def draw(self):
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.texture[0])
        bgl.glBindVertexArray(self.vertex_array[0])
        bgl.glDrawArrays(bgl.GL_TRIANGLE_FAN, 0, 4)
        bgl.glBindVertexArray(0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

def get_panels():
    exclude_panels = {
        'RENDER_PT_gpencil',
        'RENDER_PT_simplify',
        'RENDER_PT_freestyle',
        'RENDER_PT_stereoscopy',
        'DATA_PT_light',
        'DATA_PT_preview',
        'DATA_PT_EEVEE_light',
        'DATA_PT_area',
        'DATA_PT_spot',
        'DATA_pt_context_light',
        'DATA_PT_lens',
        'DATA_PT_camera',
        'DATA_PT_camera_safe_areas',
        'DATA_PT_camera_background_image',
        'DATA_PT_camera_display',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels

gpencil_poll = None

@classmethod
def gpencil_poll_override(cls, context):
    return False

def register():
    bpy.utils.register_class(ArnoldRenderEngine)
    
    for panel in get_panels():
        panel.COMPAT_ENGINES.add(ArnoldRenderEngine.bl_idname)

    # For some reason, there are a handful of classes that get 'ARNOLD'
    # added to COMPAT_ENGINES even though they're left out of the
    # list returned from get_panels(). Need to file a bug report
    # to Blender devs, but for now we'll brute-force remove it.
    for panel in bpy.types.Panel.__subclasses__():
        if panel.__name__ == 'DATA_PT_light':
            panel.COMPAT_ENGINES.remove(ArnoldRenderEngine.bl_idname)

def unregister():
    bpy.utils.unregister_class(ArnoldRenderEngine)
    
    for panel in get_panels():
        if ArnoldRenderEngine.bl_idname in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove(ArnoldRenderEngine.bl_idname)

if __name__ == "__main__":
    register()