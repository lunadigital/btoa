import math

from .exporter import Exporter
from ..universe_options import UniverseOptions
from ..node import ArnoldNode
from .. import utils as export_utils

class OptionsExporter(Exporter):
    def export(self, interactive=False):
        scene = self.cache.scene
        render = self.cache.render
        prefs = self.cache.preferences

        options = UniverseOptions()

        x, y = export_utils.get_render_resolution(self.cache, interactive=interactive)
        options.set_render_resolution(x, y)

        if render["use_border"]:
            min_x = int(x * render["border_min_x"])
            min_y = int(math.ceil(y * (1 - render["border_max_y"])))
            max_x = int(x * render["border_max_x"]) - 1 # I don't know why, but subtracting 1px here avoids weird render artifacts
            max_y = int(math.ceil(y * (1 - render["border_min_y"])))

            options.set_render_region(min_x, min_y, max_x, max_y)

        options.set_int("render_device", int(scene["render_device"]))

        options.set_int("AA_samples", scene["aa_samples"])
        options.set_int("GI_diffuse_samples", scene["diffuse_samples"])
        options.set_int("GI_specular_samples", scene["specular_samples"])
        options.set_int("GI_transmission_samples", scene["transmission_samples"])
        options.set_int("GI_sss_samples", scene["sss_samples"])
        options.set_int("GI_volume_samples", scene["volume_samples"])

        if scene["clamp_aa_samples"]:
            options.set_float("AA_sample_clamp", scene["sample_clamp"])
            options.set_bool("AA_sample_clamp_affects_aovs", scene["clamp_aovs"])
            
        options.set_float("indirect_sample_clamp", scene["indirect_sample_clamp"])
        options.set_float("low_light_threshold", scene["low_light_threshold"])

        options.set_bool("enable_adaptive_sampling", scene["use_adaptive_sampling"])
        options.set_int("AA_samples_max", scene["adaptive_aa_samples_max"])
        options.set_float("AA_adaptive_threshold", scene["adaptive_threshold"])

        seed = 1 if scene["lock_sampling_pattern"] else scene["frame_current"]
        options.set_int("AA_seed", seed)

        options.set_int("GI_total_depth", scene["total_depth"])
        options.set_int("GI_diffuse_depth", scene["diffuse_depth"])
        options.set_int("GI_specular_depth", scene["specular_depth"])
        options.set_int("GI_transmission_depth", scene["transmission_depth"])
        options.set_int("GI_volume_depth", scene["volume_depth"])
        options.set_int("auto_transparency_depth", scene["transparency_depth"])

        options.set_int("bucket_size", scene["bucket_size"])
        options.set_string("bucket_scanning", scene["bucket_scanning"])
        options.set_bool("parallel_node_init", scene["parallel_node_init"])
        options.set_int("threads", scene["threads"])

        if not render["film_transparent"]:
            bg_shader = ArnoldNode("flat")
            bg_shader.set_string("name", "film_background")
            bg_shader.set_rgb("color", 0, 0, 0)
            options.set_pointer("background", bg_shader)

        if interactive:
            options.set_bool("enable_progressive_render", True)
            options.set_bool("enable_dependency_graph", True)

        options.set_bool("abort_on_license_fail", prefs["abort_on_license_fail"])
        options.set_bool("skip_license_check", prefs["skip_license_check"])
