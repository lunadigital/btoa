import bpy
from .object_exporter import ObjectExporter
from .polymesh_exporter import PolymeshExporter
from ..array import ArnoldArray
from ..constants import BTOA_CONVERTIBLE_TYPES
from ..node import ArnoldNode
from ..matrix import ArnoldMatrix
from .. import utils as export_utils

class InstancerCache:
    def __init__(self, parent):
        self.name = parent.name
        self.uuid = parent.uuid
        self.matrix_world = export_utils.flatten_matrix(parent.matrix_world)

class InstanceExporter(ObjectExporter):
    def __init__(self, session):
        super().__init__(session, None)
        self.instance_transform = ArnoldMatrix()

    def export(self, parent, objects):
        # Cache instance offset
        self.instance_transform.convert_from_buffer(parent.matrix_world)

        # Check for existing nodes. If they don't exist, create
        # originals and turn off visibility.
        nodes = []

        for ob in objects:
            node = ob[0]
            bl_visible = ob[1]
            ai_visible = node.get_byte("visibility")
            
            if not bl_visible:
                node.set_byte("visibility", 0)
            
            nodes.append(node)

        # Set up instancer node
        self.node = ArnoldNode('instancer')

        array = ArnoldArray()
        array.allocate(len(nodes), 1, 'POINTER')
        self.node.set_string("name", parent.name)
        self.node.set_uuid(parent.uuid)

        visibility_array = ArnoldArray()
        visibility_array.allocate(len(nodes), 1, 'BYTE')

        for i, node in enumerate(nodes):
            array.set_pointer(i, node)
            visibility_array.set_byte(i, 255)
        
        self.node.set_array("nodes", array)
        self.node.set_array("instance_visibility", visibility_array)

        # Per instance matrices
        array = ArnoldArray()
        array.allocate(len(nodes), 1, 'MATRIX')

        for i, ob in enumerate(objects):
            matrix = ob[0].get_matrix("matrix")
            array.set_matrix(i, matrix)

        self.node.set_array("instance_matrix", array)
        self.node.set_matrix("matrix", self.instance_transform)

        return self.node