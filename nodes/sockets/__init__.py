from . import ainodesocketcolor
from . import ainodesocketfloat
from . import ainodesocketsurface

def register():
    ainodesocketcolor.register()
    ainodesocketfloat.register()
    ainodesocketsurface.register()

def unregister():
    ainodesocketcolor.unregister()
    ainodesocketfloat.unregister()
    ainodesocketsurface.unregister()