from . import color_correct, constant

def register():
    color_correct.register()
    constant.register()

def unregister():
    color_correct.unregister()
    constant.unregister()