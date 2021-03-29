import bpy
import bgl
import numpy
import os
import math
import ctypes

from bl_ui.properties_render import RENDER_PT_color_management
import mathutils

from . import btoa
from . import utils

class ArnoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ARNOLD"
    bl_label = "Arnold"
    bl_use_preview = True

    def __init__(self):
        self.session = {}

        self.progress = 0
        self._progress_increment = 0
        
        btoa.start_session()

    def __del__(self):
        btoa.end_session()

    @classmethod
    def is_active(cls, context):
        return context.scene.render.engine == cls.bl_idname

    def create_camera(self, object_instance):
        node = btoa.BtNode("persp_camera")
        self.sync_camera(node, object_instance)
        
        return node

    def create_light(self, object_instance):
        ob = utils.get_object_data_from_instance(object_instance)

        ntype = btoa.BT_LIGHT_SHAPE_CONVERSIONS[ob.data.shape] if ob.data.type == 'AREA' else btoa.BT_LIGHT_CONVERSIONS[ob.data.type]
        node = btoa.BtNode(ntype)
        self.sync_light(node, object_instance)

        return node

    def create_polymesh(self, object_instance):
        ob = utils.get_object_data_from_instance(object_instance)
        mesh = utils.bake_mesh(ob)

        if mesh is None:
            return None

        settings = self.session["render_settings"]

        if settings.enable_motion_blur and settings.camera_motion_blur:
            transform_matrix = self.get_transform_blur_matrix(object_instance)
            mesh = utils.bake_mesh(ob)
        else:
            transform_matrix = utils.flatten_matrix(object_instance.matrix_world)

        if settings.enable_motion_blur and settings.deformation_motion_blur:
            motion_steps = numpy.linspace(
                settings.shutter_start,
                settings.shutter_end,
                settings.motion_keys
            )

            frame_current = self.session["scene"].frame_current

            vlist_data = None
            nlist_data = None

            for i in range(0, motion_steps.size):
                frame_as_flt = frame_current + motion_steps[i]
                frame_as_int = math.floor(frame_as_flt)
                subframe = frame_as_flt - frame_as_int

                self.frame_set(frame_as_int, subframe=subframe)
                mesh = utils.bake_mesh(ob)

                a = numpy.ndarray(
                    len(mesh.vertices) * 3,
                    dtype=numpy.float32
                )
                mesh.vertices.foreach_get("co", a)
                
                vlist_data = a if vlist_data is None else numpy.concatenate((vlist_data, a))

                a = numpy.ndarray(
                    len(mesh.loops) * 3,
                    dtype=numpy.float32
                )
                mesh.loops.foreach_get("normal", a)

                nlist_data = a if nlist_data is None else numpy.concatenate((nlist_data, a))

            self.frame_set(frame_current, subframe=0)
            mesh = utils.bake_mesh(ob)

            vlist = btoa.BtArray()
            vlist.convert_from_buffer(
                len(mesh.vertices),
                settings.motion_keys,
                'VECTOR',
                ctypes.c_void_p(vlist_data.ctypes.data)
            )

            nlist = btoa.BtArray()
            nlist.convert_from_buffer(
                len(mesh.loops),
                settings.motion_keys,
                'VECTOR',
                ctypes.c_void_p(nlist_data.ctypes.data)
            )

        else:
            a = numpy.ndarray(
                len(mesh.vertices) * 3,
                dtype=numpy.float32
            )
            mesh.vertices.foreach_get("co", a)

            vlist = btoa.BtArray()
            vlist.convert_from_buffer(
                len(mesh.vertices),
                1,
                'VECTOR',
                ctypes.c_void_p(a.ctypes.data)
            )

            a = numpy.ndarray(
                len(mesh.loops) * 3,
                dtype=numpy.float32
            )
            mesh.loops.foreach_get("normal", a)

            nlist = btoa.BtArray()
            nlist.convert_from_buffer(
                len(mesh.loops),
                1,
                'VECTOR',
                ctypes.c_void_p(a.ctypes.data)
            )

        # Polygons
        a = numpy.ndarray(
            len(mesh.polygons),
            dtype=numpy.uint32
        )
        mesh.polygons.foreach_get("loop_total", a)

        nsides = btoa.BtArray()
        nsides.convert_from_buffer(
            len(mesh.polygons),
            1,
            'UINT',
            ctypes.c_void_p(a.ctypes.data)
        )

        a = numpy.ndarray(
            len(mesh.loops),
            dtype=numpy.uint32
        )
        mesh.polygons.foreach_get("vertices", a)

        vidxs = btoa.BtArray()
        vidxs.convert_from_buffer(
            len(mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(a.ctypes.data)
        )

        a = numpy.arange(
            len(mesh.loops),
            dtype=numpy.uint32
        )
        
        nidxs = btoa.BtArray()
        nidxs.convert_from_buffer(
            len(mesh.loops),
            1,
            'UINT',
            ctypes.c_void_p(a.ctypes.data)
        )

        # Create polymesh object
        name = utils.get_unique_name(object_instance)
        node = btoa.BtPolymesh(name)

        if settings.enable_motion_blur and settings.camera_motion_blur:
            node.set_array("matrix", transform_matrix)
        else:
            node.set_matrix("matrix", transform_matrix)
        
        node.set_bool("smoothing", True)
        node.set_array("vlist", vlist)
        node.set_array("nlist", nlist)
        node.set_array("nsides", nsides)
        node.set_array("vidxs", vidxs)
        node.set_array("nidxs", nidxs)
        node.set_float("motion_start", settings.shutter_start)
        node.set_float("motion_end", settings.shutter_end)

        # UV's
        for i, uvt in enumerate(mesh.uv_layers):
            if uvt.active_render:
                data = mesh.uv_layers[i].data
                
                a = numpy.arange(len(data), dtype=numpy.uint32)
                uvidxs = btoa.BtArray()
                uvidxs.convert_from_buffer(
                    len(data),
                    1,
                    'UINT',
                    ctypes.c_void_p(a.ctypes.data)
                )

                a = numpy.ndarray(
                    len(data) * 2,
                    dtype=numpy.float32
                )
                data.foreach_get("uv", a)

                uvlist = btoa.BtArray()
                uvlist.convert_from_buffer(
                    len(data),
                    1,
                    'VECTOR2',
                    ctypes.c_void_p(a.ctypes.data)
                )

                node.set_array("uvidxs", uvidxs)
                node.set_array("uvlist", uvlist)

                break

        # Materials
        # This should really be in a for loop, but for now we're only
        # looking for the material in the first slot.
        # for slot in ob.material_slots:
        try:
            slot = ob.material_slots[0]
            if slot.material is not None:
                unique_name = utils.get_unique_name(slot.material)

                if slot.material.arnold.node_tree is not None:
                    shader = btoa.get_node_by_name(unique_name)

                    if shader.is_valid():
                        node.set_pointer("shader", shader)
                    else:
                        surface, volume, displacement = slot.material.arnold.node_tree.export()
                        surface[0].set_string("name", unique_name)
                        node.set_pointer("shader", surface[0])

        except:
            print("WARNING: {} has no material slots assigned!".format(ob.name))

        return node

    def create_world(self):
        world = self.session["scene"].world
        arnold = world.arnold.data

        unique_name = utils.get_unique_name(world)

        surface, volume, displacement = world.arnold.node_tree.export()
        btnode = surface[0]
        
        btnode.set_string("name", unique_name)

        # Flip image textures in the U direction
        image = btnode.get_link("color")
        if image.is_valid() and image.type_is("image"):
            sflip = image.get_bool("sflip")
            image.set_bool("sflip", not sflip)

        btnode.set_int("samples", arnold.samples)
        btnode.set_bool("normalize", arnold.normalize)

        btnode.set_bool("cast_shadows", arnold.cast_shadows)
        btnode.set_bool("cast_volumetric_shadows", arnold.cast_volumetric_shadows)
        btnode.set_rgb("shadow_color", *arnold.shadow_color)
        btnode.set_float("shadow_density", arnold.shadow_density)

        btnode.set_float("camera", arnold.camera)
        btnode.set_float("diffuse", arnold.diffuse)
        btnode.set_float("specular", arnold.specular)
        btnode.set_float("transmission", arnold.transmission)
        btnode.set_float("sss", arnold.sss)
        btnode.set_float("indirect", arnold.indirect)
        btnode.set_float("volume", arnold.volume)
        btnode.set_int("max_bounces", arnold.max_bounces)

        return btnode

    def get_transform_blur_matrix(self, object_instance):
        settings = self.session["render_settings"]
        
        motion_steps = numpy.linspace(
            settings.shutter_start,
            settings.shutter_end,
            settings.motion_keys
        )

        frame_current = self.session["scene"].frame_current

        transform_matrix = btoa.BtArray()
        transform_matrix.allocate(1, settings.motion_keys, 'MATRIX')
        
        for i in range(0, motion_steps.size):
            frame_as_flt = frame_current + motion_steps[i]
            frame_as_int = math.floor(frame_as_flt)
            subframe = frame_as_flt - frame_as_int

            self.frame_set(frame_as_int, subframe=subframe)
            
            m = utils.flatten_matrix(object_instance.matrix_world)
            transform_matrix.set_matrix(i, m)

        self.frame_set(frame_current, subframe=0)

        return transform_matrix

    def get_render_resolution(self, scene):
        scale = scene.render.resolution_percentage / 100
        x = int(scene.render.resolution_x * scale)
        y = int(scene.render.resolution_y * scale)

        return mathutils.Vector((x, y))

    def sync_camera(self, btnode, object_instance):
        ob = utils.get_object_data_from_instance(object_instance)
        data = ob.data
        arnold = data.arnold
        settings = self.session["render_settings"]

        btnode.set_string("name", utils.get_unique_name(object_instance))

        if settings.enable_motion_blur and settings.camera_motion_blur:
            matrix = self.get_transform_blur_matrix(object_instance)
            btnode.set_array("matrix", matrix)
        else:
            matrix = utils.flatten_matrix(object_instance.matrix_world)
            btnode.set_matrix("matrix", matrix)

        fov = utils.calc_horizontal_fov(ob)
        btnode.set_float("fov", math.degrees(fov))
        btnode.set_float("exposure", arnold.exposure)

        if data.dof.focus_object:
            distance = mathutils.geometry.distance_point_to_plane(
                ob.matrix_world.to_translation(),
                data.dof.focus_object.matrix_world.to_translation(),
                ob.matrix_world.col[2][:3]
            )
        else:
            distance = data.dof.focus_distance

        aperture_size = arnold.aperture_size if arnold.enable_dof else 0

        btnode.set_float("focus_distance", distance)
        btnode.set_float("aperture_size", aperture_size)
        btnode.set_int("aperture_blades", arnold.aperture_blades)
        btnode.set_float("aperture_rotation", arnold.aperture_rotation)
        btnode.set_float("aperture_blade_curvature", arnold.aperture_blade_curvature)
        btnode.set_float("aperture_aspect_ratio", arnold.aperture_aspect_ratio)

        btnode.set_float("near_clip", data.clip_start)
        btnode.set_float("far_clip", data.clip_end)

        if settings.enable_motion_blur:
            btnode.set_float("shutter_start", settings.shutter_start)
            btnode.set_float("shutter_end", settings.shutter_end)
            #btnode.set_string("shutter_type", arnold.shutter_type)
            #btnode.set_string("rolling_shutter", arnold.rolling_shutter)
            #btnode.set_float("rolling_shutter_duration", arnold.rolling_shutter_duration)

    def sync_light(self, btnode, object_instance):    
        ob = utils.get_object_data_from_instance(object_instance)

        data = ob.data
        arnold = data.arnold

        btnode.set_string("name", utils.get_unique_name(object_instance))

        # Set matrix for everything except cylinder lights
        if not hasattr(data, "shape") or data.shape != 'RECTANGLE':
            btnode.set_matrix(
                "matrix",
                utils.flatten_matrix(ob.matrix_world)
            )
        
        btnode.set_rgb("color", *data.color)
        btnode.set_float("intensity", arnold.intensity)
        btnode.set_float("exposure", arnold.exposure)
        btnode.set_int("samples", arnold.samples)
        btnode.set_bool("normalize", arnold.normalize)

        btnode.set_bool("cast_shadows", arnold.cast_shadows)
        btnode.set_bool("cast_volumetric_shadows", arnold.cast_volumetric_shadows)
        btnode.set_rgb("shadow_color", *arnold.shadow_color)
        btnode.set_float("shadow_density", arnold.shadow_density)

        btnode.set_float("camera", arnold.camera)
        btnode.set_float("diffuse", arnold.diffuse)
        btnode.set_float("specular", arnold.specular)
        btnode.set_float("transmission", arnold.transmission)
        btnode.set_float("sss", arnold.sss)
        btnode.set_float("indirect", arnold.indirect)
        btnode.set_float("volume", arnold.volume)
        btnode.set_int("max_bounces", arnold.max_bounces)

        if data.type in ('POINT', 'SPOT'):
            btnode.set_float("radius", data.shadow_soft_size)

        if data.type == 'SUN':
            btnode.set_float("angle", arnold.angle)

        if data.type == 'SPOT':
            btnode.set_float("cone_angle", math.degrees(data.spot_size))
            btnode.set_float("penumbra_angle", math.degrees(arnold.penumbra_angle))
            btnode.set_float("roundness", arnold.spot_roundness)
            btnode.set_float("aspect_ratio", arnold.aspect_ratio)
            btnode.set_float("lens_radius", arnold.lens_radius)

        if data.type == 'AREA':
            btnode.set_float("roundness", arnold.area_roundness)
            btnode.set_float("spread", arnold.spread)
            btnode.set_int("resolution", arnold.resolution)
            btnode.set_float("soft_edge", arnold.soft_edge)
            
            if data.shape == 'SQUARE':
                smatrix = mathutils.Matrix.Diagonal((
                    data.size / 2,
                    data.size / 2,
                    data.size / 2
                )).to_4x4()
                
                tmatrix = ob.matrix_world @ smatrix
            
                btnode.set_matrix(
                    "matrix",
                    utils.flatten_matrix(tmatrix)
                )
            elif data.shape == 'DISK':
                s = ob.scale.x if ob.scale.x > ob.scale.y else ob.scale.y
                btnode.set_float("radius", 0.5 * data.size * s)
            elif data.shape == 'RECTANGLE':
                d = 0.5 * data.size_y * ob.scale.y
                top = utils.get_position_along_local_vector(ob, d, 'Y')
                bottom = utils.get_position_along_local_vector(ob, -d, 'Y')

                btnode.set_vector("top", *top)
                btnode.set_vector("bottom", *bottom)

                s = ob.scale.x if ob.scale.x > ob.scale.z else ob.scale.z
                btnode.set_float("radius", 0.5 * data.size * s)

    def update(self, data, depsgraph):
        self.session["depsgraph"] = depsgraph
        self.session["scene"] = depsgraph.scene
        self.session["render_settings"] = depsgraph.scene.arnold_options
        self.session["options"] = btoa.BtOptions()
        self.session["resolution"] = self.get_render_resolution(depsgraph.scene)

        # Global render options
        options = self.session["options"]
        resolution = self.session["resolution"]
        settings = self.session["render_settings"]

        options.set_int("xres", int(resolution.x))
        options.set_int("yres", int(resolution.y))

        options.set_int("render_device", int(settings.render_device))

        options.set_int("AA_samples", settings.aa_samples)
        options.set_int("GI_diffuse_samples", settings.diffuse_samples)
        options.set_int("GI_specular_samples", settings.specular_samples)
        options.set_int("GI_transmission_samples", settings.transmission_samples)
        options.set_int("GI_sss_samples", settings.sss_samples)
        options.set_int("GI_volume_samples", settings.volume_samples)
        options.set_float("AA_sample_clamp", settings.sample_clamp)
        options.set_bool("AA_sample_clamp_affects_aovs", settings.clamp_aovs)
        options.set_float("indirect_sample_clamp", settings.indirect_sample_clamp)
        options.set_float("low_light_threshold", settings.low_light_threshold)

        options.set_bool("enable_adaptive_sampling", settings.use_adaptive_sampling)
        options.set_int("AA_samples_max", settings.adaptive_aa_samples_max)
        options.set_float("adaptive_threshold", settings.adaptive_threshold)

        if settings.aa_seed > 0:
            options.set_int("AA_seed", settings.aa_seed)

        options.set_int("GI_total_depth", settings.total_depth)
        options.set_int("GI_diffuse_depth", settings.diffuse_depth)
        options.set_int("GI_specular_depth", settings.specular_depth)
        options.set_int("GI_transmission_depth", settings.transmission_depth)
        options.set_int("GI_volume_depth", settings.volume_depth)
        options.set_int("auto_transparency_depth", settings.transparency_depth)

        options.set_int("bucket_size", settings.bucket_size)
        options.set_string("bucket_scanning", settings.bucket_scanning)
        options.set_bool("parallel_node_init", settings.parallel_node_init)
        options.set_int("threads", settings.threads)
  
        # Export scene objects
        
        for object_instance in depsgraph.object_instances:
            ob = utils.get_object_data_from_instance(object_instance)
            ob_unique_name = utils.get_unique_name(object_instance)

            if ob.type in btoa.BT_CONVERTIBLE_TYPES:
                node = btoa.get_node_by_name(ob_unique_name)

                if not node.is_valid():
                    node = self.create_polymesh(object_instance)
                    
            elif ob.type == 'CAMERA' and ob.name == self.session["scene"].camera.name:
                node = btoa.get_node_by_name(ob_unique_name)
                
                if not node.is_valid(): 
                    node = self.create_camera(object_instance)
                #else:
                #    self.sync_camera(node, object_instance)

                options.set_pointer("camera", node)
            
            if ob.type == 'LIGHT':
                node = btoa.get_node_by_name(ob_unique_name)
                
                if not node.is_valid():
                    node = self.create_light(object_instance)

                # If existing AiNode is an area light, but doesn't match the type in Blender
                #elif node.type_is("quad_light") or node.type_is("disk_light") or node.type_is("cylinder_light"):
                #    if not node.type_is(btoa.BT_LIGHT_SHAPE_CONVERSIONS[ob.data.shape]):
                #        node.destroy()
                #        node = self.create_light(object_instance)

                # If existing AiNode is a non-area light type, but doesn't match the type in Blender
                #elif not node.type_is(btoa.BT_LIGHT_CONVERSIONS[ob.data.type]):
                #    node.destroy()
                #    node = btoa_utils.create_light(object_instance)

                # If AiNode exists and same type, just update params
                #else:
                #    btoa_utils.sync_light(node, object_instance)

        # Export world settings

        if self.session["scene"].world.arnold.node_tree is not None:
            self.create_world()

        # Add final required nodeds

        default_filter = btoa.BtNode("gaussian_filter")
        default_filter.set_string("name", "gaussianFilter")

        outputs = btoa.BtArray()
        outputs.allocate(1, 1, 'STRING')
        outputs.set_string(0, "RGBA RGBA gaussianFilter __display_driver")
        options.set_array("outputs", outputs)

        color_manager = btoa.BtColorManager()
        color_manager.set_string("config", os.getenv("OCIO"))
        options.set_pointer("color_manager", color_manager)

    def render(self, depsgraph):
        engine = self
        _htiles = {}
        
        def display_callback(x, y, width, height, buffer, data):
            resolution = engine.session["resolution"]

            if buffer:
                try:
                    result = _htiles.pop((x, y), None)
                    
                    if result is None:
                        result = engine.begin_result(x, resolution.y - y - height, width, height)
                    
                    _buffer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_float))
                    rect = numpy.ctypeslib.as_array(_buffer, shape=(width * height, 4))
                    
                    result.layers[0].passes["Combined"].rect = rect
                    engine.end_result(result)

                    engine.progress += engine._progress_increment
                    engine.update_progress(engine.progress)
                finally:
                    btoa.free(buffer)
            else:
                result = engine.begin_result(x, resolution.y - y - height, width, height)
                _htiles[(x, y)] = result
            
            if engine.test_break():
                btoa.abort()
                while _htiles:
                    (x, y), result = _htiles.popitem()
                    engine.end_result(result, cancel=True)

        # Calculate progress increment
        options = self.session["options"]
        
        width = options.get_int("xres")
        height = options.get_int("yres")
        bucket_size = options.get_int("bucket_size")

        h_buckets = math.ceil(width / bucket_size)
        v_buckets = math.ceil(height / bucket_size)
        total_buckets = h_buckets * v_buckets
        
        self.progress = 0
        self._progress_increment = 1 / total_buckets

        # Set callback
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