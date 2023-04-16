import arnold
import bpy
import ctypes
from dataclasses import dataclass
import numpy as np

from .object import ObjectData
from .. import utils

'''
Evaluates mesh data for a single frame.
'''

@dataclass(init=False)
class MeshData:
    vertices: np.ndarray
    normals: np.ndarray
    sides: np.ndarray
    vertex_indices: np.ndarray
    normal_indices: np.arange
    uvidxs: np.arange
    uvlist: np.ndarray

    @staticmethod
    def init_from_mesh(mesh: bpy.types.Mesh):
        # Validate mesh
        if not hasattr(mesh, 'calc_normals_split'):
            log.warn("No calc_normals_split() in mesh", mesh)
            return None

        mesh.calc_normals_split()
        mesh.calc_loop_triangles()

        if len(mesh.loop_triangles) == 0:
            return None

        # Export mesh data
        data = MeshData()

        data.vertices = utils.get_data_from_collection(mesh.vertices, 'co', (len(mesh.vertices), 3))
        data.normals = utils.get_data_from_collection(mesh.loops, 'normal', (len(mesh.loops), 3))
        data.sides = utils.get_data_from_collection(mesh.polygons, 'loop_total', (len(mesh.polygons)), dtype=np.uint32)
        data.vertex_indices = utils.get_data_from_collection(mesh.polygons, 'vertices', (len(mesh.loops)), dtype=np.uint32)
        data.normal_indices = np.arange(len(mesh.loops), dtype=np.uint32)

        for layer in mesh.uv_layers:
            if layer.active_render:
                data.uvidxs = np.arange(len(layer.data), dtype=np.uint32)
                data.uvlist = utils.get_data_from_collection(layer.data, 'uv', (len(layer.data), 2))
                break

        return data

    @staticmethod
    def to_arnold(ob: bpy.types.Object, scene: bpy.types.Scene):
        node = arnold.AiNode('polymesh')

        arnold.AiNodeSetStr(node, 'name', ob.name)
        # set uuid

        # Determine params for motion blur
        start, end, keys = 0, 0, 1

        if scene.arnold.enable_motion_blur:
            start = scene.arnold.shutter_start
            end = scene.arnold.shutter_end
            keys = scene.arnold.motion_keys

        steps = np.linspace(start, end, keys)

        # Export mesh data for each motion key
        ob_data_steps = []
        mesh_data_steps = []

        for step in steps:
            frame, sub = utils.get_frame_target(scene.frame_current, step)
            scene.frame_set(frame, subframe=sub)

            ob_data_steps.append(ObjectData.init_from_object(ob))

            if scene.arnold.deformation_motion_blur:
                mesh_data_steps.append(MeshData.init_from_mesh(ob.data))
            
            scene.frame_set(scene.frame_current)
        
        if not scene.arnold.deformation_motion_blur:
            mesh_data_steps.append(MeshData.init_from_mesh(ob.data))

        # Set matrix transform
        ObjectData.to_arnold(node, ob_data_steps, len(steps))
        
        # Set mesh data
        vlist = np.concatenate(tuple(m.vertices for m in mesh_data_steps))
        vlist = arnold.AiArrayConvert(
            len(mesh_data_steps[0].vertices),
            len(steps),
            arnold.AI_TYPE_VECTOR,
            ctypes.c_void_p(vlist.ctypes.data)
        )

        nlist = np.concatenate(tuple(m.normals for m in mesh_data_steps))
        nlist = arnold.AiArrayConvert(
            len(mesh_data_steps[0].normals),
            len(steps),
            arnold.AI_TYPE_VECTOR,
            ctypes.c_void_p(nlist.ctypes.data)
        )

        nsides = np.concatenate(tuple(m.sides for m in mesh_data_steps))
        nsides = arnold.AiArrayConvert(
            len(mesh_data_steps[0].sides),
            len(steps),
            arnold.AI_TYPE_UINT,
            ctypes.c_void_p(nsides.ctypes.data)
        )

        vidxs = np.concatenate(tuple(m.vertex_indices for m in mesh_data_steps))
        vidxs = arnold.AiArrayConvert(
            len(mesh_data_steps[0].vertex_indices),
            len(steps),
            arnold.AI_TYPE_UINT,
            ctypes.c_void_p(vidxs.ctypes.data)
        )

        nidxs = np.concatenate(tuple(m.normal_indices for m in mesh_data_steps))
        nidxs = arnold.AiArrayConvert(
            len(mesh_data_steps[0].normal_indices),
            len(steps),
            arnold.AI_TYPE_UINT,
            ctypes.c_void_p(nidxs.ctypes.data)
        )

        arnold.AiNodeSetArray(node, 'vlist', vlist)
        arnold.AiNodeSetArray(node, 'nlist', nlist)
        arnold.AiNodeSetArray(node, 'nsides', nsides)
        arnold.AiNodeSetArray(node, 'vidxs', vidxs)
        arnold.AiNodeSetArray(node, 'nidxs', nidxs)

        return node