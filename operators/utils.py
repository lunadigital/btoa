import bpy

''' Utility functions for operators '''

def make_nodetree_name(material_name):
    import uuid
    uid = uuid.uuid4()

    return "Ai_{}_{}".format(material_name, uid.hex)

def poll_object(context):
    return context.object and not context.object.library

def init_mat_node_tree(node_tree):
    # Seems like we still need this.
    # User counting does not work reliably with Python PointerProperty.
    # Sometimes, the material this tree is linked to is not counted as user.
    node_tree.use_fake_user = True

    nodes = node_tree.nodes

    output = nodes.new("AiShaderOutput")
    output.location = 300, 200
    output.select = False

    shader = nodes.new("AiStandardSurface")
    shader.location = 0, 200

    node_tree.links.new(shader.outputs[0], output.inputs[0])

def init_world_node_tree(node_tree):
    node_tree.use_fake_user = True

    nodes = node_tree.nodes

    output = nodes.new("AiShaderOutput")
    output.location = 300, 200
    output.select = False

    shader = nodes.new("AiSkydome")
    shader.location = 0, 200

    node_tree.links.new(shader.outputs[0], output.inputs[0])

def get_name_with_lib(datablock):
    '''
    Format the name for display similar to Blender,
    with an "L" as prefix if from a library
    '''
    text = datablock.name

    if datablock.library:
        text = "L " + text

    return text