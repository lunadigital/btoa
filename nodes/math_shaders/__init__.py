from . import (
    airange,
    multiply
)

modules = (
    airange,
    multiply
)

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()