import bpy

# TODO: Do we need this anymore now that we have ID.uuid?
def make_nodetree_name(material_name):
    import uuid
    uid = uuid.uuid4()

    return "Ai_{}_{}".format(material_name, uid.hex)

def poll_object(context):
    return context.object and not context.object.library

def init_material_nodetree(ntree):
    ntree.use_fake_user = True

    output = ntree.nodes.new('AiShaderOutput')
    output.location = 300, 200
    output.select = False

    shader = ntree.nodes.new('AiStandardSurface')
    shader.location = 0, 200

    ntree.links.new(shader.outputs[0], output.inputs[0])

def init_world_nodetree(ntree):
    ntree.use_fake_user = True

    output = ntree.nodes.new('AiShaderOutput')
    output.location = 300, 200
    output.select = False

    shader = ntree.nodes.new('AiSkydome')
    shader.location = 0, 200

    ntree.links.new(shader.outputs[0], output.inputs[0])

def get_name_with_lib(datablock):
    '''
    Format the name for display similar to Blender,
    with an "L" as prefix if from a library
    '''
    if datablock.library:
        return f'L {datablock.name}'

    return datablock.name