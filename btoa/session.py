import bpy
import arnold
import math
import mathutils
import numpy
import time
import os

from .exporter import *

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
        instances = {}
        for object_instance in depsgraph.object_instances:
            node = None

            if isinstance(object_instance.object.data, BTOA_CONVERTIBLE_TYPES):
                node = PolymeshExporter(self).export(object_instance)
            elif isinstance(object_instance.object.data, bpy.types.Light):
                node = LightExporter(self).export(object_instance)

            if node and object_instance.is_instance:
                parent = InstancerCache(object_instance.parent)
                result = [
                    node,
                    object_instance.instance_object.visible_get(view_layer=self.cache.view_layer)
                ]

                if parent not in instances.keys():
                    instances[parent] = [result]
                else:
                    instances[parent].append(result)
                
        # Create instances
        for key in instances.keys():
            InstanceExporter(self).export(key, instances[key])

        options = UniverseOptions()

        # Camera
        if context:
            # In viewport, we must reconsruct the camera ourselves
            bl_camera = export_utils.get_viewport_camera_object(context)
            self.last_viewport_matrix = bl_camera.matrix_world

            camera = CameraExporter(self).export(bl_camera)
        else:
            camera = CameraExporter(self).export(depsgraph.scene.camera.evaluated_get(depsgraph))

        options.set_pointer("camera", camera)

        # World
        if depsgraph.scene.world.arnold.node_tree:
            WorldExporter(self).export(depsgraph.scene.world)

        # AOVs
        scene = self.cache.scene
        aovs = depsgraph.view_layer.arnold.aovs
        enabled_aovs = [aovs.beauty] if self.is_interactive else aovs.enabled_aovs

        default_filter = ArnoldNode(scene["filter_type"])
        default_filter.set_string("name", "btoa_default_filter")
        default_filter.set_float("width", scene["filter_width"])

        outputs = ArnoldArray()
        outputs.allocate(len(enabled_aovs), 1, 'STRING')

        for aov in enabled_aovs:
            filter_type = "btoa_default_filter"

            if aov.name == 'Z':
                closest_filter = ArnoldNode("closest_filter")
                closest_filter.set_string("name", "btoa_closest_filter")
                closest_filter.set_float("width", scene["filter_width"])

                filter_type = "btoa_closest_filter"

            outputs.set_string(enabled_aovs.index(aov), f"{aov.ainame} {aov.pixel_type} {filter_type} btoa_driver")

        options.set_array("outputs", outputs)
        arnold.AiRenderAddInteractiveOutput(None, 0)

        # Color management
        color_manager = ArnoldColorManager()

        if 'OCIO' in os.environ:
            ocio = os.getenv('OCIO')
        else:
            install_dir = os.path.dirname(bpy.app.binary_path)
            major, minor, fix = bpy.app.version
            ocio = os.path.join(install_dir, f'{major}.{minor}', 'datafiles', 'colormanagement', 'config.ocio')
        
        color_manager.set_string('config', ocio)
        options.set_pointer('color_manager', color_manager)

    def free_buffer(self, buffer):
        rdata = buffer.contents

        for i in range(0, rdata.count):
            aov = rdata.aovs[i]
            arnold.AiFree(aov.data)
            
        arnold.AiFree(rdata.aovs)
        arnold.AiFree(buffer)

    def get_node_by_name(self, name):
        ainode = arnold.AiNodeLookUpByName(name)

        node = ArnoldNode()
        node.set_data(ainode)

        return node

    def get_all_by_uuid(self, uuid):
        iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_SHAPE | arnold.AI_NODE_LIGHT | arnold.AI_NODE_SHADER)
        result = []

        while not arnold.AiNodeIteratorFinished(iterator):
            ainode = arnold.AiNodeIteratorGetNext(iterator)
            
            if arnold.AiNodeGetStr(ainode, 'btoa_id') == uuid:
                node = ArnoldNode()
                node.set_data(ainode)
                result.append(node)
        
        return result

    def get_node_by_uuid(self, uuid):
        iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_SHAPE | arnold.AI_NODE_LIGHT | arnold.AI_NODE_SHADER)
        node = ArnoldNode()

        while not arnold.AiNodeIteratorFinished(iterator):
            ainode = arnold.AiNodeIteratorGetNext(iterator)
            btoa_id = arnold.AiNodeGetStr(ainode, 'btoa_id')
            
            if btoa_id == uuid:
                node.set_data(ainode)
                break
        
        return node

    def pause(self):
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
