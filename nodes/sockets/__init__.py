from . import ainodesocketcolor
from . import ainodesocketcoord
from . import ainodesocketfloat
from . import ainodesocketint
from . import ainodesocketstate
from . import ainodesocketsurface
from . import ainodesocketvector

modules = (
    ainodesocketcolor,
    ainodesocketcoord,
    ainodesocketfloat,
    ainodesocketint,
    ainodesocketstate,
    ainodesocketsurface,
    ainodesocketvector
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()