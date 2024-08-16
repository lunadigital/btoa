import bpy

def make_key(datablock):
    return str(datablock.original.as_pointer())

def generate_uuid(self):
    if isinstance(self, bpy.types.DepsgraphObjectInstance):
        return make_key(self.object)
    elif isinstance(self, bpy.types.DepsgraphUpdate):
        return make_key(self.id)
    elif isinstance(self, bpy.types.SpaceView3D):
        return str(self.as_pointer())
    else:
        return make_key(self)

def register():
    bpy.types.ID.uuid = property(generate_uuid)
    bpy.types.DepsgraphObjectInstance.uuid = property(generate_uuid)
    bpy.types.DepsgraphUpdate.uuid = property(generate_uuid)
    bpy.types.SpaceView3D.uuid = property(generate_uuid)

def unregister():
    del bpy.types.ID.uuid
    del bpy.types.DepsgraphObjectInstance.uuid
    del bpy.types.DepsgraphUpdate.uuid
    del bpy.types.SpaceView3D.uuid