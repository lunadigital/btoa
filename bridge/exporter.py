import arnold
import bpy
import datetime
import math
import numpy

from pathlib import Path

from . import config
from . import utils

def get_data_from_collection():
    pass

def get_target_frame(step):
    pass

def get_transform(engine, datablock, motion_blur=False, start=0, end=0, motion_keys=0):
    if motion_blur:
        result = arnold.AiArrayAllocate(1, motion_keys, arnold.AI_TYPE_MATRIX)
        steps = numpy.linspace(start, end, motion_keys)

        for i in range(0, steps.size):
            frame, subframe = get_target_frame(steps[i])
            engine.frame_set(frame, subframe=subframe)

            

        
    else:
        return utils.format_matrix(datablock.matrix_world)

def export_options(depsgraph, ipr=False, region=None):
    scene = depsgraph.scene
    render = scene.render
    ai = scene.arnold
    prefs = bpy.context.preferences.addons[config.BTOA_PACKAGE_NAME].preferences
    options = arnold.AiUniverseGetOptions()

    # Render resolution

    x, y = utils.get_render_resolution(depsgraph, ipr, region)
    arnold.AiNodeSetInt(options, 'xres', x)
    arnold.AiNodeSetInt(options, 'yres', y)

    if render.use_border:
        min_x = int(x * render.border_min_x)
        min_y = int(math.ceil(y * (1 - render.border_max_y)))

        '''
        I don't understand why, but subtracting 1px here avoids
        weird render artifacts.
        '''
        max_x = int(x * render.border_max_x) - 1
        max_y = int(math.ceil(y * (1 - render.border_min_y)))

        arnold.AiNodeSetInt(options, 'region_min_x', min_x)
        arnold.AiNodeSetInt(options, 'region_min_y', min_y)
        arnold.AiNodeSetInt(options, 'region_max_x', max_x)
        arnold.AiNodeSetInt(options, 'region_max_y', max_y)

    # General universe options

    arnold.AiNodeSetInt(options, 'render_device', int(ai.render_device))
    arnold.AiNodeSetInt(options, 'AA_samples', ai.aa_samples)
    arnold.AiNodeSetInt(options, 'GI_diffuse_samples', ai.diffuse_samples)
    arnold.AiNodeSetInt(options, 'GI_specular_samples', ai.specular_samples)
    arnold.AiNodeSetInt(options, 'GI_transmission_samples', ai.transmission_samples)
    arnold.AiNodeSetInt(options, 'GI_sss_samples', ai.sss_samples)
    arnold.AiNodeSetInt(options, 'GI_volume_samples', ai.volume_samples)
    arnold.AiNodeSetFlt(options, 'indirect_sample_clamp', ai.indirect_sample_clamp)
    arnold.AiNodeSetFlt(options, 'low_light_threshold', ai.low_light_threshold)
    arnold.AiNodeSetBool(options, 'enable_adaptive_sampling', ai.use_adaptive_sampling)
    arnold.AiNodeSetInt(options, 'AA_samples_max', ai.adaptive_aa_samples_max)
    arnold.AiNodeSetFlt(options, 'AA_adaptive_threshold', ai.adaptive_threshold)
    arnold.AiNodeSetInt(options, 'GI_total_depth', ai.total_depth)
    arnold.AiNodeSetInt(options, 'GI_diffuse_depth', ai.diffuse_depth)
    arnold.AiNodeSetInt(options, 'GI_specular_depth', ai.specular_depth)
    arnold.AiNodeSetInt(options, 'GI_transmission_depth', ai.transmission_depth)
    arnold.AiNodeSetInt(options, 'GI_volume_depth', ai.volume_depth)
    arnold.AiNodeSetInt(options, 'auto_transparency_depth', ai.transparency_depth)
    arnold.AiNodeSetInt(options, 'bucket_size', ai.bucket_size)
    arnold.AiNodeSetStr(options, 'bucket_scanning', ai.bucket_scanning)
    arnold.AiNodeSetBool(options, 'parallel_node_init', ai.parallel_node_init)
    arnold.AiNodeSetInt(options, 'threads', ai.threads)
    
    seed = 1 if ai.lock_sampling_pattern else scene.frame_current
    arnold.AiNodeSetInt(options, 'AA_seed', seed)

    if scene.clamp_aa_samples:
        arnold.AiNodeSetFlt(options, 'AA_sample_clamp', scene.sample_clamp)
        arnold.AiNodeSetBool(options, 'AA_sample_clamp_affects_aovs', scene.clamp_aovs)

    # Logging & licensing

    arnold.AiNodeSetBool(options, 'abort_on_license_fail', prefs.abort_on_license_fail)
    arnold.AiNodeSetBool(options, 'skip_license_check', prefs.skip_license_check)

    if prefs.log_to_file: 
        folder = prefs.log_path if prefs.log_path else Path.home()
        Path(folder).mkdir(parents=True, exist_ok=True)

        timestamp = str(datetime.now()).replace(" ", "-").replace(":", "-").split(".")[0]
        filepath = str(Path(folder).join(f'arnold-{timestamp}.log'))
        arnold.AiMsgSetLogFileName(filepath)

    if not ipr:
        if prefs.log_all:
            arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_ALL)
        else:
            arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_NONE)

            if prefs.log_info:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_INFO)
            
            if prefs.log_warnings:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_WARNINGS)

            if prefs.log_errors:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_ERRORS)
            
            if prefs.log_debug:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_DEBUG)
            
            if prefs.log_stats:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_STATS)

            if prefs.log_plugins:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_PLUGINS)

            if prefs.log_progress:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_PROGRESS)
            
            if prefs.log_nan:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_NAN)

            if prefs.log_timestamp:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_TIMESTAMP)

            if prefs.log_backtrace:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_BACKTRACE)

            if prefs.log_memory:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_MEMORY)

            if prefs.log_color:
                arnold.AiMsgSetConsoleFlags(arnold.AI_LOG_COLOR)
    
    # Ignore flags

    arnold.AiNodeSetBool(options, 'ignore_textures', ai.ignore_textures)
    arnold.AiNodeSetBool(options, 'ignore_shaders', ai.ignore_shaders)
    arnold.AiNodeSetBool(options, 'ignore_atmosphere', ai.ignore_atmosphere)
    arnold.AiNodeSetBool(options, 'ignore_lights', ai.ignore_lights)
    arnold.AiNodeSetBool(options, 'ignore_shadows', ai.ignore_shadows)
    arnold.AiNodeSetBool(options, 'ignore_subdivision', ai.ignore_subdivision)
    arnold.AiNodeSetBool(options, 'ignore_displacement', ai.ignore_displacement)
    arnold.AiNodeSetBool(options, 'ignore_bump', ai.ignore_displacement)
    arnold.AiNodeSetBool(options, 'ignore_motion', ai.ignore_motion)
    arnold.AiNodeSetBool(options, 'ignore_dof', ai.ignore_dof)
    arnold.AiNodeSetBool(options, 'ignore_smoothing', ai.ignore_smoothing)
    arnold.AiNodeSetBool(options, 'ignore_sss', ai.ignore_sss)
    arnold.AiNodeSetBool(options, 'ignore_imagers', ai.ignore_imagers)

    # Denoising

    driver = arnold.AiNodeLookUpByName('btoa_driver')
    denoiser = arnold.AiNodeGetPtr(driver, 'input')

    if denoiser:
        arnold.AiNodeDestroy(denoiser)

    # Misc. settings

    if not render.film_transparent:
        shader = arnold.AiNode('flat')
        arnold.AiNodeSetStr(shader, 'name', 'film_background')
        arnold.AiNodeSetRGB(shader, 'color', 0, 0, 0)
        arnold.AiNodeSetPtr(options, 'background', shader)
    
    if ipr:
        arnold.AiNodeSetBool(options, 'enable_progressive_render', True)
        arnold.AiNodeSetBool(options, 'enable_dependency_graph', True)

        if ai.enable_viewport_denoising:
            denoiser = arnold.AiNode(ai.viewport_denoiser)
            arnold.AiNodeSetPtr(driver, 'input', denoiser)
        '''
        elif scene.enable_render_denoising:
            denoiser = arnold.AiNode('imager_denoiser_noice')
            arnold.AiNodeSetPtr(driver, 'input', denoiser)
        '''

def export_polymesh(engine, depsgraph, depsgraph_object, node=None):
    scene = depsgraph.scene
    ai = scene.arnold

    # Validate datablock
    datablock_eval = None

    if isinstance(depsgraph_object, bpy.types.DepsgraphObjectInstance):
        datablock_eval = utils.data_from_instance(depsgraph_object)
    elif isinstance(depsgraph_object, bpy.types.DepsgraphUpdate):
        datablock_eval = depsgraph_object.id

    if not datablock_eval:
        raise ValueError('BtoA can only export objects of type DepsgraphObjectInstance or Depsgraph Update.')

    # Validate Arnold node
    if not node:
        node = arnold.AiNode('polymesh')
        arnold.AiNodeSetStr(node, 'name', self.datablock_eval.name)
        utils.set_uuid(node, datablock_eval.uuid)

    # Prep mesh for export
    mesh = self.datablock_eval.to_mesh()
    mesh.calc_normals_split()

    # Ensure UV map
    if len(mesh.uv_layers) == 0:
        mesh.uv_layers.new(name='UVMap')

    # Export mesh data


    # Subdiv settings
    data = self.datablock_eval.arnold

    arnold.AiNodeSetStr(node, 'subdiv_type', data.subdiv_type)
    arnold.AiNodeSetByte(node, 'subdiv_iterations', data.subdiv_iterations)
    arnold.AiNodeSetFlt(node, 'subdiv_adaptive_error', data.subdiv_adaptive_error)
    arnold.AiNodeSetStr(node, 'subdiv_adaptive_metric', data.subdiv_adaptive_metric)
    arnold.AiNodeSetStr(node, 'subdiv_adaptive_space', data.subdiv_adaptive_space)
    arnold.AiNodeSetBool(node, 'subdiv_frustrum_ignore', data.subdiv_frustrum_ignore)
    arnold.AiNodeSetStr(node, 'subdiv_uv_smoothing', data.subdiv_uv_smoothing)
    arnold.AiNodeSetBool(node, 'subdiv_smooth_derivs', data.subdiv_smooth_derivs)

    # Everything else
    arnold.AiNodeSetBool(node, 'smoothing', True)
    arnold.AiNodeSetFlt(node, 'motion_start', ai.shutter_start)
    arnold.AiNodeSetFlt(node, 'motion_end', ai.shutter_end)

    self.datablock_eval.to_mesh_clear()

def export_light(depsgraph, obj, ipr=False):
    pass