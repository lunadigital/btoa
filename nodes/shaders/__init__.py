from . import lambert
from . import output

def register():
    lambert.register()
    output.register()

def unregister():
    lambert.unregister()
    output.unregister()