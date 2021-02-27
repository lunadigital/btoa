import arnold
from .btnode import BtNode

class BtOptions(BtNode):
    def __init__(self):
        super().__init__()
        self._data = arnold.AiUniverseGetOptions()