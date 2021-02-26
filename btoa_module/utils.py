import arnold
from .node import Node

def start_session():
    arnold.AiBegin()

def end_session():
    arnold.AiEnd()

def get_node_by_name(name):
    ainode = arnold.AiNodeLookUpByName(name)

    if ainode is None:
        return None

    btoa_node = Node.__new__(Node)
    btoa_node.set_data(ainode)

    return btoa_node