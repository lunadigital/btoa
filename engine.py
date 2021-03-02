import bpy
import bgl
import numpy
import os
import ctypes

from bl_ui.properties_render import RENDER_PT_color_management
from mathutils import Vector

from . import btoa
from .utils import btoa_utils, depsgraph_utils

class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True

    def __init__(self):
        self.resolution = Vector((0, 0))
        btoa.start_session()

    def __del__(self):
        btoa.end_session()

    @classmethod
    def is_active(cls, context):
        return context.scene.render.engine == cls.bl_idname

    def __get_render_resolution(self, scene):
        scale = scene.render.resolution_percentage / 100
        x = int(scene.render.resolution_x * scale)
        y = int(scene.render.resolution_y * scale)

        return x, y

    def update(self, data, depsgraph):
        scene = depsgraph.scene

        ai_options = scene.arnold_options
        bt_options = btoa.BtOptions()
        
        # Render resolution
        x, y = self.__get_render_resolution(scene)
        self.resolution.x = x
        self.resolution.y = y
        bt_options.set_int("xres", x)
        bt_options.set_int("yres", y)

        # Sampling settings
        bt_options.set_int("AA_samples", ai_options.aa_samples)
        bt_options.set_int("GI_diffuse_samples", ai_options.diffuse_samples)
        bt_options.set_int("GI_specular_samples", ai_options.specular_samples)
        bt_options.set_int("GI_transmission_samples", ai_options.transmission_samples)
        bt_options.set_int("GI_sss_samples", ai_options.sss_samples)
        bt_options.set_int("GI_volume_samples", ai_options.volume_samples)
        bt_options.set_float("AA_sample_clamp", ai_options.sample_clamp)
        bt_options.set_bool("AA_sample_clamp_affects_aovs", ai_options.clamp_aovs)
        bt_options.set_float("indirect_sample_clamp", ai_options.indirect_sample_clamp)
        bt_options.set_float("low_light_threshold", ai_options.low_light_threshold)

        if ai_options.aa_seed > 0:
            bt_options.set_int("AA_seed", ai_options.aa_seed)

        # Ray depth settings
        bt_options.set_int("GI_total_depth", ai_options.total_depth)
        bt_options.set_int("GI_diffuse_depth", ai_options.diffuse_depth)
        bt_options.set_int("GI_specular_depth", ai_options.specular_depth)
        bt_options.set_int("GI_transmission_depth", ai_options.transmission_depth)
        bt_options.set_int("GI_volume_depth", ai_options.volume_depth)
        bt_options.set_int("auto_transparency_depth", ai_options.transparency_depth)

        # Render settings
        bt_options.set_int("bucket_size", ai_options.bucket_size)
        bt_options.set_string("bucket_scanning", ai_options.bucket_scanning)
        bt_options.set_bool("parallel_node_init", ai_options.parallel_node_init)
        bt_options.set_int("threads", ai_options.threads)
  
        for object_instance in depsgraph.object_instances:
            ob = depsgraph_utils.get_object_data_from_instance(object_instance)
            btoa_unique_name = depsgraph_utils.get_unique_name(object_instance)

            # Geometry & objects
            if ob.type in btoa.BT_CONVERTIBLE_TYPES:
                node = btoa.get_node_by_name(btoa_unique_name)
                if not node.is_valid():
                    node = btoa_utils.create_polymesh(object_instance)
                    
            elif ob.type == 'CAMERA' and ob.name == scene.camera.name:
                camera_node = btoa.get_node_by_name(btoa_unique_name)
                if not camera_node.is_valid(): 
                    camera_node = btoa_utils.create_camera(object_instance)
                else:
                    btoa_utils.sync_camera(camera_node, object_instance)
                
                bt_options.set_pointer("camera", camera_node)
            
            # Lights
            if ob.type == 'LIGHT':
                node = btoa.get_node_by_name(btoa_unique_name)
                if not node.is_valid():
                    node = btoa_utils.create_light(object_instance)

                # If existing AiNode is an area light, but doesn't match the type in Blender
                elif node.type_is("quad_light") or node.type_is("disk_light") or node.type_is("cylinder_light"):
                    if not node.type_is(btoa.BT_LIGHT_SHAPE_CONVERSIONS[ob.data.shape]):
                        node.destroy()
                        node = btoa_utils.create_light(object_instance)

                # If existing AiNode is a non-area light type, but doesn't match the type in Blender
                elif not node.type_is(btoa.BT_LIGHT_CONVERSIONS[ob.data.type]):
                    node.destroy()
                    node = btoa_utils.create_light(object_instance)

                # If AiNode exists and same type, just update params
                else:
                    btoa_utils.sync_light(node, object_instance)

        gaussian_filter = btoa.BtNode("gaussian_filter")
        gaussian_filter.set_string("name", "gaussianFilter")

        outputs = btoa.BtArray()
        outputs.allocate(1, 1, 'STRING')
        outputs.set_string(0, "RGBA RGBA gaussianFilter __display_driver")
        bt_options.set_array("outputs", outputs)

        color_manager = btoa.BtColorManager()
        color_manager.set_string("config", os.getenv("OCIO"))
        bt_options.set_pointer("color_manager", color_manager)

    def render(self, depsgraph):
        engine = self
        _htiles = {}
        
        def display_callback(x, y, width, height, buffer, data):
            if buffer:
                try:
                    result = _htiles.pop((x, y), None)
                    
                    if result is None:
                        result = engine.begin_result(x, engine.resolution.y - y - height, width, height)
                    
                    _buffer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
                    rect = numpy.ctypeslib.as_array(_buffer, shape=(width * height, 4))
                    
                    result.layers[0].passes["Combined"].rect = rect
                    engine.end_result(result)
                finally:
                    btoa.free(buffer)
            else:
                result = engine.begin_result(x, engine.resolution.y - y - height, width, height)
                _htiles[(x, y)] = result
            
            if engine.test_break():
                btoa.abort()
                while _htiles:
                    (x, y), result = _htiles.popitem()
                    engine.end_result(result, cancel=True)

        cb = btoa.AtDisplayCallback(display_callback)
        
        display_node = btoa.get_node_by_name("__display_driver")
        if not display_node.is_valid():
            display_node = btoa.BtNode("driver_display_callback")
            display_node.set_string("name", "__display_driver")
        
        display_node.set_pointer("callback", cb)

        btoa.render()

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