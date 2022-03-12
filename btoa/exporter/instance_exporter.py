from .object_exporter import ObjectExporter
from ..array import ArnoldArray
from ..node import ArnoldNode
from ..matrix import ArnoldMatrix

class InstanceExporter(ObjectExporter):
    def __init__(self, session):
        super().__init__(session, None)

        self.instance_transform = ArnoldMatrix()

    def set_transform(self, matrix):
        if isinstance(matrix, (ArnoldArray, ArnoldMatrix)):
            self.instance_transform = matrix
        else:
            self.instance_transform.convert_from_buffer(matrix)

    def export(self, node):
        self.node = ArnoldNode("instancer")

        nodes = ArnoldArray()
        nodes.allocate(1, 1, 'POINTER')
        nodes.set_pointer(0, node)
        self.node.set_array("nodes", nodes)

        if self.cache.scene["enable_motion_blur"]:
            node_matricies = node.get_array("matrix", copy=True)

            for i in range(0, node_matricies.get_num_keys()):
                node_mtx = node_matricies.get_matrix(i)
                instance_mtx = self.instance_transform.get_matrix(i)

                node_mtx.multiply(instance_mtx)

                node_matricies.set_matrix(i, node_mtx)
                
            self.node.set_array("instance_matrix", node_matricies)
        else:
            self.node.set_matrix("instance_matrix", self.instance_transform)

        return self.node