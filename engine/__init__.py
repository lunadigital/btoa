import bpy
import bgl
import ctypes
import math
import mathutils
import numpy
import os

from .. import btoa

from bl_ui.properties_render import RENDER_PT_color_management

class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True

    def __init__(self):
        self.progress = 0
        self._progress_increment = 0
        
        self.session = btoa.Session()

        self.framebuffer = None

    def __del__(self):
        self.session.end()

    @classmethod
    def is_active(cls, context):
        return context.scene.render.engine == cls.bl_idname

    def update(self, data, depsgraph):
        self.session.start()
        self.session.export(self, depsgraph)

    def render(self, depsgraph):
        # Configure display callback
        # NOTE: We can't do this in the exporter because it results in a nasty MEMORY_ACCESS_VIOLATION error

        options = btoa.UniverseOptions()

        _session = self.session
        _buckets = {}

        def update_render_result(x, y, width, height, buffer, data):
            render = _session.depsgraph.scene.render

            if render.use_border:
                min_x, min_y, max_x, max_y = options.get_render_region()
            else:
                min_x, min_y, max_x, max_y = 0, 0, *options.get_render_resolution()

            x = x - min_x
            y = max_y - y - height

            if buffer:
                try:
                    result = _buckets.pop((x, y), None)

                    if result is None:
                        result = _session.engine.begin_result(x, y, width, height)

                    b = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
                    rect = numpy.ctypeslib.as_array(b, shape=(width * height, 4))

                    result.layers[0].passes["Combined"].rect = rect
                    _session.engine.end_result(result)

                    # Update progress counter

                    _session.engine.progress += _session.engine._progress_increment
                    _session.engine.update_progress(_session.engine.progress)
                
                finally:
                    _session.free_buffer(buffer)
            else:
                _buckets[(x, y)] = _session.engine.begin_result(x, y, width, height)

            if _session.engine.test_break():
                _session.abort()
                while _buckets:
                    (x, y), result = _buckets.popitem()
                    _session.engine.end_result(result, cancel=True)

        cb = btoa.ArnoldDisplayCallback(update_render_result)

        display_node = self.session.get_node_by_name("__display_driver")
        
        if not display_node.is_valid():
            display_node = btoa.ArnoldNode("driver_display_callback")
            display_node.set_string("name", "__display_driver")
        
        display_node.set_pointer("callback", cb)

        # Calculate progress increment
        
        width, height = options.get_render_resolution()
        bucket_size = options.get_int("bucket_size")

        h_buckets = math.ceil(width / bucket_size)
        v_buckets = math.ceil(height / bucket_size)
        total_buckets = h_buckets * v_buckets
        
        self.progress = 0
        self._progress_increment = 1 / total_buckets

        self.session.render()

        # Reset session to free RenderEngine class and call AiEnd()
        self.session.reset()

    def view_update(self, context, depsgraph):
        if not self.session.is_running:
            self.session.start(interactive=True)

        self.session.export(self, depsgraph)

        _session = self.session
        _framebuffer = self.framebuffer

        def update_viewport(x, y, width, height, buffer, data):
            print(x, y, width, height, buffer, data)
            '''if buffer:
                try:
                    _buffer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint16))
                    a = numpy.ctypeslib.as_array(_buffer, shape=(height, width, 4))
                    _framebuffer.set_data(a)
                    #rect[y : y + height, x : x + width] = a
                    #redraw_event.set()
                finally:
                    _session.free_buffer(buffer)'''

        cb = btoa.ArnoldDisplayCallback(update_viewport)

        display_node = self.session.get_node_by_name("__display_driver")
        
        if not display_node.is_valid():
            display_node = btoa.ArnoldNode("driver_display_callback")
            display_node.set_string("name", "__display_driver")
        
        display_node.set_pointer("callback", cb)

        self.session.render()

    def view_draw(self, context, depsgraph):
        region = context.region
        scene = depsgraph.scene

        dimensions = region.width, region.height

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_ONE, bgl.GL_ONE_MINUS_SRC_ALPHA)
        self.bind_display_space_shader(scene)

        if not self.framebuffer or self.framebuffer.dimensions != dimensions:
            self.framebuffer = FrameBuffer(dimensions)
        
        self.framebuffer.draw()

        self.unbind_display_space_shader()
        bgl.glDisable(bgl.GL_BLEND)

class FrameBuffer:
    def __init__(self, dimensions):
        self.dimensions = dimensions

        self.pixel_data = [0.0, 0.0, 0.0, 1.0] * width * height
        self.build_gl_texture()

    def set_data(self, data):
        width, height = dimensions
        self.pixel_data = bgl.Buffer(bgl.GL_FLOAT, width * height * 4, data)

        self.build_gl_texture()

    def build_gl_texture(self):
        width, height = dimensions

        self.texture = bgl.Buffer(bgl.GL_INT, 1)

        bgl.glGenTextures(1, self.texture)
        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.texture[0])
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA16F, width, height, 0, bgl.GL_RGBA, bgl.GL_FLOAT, self.pixel_data)
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
        'WORLD_PT_context_world',
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