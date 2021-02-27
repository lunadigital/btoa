import arnold
from .btnode import BtNode

def start_session():
    arnold.AiBegin()

def end_session():
    arnold.AiEnd()

def free(buffer):
    arnold.AiFree(buffer)

def render():
    arnold.AiRender(arnold.AI_RENDER_MODE_CAMERA)

def abort():
    arnold.AiRenderAbort()

def get_node_by_name(name):
    ainode = arnold.AiNodeLookUpByName(name)

    btnode = BtNode()
    btnode._set_data(ainode)

    return btnode