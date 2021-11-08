from .node import ArnoldNode

class ArnoldColorManager(ArnoldNode):
    def __init__(self):
        super().__init__("color_manager_ocio")