import arnold
import bpy
import time

from . import config
from . import exporter

def abort():
    arnold.AiRenderAbort()

def end(ipr=False):
    if ipr:
        arnold.AiRenderInterrupt()
    
    arnold.AiRenderEnd()
    arnold.AiEnd()

def free(buffer):
    contents = buffer.contents

    for i in range(0, contents.count):
        aov = contents.aovs[i]
        arnold.AiFree(aov.data)

    arnold.AiFree(contents.aovs)
    arnold.AiFree(buffer)

'''
NOTE: We might have to implement something on the server side
once we move to a proper Arnold Server model. Something like,

    def get_all_with_value(value_id, value):
        ...

and used like this:

    node_list = arnoldserver.get_all_with_value('btoa_id', uuid)

'''
def get_all_by_uuid(uuid):
    iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_SHAPE | arnold.AI_NODE_LIGHT | arnold.AI_NODE_SHADER)
    result = []

    while not arnold.AiNodeIteratorFinished(iterator):
        node = arnold.AiNodeIteratorGetNext(iterator)
        
        if arnold.AiNodeGetStr(node, 'btoa_id') == uuid:
            result.append(node)
    
    return result

def get_node_by_uuid(uuid):
    iterator = arnold.AiUniverseGetNodeIterator(arnold.AI_NODE_SHAPE | arnold.AI_NODE_LIGHT | arnold.AI_NODE_SHADER)

    while not arnold.AiNodeIteratorFinished(iterator):
        node = arnold.AiNodeIteratorGetNext(iterator)
        btoa_id = arnold.AiNodeGetStr(node, 'btoa_id')
        
        if btoa_id == uuid:
            return node

def pause():
    arnold.AiRenderInterrupt(arnold.AI_BLOCKING)

def render():
    if arnold.AiRenderBegin() == arnold.AI_SUCCESS.value:
        while arnold.AiRenderGetStatus() == arnold.AI_RENDER_STATUS_RENDERING.value:
            time.sleep(0.001)
    
    end()

def render_ipr(callback):
    result = arnold.AiRenderBegin(
        arnold.AI_RENDER_MODE_CAMERA,
        callback,
        None
    )

    if result != arnold.AI_SUCCESS.value:
        end()

def start(ipr=False):
    mode = arnold.AI_SESSION_INTERACTIVE if ipr else arnold.AI_SESSION_BATCH
    arnold.AiBegin(mode)