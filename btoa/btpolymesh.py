from .btnode import BtNode

class BtPolymesh(BtNode):
    def __init__(self, name):
        super().__init__("polymesh")
        self.set_string("name", name)