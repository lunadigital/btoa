from ..node import ArnoldNode

class Exporter:
    def __init__(self, session, node=None):
        self.session = session
        self.cache = session.cache

        if not node:
            self.node = ArnoldNode()
        else:
            self.node = node

    def export(self, datablock):
        self.datablock = datablock