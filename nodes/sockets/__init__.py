from . import ainodesocketcolor
from . import ainodesocketcoord
from . import ainodesocketfloat
from . import ainodesocketint
from . import ainodesocketsurface
from . import ainodesocketvector

modules = (
    ainodesocketcolor,
    ainodesocketcoord,
    ainodesocketfloat,
    ainodesocketint,
    ainodesocketsurface,
    ainodesocketvector
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()