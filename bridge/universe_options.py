import bpy
import arnold
import datetime
import math
import os

from pathlib import Path

from . import constants
from . import utils as export_utils
from .node import ArnoldNode

class UniverseOptions(ArnoldNode):
    def __init__(self):
        super().__init__()
        self.data = arnold.AiUniverseGetOptions(None)

    def export(self, depsgraph, context=None):
        scene = depsgraph.scene
        render = scene.render
        view_layer = depsgraph.view_layer_eval
        prefs = bpy.context.preferences.addons[constants.BTOA_PACKAGE_NAME].preferences

        # Set render resolution
        x, y = export_utils.get_render_resolution(depsgraph.scene, context)
        self.set_render_resolution(x, y)

        # Set render border
        if render.use_border:
            min_x = int(x * render.border_min_x)
            min_y = int(math.floor(y * (1 - render.border_max_y)))
            max_x = int(x * render.border_max_x) - 1
            max_y = int(math.floor(y * (1 - render.border_min_y))) - 1

            self.set_render_region(min_x, min_y, max_x, max_y)
        
        # Set universe options
        self.set_int("render_device", int(scene.arnold.render_device))

        self.set_int("AA_samples", scene.arnold.aa_samples)
        self.set_int("GI_diffuse_samples", scene.arnold.diffuse_samples)
        self.set_int("GI_specular_samples", scene.arnold.specular_samples)
        self.set_int("GI_transmission_samples", scene.arnold.transmission_samples)
        self.set_int("GI_sss_samples", scene.arnold.sss_samples)
        self.set_int("GI_volume_samples", scene.arnold.volume_samples)

        if scene.arnold.clamp_aa_samples:
            self.set_float("AA_sample_clamp", scene.arnold.sample_clamp)
            self.set_bool("AA_sample_clamp_affects_aovs", scene.arnold.clamp_aovs)
        
        self.set_float("indirect_sample_clamp", scene.arnold.indirect_sample_clamp)
        self.set_float("low_light_threshold", scene.arnold.low_light_threshold)

        self.set_bool("enable_adaptive_sampling", scene.arnold.use_adaptive_sampling)
        self.set_int("AA_samples_max", scene.arnold.adaptive_aa_samples_max)
        self.set_float("AA_adaptive_threshold", scene.arnold.adaptive_threshold)

        seed = 1 if scene.arnold.lock_sampling_pattern else scene.frame_current
        self.set_int("AA_seed", seed)

        self.set_int("GI_total_depth", scene.arnold.total_depth)
        self.set_int("GI_diffuse_depth", scene.arnold.diffuse_depth)
        self.set_int("GI_specular_depth", scene.arnold.specular_depth)
        self.set_int("GI_transmission_depth", scene.arnold.transmission_depth)
        self.set_int("GI_volume_depth", scene.arnold.volume_depth)
        self.set_int("auto_transparency_depth", scene.arnold.transparency_depth)

        self.set_int("bucket_size", scene.arnold.bucket_size)
        self.set_string("bucket_scanning", scene.arnold.bucket_scanning)
        self.set_bool("parallel_node_init", scene.arnold.parallel_node_init)
        self.set_int("threads", scene.arnold.threads)

        # Film transparency
        if not render.film_transparent:
            shader = ArnoldNode("flat")
            shader.set_string("name", "film_background")
            shader.set_rgb("color", 0, 0, 0)
            self.set_pointer("background", shader)

        # IPR render settings
        self.set_bool("enable_progressive_render", True)
        self.set_bool("enable_dependency_graph", True)

        # License settings
        self.set_bool("abort_on_license_fail", prefs.abort_on_license_fail)
        self.set_bool("skip_license_check", prefs.skip_license_check)

        # Logging settings
        if prefs.log_to_file:
            t = str(datetime.now()).replace(" ", "-").replace(":", "-").split(".")[0]
            folder = prefs.log_path if prefs.log_path != "" else Path.home()
            filename = f"arnold-{t}.log"
            filepath = os.path.join(folder, filename)

            Path(folder).mkdir(parents=True, exist_ok=True)

            arnold.AiMsgSetLogFileName(filepath)
        
        if prefs.log_all:
            arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_ALL)
        else:
            arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_NONE)

            if prefs.log_info:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_INFO)
            if prefs.log_warnings:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_WARNINGS)
            if prefs.log_errors:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_ERRORS)
            if prefs.log_debug:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_DEBUG)
            if prefs.log_stats:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_STATS)
            if prefs.log_plugins:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_PLUGINS)
            if prefs.log_progress:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_PROGRESS)
            if prefs.log_nan:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_NAN)
            if prefs.log_timestamp:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_TIMESTAMP)
            if prefs.log_backtrace:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_BACKTRACE)
            if prefs.log_memory:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_MEMORY)
            if prefs.log_color:
                arnold.AiMsgSetConsoleFlags(None, arnold.AI_LOG_COLOR)
        
        # Ignore features settings
        for key in scene.keys():
            if "ignore_" in key:
                self.set_bool(key, scene[key])
        
        # Denoiser settings
        driver = arnold.AiNodeLookUpByName(None, "btoa_driver")
        denoiser = arnold.AiNodeGetPtr(driver, "input")

        if denoiser:
            arnold.AiNodeDestroy(denoiser)

        if scene.arnold.enable_viewport_denoising:
            denoiser = arnold.AiNode(None, scene.arnold.viewport_denoiser)
            arnold.AiNodeSetPtr(driver, "input", denoiser)
        
        # Material override
        material_override = view_layer.material_override

        if material_override:
            shader = self.session.get_node_by_uuid(material_override.uuid)

            if not shader.is_valid:
                surface, volume, displacement = material_override.arnold.node_tree.export()
                surface.value.set_string("name", material_override.name)
                surface.value.set_uuid(material_override.uuid)
                shader = surface.value

            self.set_pointer("shader_override", shader)
        else:
            self.set_pointer("shader_override", None)
        
    def get_render_region(self):
        return (
            self.get_int("region_min_x"),
            self.get_int("region_min_y"),
            self.get_int("region_max_x"),
            self.get_int("region_max_y"),
        )

    def set_render_region(self, min_x, min_y, max_x, max_y):
        if self.is_valid:
            self.set_int("region_min_x", min_x)
            self.set_int("region_min_y", min_y)
            self.set_int("region_max_x", max_x)
            self.set_int("region_max_y", max_y)
    
    def set_render_resolution(self, x, y):
        if self.is_valid:
            self.set_int("xres", x)
            self.set_int("yres", y)

    def get_render_resolution(self):
        if self.is_valid:
            return self.get_int("xres"), self.get_int("yres")

        return None, None