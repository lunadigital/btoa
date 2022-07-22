import bpy
import arnold
import math
import mathutils
import numpy
import time
import os

from .exporter import PolymeshExporter, CameraExporter, OptionsExporter, LightExporter, WorldExporter

from .array import ArnoldArray
from .colormanager import ArnoldColorManager
from .node import ArnoldNode
from .polymesh import ArnoldPolymesh
from .universe_options import UniverseOptions
from .constants import BTOA_CONVERTIBLE_TYPES
from .session_cache import SessionCache
from . import utils as export_utils

if "AI_SESSION" not in globals().keys():
    AI_SESSION = None

class Session:
    def __init__(self):
        self.reset()
        self.update_viewport_dimensions = False

    def abort(self):
        arnold.AiRenderAbort()

    def end(self):
        if self.is_interactive:
            arnold.AiRenderInterrupt(arnold.AI_BLOCKING)
            arnold.AiRenderEnd()

        arnold.AiEnd()

    def destroy(self, node):
        arnold.AiNodeDestroy(node.data)

    def export(self, engine, depsgraph, prefs, context=None):
        global AI_SESSION
        self.cache.sync(engine, depsgraph, prefs, context)

        OptionsExporter(self).export(interactive=self.is_interactive)

        # Geometry and lights

        for instance in depsgraph.object_instances:
            ob = export_utils.get_object_data_from_instance(instance)

            if isinstance(ob.data, BTOA_CONVERTIBLE_TYPES):
                PolymeshExporter(self).export(instance)
            elif isinstance(ob.data, bpy.types.Light):
                LightExporter(self).export(instance)
            elif not self.is_interactive and isinstance(ob.data, bpy.types.Camera) and ob.name == depsgraph.scene.camera.name:
                camera = CameraExporter(self).export(instance)

        options = UniverseOptions()

        # Camera

        if context:
            # In viewport, we must reconsruct the camera ourselves
            bl_camera = export_utils.get_viewport_camera_object(context)
            self.last_viewport_matrix = bl_camera.matrix_world

            camera = CameraExporter(self).export(bl_camera)

        options.set_pointer("camera", camera)

        # World

        if depsgraph.scene.world.arnold.node_tree:
            WorldExporter(self).export(depsgraph.scene.world)

        # Everything else
        scene = self.cache.scene

        default_filter = ArnoldNode(scene["filter_type"])
        default_filter.set_string("name", "btoa_image_filter")
        default_filter.set_float("width", scene["filter_width"])

        outputs = ArnoldArray()
        outputs.allocate(1, 1, 'STRING')
        outputs.set_string(0, "RGBA RGBA btoa_image_filter btoa_driver")
        options.set_array("outputs", outputs)

        arnold.AiRenderAddInteractiveOutput(None, 0)

        color_manager = ArnoldColorManager()

        if 'OCIO' in os.environ:
            ocio = os.getenv('OCIO')
        else:
            install_dir = os.path.dirname(bpy.app.binary_path)
            ocio = os.path.join(install_dir, "3.2", "datafiles", "colormanagement", "config.ocio")
        
        color_manager.set_string("config", ocio)
        options.set_pointer("color_manager", color_manager)

    def free_buffer(self, buffer):
        arnold.AiFree(buffer)

    def get_node_by_name(self, name):
        ainode = arnold.AiNodeLookUpByName(name)

        node = ArnoldNode()
        node.set_data(ainode)

        return node

    def pause(self):
        self.is_running = False
        arnold.AiRenderInterrupt(arnold.AI_BLOCKING)

    def render(self):
        result = arnold.AiRenderBegin()
        if result == arnold.AI_SUCCESS.value:
            status = arnold.AiRenderGetStatus()
            while status == arnold.AI_RENDER_STATUS_RENDERING.value:
                time.sleep(0.001)
                status = arnold.AiRenderGetStatus()

        result = arnold.AiRenderEnd()

        self.end()
        self.reset()

    def render_interactive(self, callback):
        render_mode = arnold.AI_RENDER_MODE_CAMERA
        private_data = None

        result = arnold.AiRenderBegin(render_mode, callback, private_data)
        if result != arnold.AI_SUCCESS.value:
            self.end()
            self.reset()

    def reset(self):
        self.is_interactive = False
        self.is_running = False
        self.cache = SessionCache()

    def restart(self):
        arnold.AiRenderRestart()
        self.is_running = True

    def replace_node(self, old_node, new_node):
        arnold.AiNodeReplace(old_node.data, new_node.data, True)

    def start(self, interactive=False):
        self.is_running = True
        self.is_interactive = interactive

        render_mode = arnold.AI_SESSION_INTERACTIVE if interactive else arnold.AI_SESSION_BATCH
        arnold.AiBegin(render_mode)
