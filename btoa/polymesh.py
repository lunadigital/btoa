from .node import ArnoldNode
from . import utils as export_utils

class ArnoldPolymesh(ArnoldNode):
    def __init__(self, name):
        super().__init__("polymesh")
        self.set_string("name", name)