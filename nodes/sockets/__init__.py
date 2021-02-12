from . import ainodesocketcolor
from . import ainodesocketcoord
from . import ainodesocketfloat
from . import ainodesocketsurface

def register():
    ainodesocketcolor.register()
    ainodesocketcoord.register()
    ainodesocketfloat.register()
    ainodesocketsurface.register()

def unregister():
    ainodesocketcolor.unregister()
    ainodesocketcoord.unregister()
    ainodesocketfloat.unregister()
    ainodesocketsurface.unregister()