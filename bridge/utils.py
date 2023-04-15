import math
import numpy as np

def data_from_instance(datablock):
    return datablock.instance_object if datablock.is_instance else datablock.object

def get_render_resolution(depsgraph, ipr=False, region=None):
    if ipr:
        scene = depsgraph.scene

        x = int(region.width * scene.viewport_scale)
        y = int(region.height * scene.viewport_scale)
    else:
        render = depsgraph.scene.render
        scale = render.resolution_percentage / 100.0

        x = int(render.resolution_x * scale)
        y = int(render.resolution_y * scale)
    
    return x, y

def set_uuid(ainode, uuid):
    '''
    Sets a custom UUID to help us track nodes during a render
    session. It's not an interal Arnold param so we need to
    create it ourselves.
    '''
    arnold.AiNodeDeclare(ainode, 'btoa_id', 'constant STRING')
    arnold.AiNodeSetStr(ainode, 'btoa_id', uuid)

def get_data_from_collection(collection, attribute, size, dtype=np.float32):
    data = np.zeros(np.prod(size), dtype=dtype)
    collection.foreach_get(attribute, data)
    return data.reshape(size)

def get_frame_target(frame_current, step):
    target = frame_current + step
    return math.floor(target), target - target # frame, subframe