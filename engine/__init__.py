import bpy
import bgl
import arnold

# For more info, visit:
# https://docs.blender.org/api/current/bpy.types.RenderEngine.html
class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True

    def __init__(self):
        self.scene_data = None
        self.draw_data = None

    def __del__(self):
        pass

    def render(self, depsgraph):
        scene = depsgraph.scene
        
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        arnold.AiBegin()

        sphere = arnold.AiNode("sphere")
        arnold.AiNodeSetStr(sphere, "name", "mysphere")
        arnold.AiNodeSetVec(sphere, "center", 0, 4, 0)
        arnold.AiNodeSetFlt(sphere, "radius", 4)

        shader = arnold.AiNode("standard_surface")
        arnold.AiNodeSetStr(shader, "name", "redShader")
        arnold.AiNodeSetRGB(shader, "base_color", 1, 0.02, 0.02)
        arnold.AiNodeSetFlt(shader, "specular", 0.05)

        arnold.AiNodeSetPtr(sphere, "shader", shader)

        camera = arnold.AiNode("persp_camera")
        arnold.AiNodeSetStr(camera, "name", "Camera")
        arnold.AiNodeSetVec(camera, "position", 0, 10, 35)
        arnold.AiNodeSetVec(camera, "look_at", 0, 3, 0)
        arnold.AiNodeSetFlt(camera, "fov", 45)

        light = arnold.AiNode("point_light")
        arnold.AiNodeSetStr(light, "name", "pointLight")
        arnold.AiNodeSetVec(light, "position", 15, 30, 15)
        arnold.AiNodeSetFlt(light, "intensity", 4500)
        arnold.AiNodeSetFlt(light, "radius", 4)

        options = arnold.AiUniverseGetOptions()
        arnold.AiNodeSetInt(options, "AA_samples", 8)
        arnold.AiNodeSetInt(options, "xres", self.size_x)
        arnold.AiNodeSetInt(options, "yres", self.size_y)
        arnold.AiNodeSetInt(options, "GI_diffuse_depth", 4)
        arnold.AiNodeSetPtr(options, "camera", camera)

        driver = arnold.AiNode("driver_jpeg")
        arnold.AiNodeSetStr(driver, "name", "jpegDriver")
        arnold.AiNodeSetStr(driver, "filename", "myFirstRender.jpg")

        filter = arnold.AiNode("gaussian_filter")
        arnold.AiNodeSetStr(filter, "name", "gaussianFilter")

        outputs = arnold.AiArrayAllocate(1, 1, arnold.AI_TYPE_STRING)
        arnold.AiArraySetStr(outputs, 0, "RGBA RGBA gaussianFilter jpegDriver")
        arnold.AiNodeSetArray(options, "outputs", outputs)

        arnold.AiRender(arnold.AI_RENDER_MODE_CAMERA)

        arnold.AiEnd()

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

def register():
    bpy.utils.register_class(ArnoldRenderEngine)

def unregister():
    bpy.utils.unregister_class(ArnoldRenderEngine)

if __name__ == "__main__":
    register()