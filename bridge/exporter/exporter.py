from ..node import ArnoldNode

class Exporter:
    def __init__(self, depsgraph, node=None):
        #self.session = session
        #self.cache = session.cache

        self.depsgraph = depsgraph

        if not node:
            self.node = ArnoldNode()
        else:
            self.node = node

    def export(self, datablock):
        self.datablock = datablock