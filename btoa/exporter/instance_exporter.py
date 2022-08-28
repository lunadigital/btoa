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

        '''
        We know the `objects` variable is a pre-validated list
        of ArnoldNode types.

        If the node is marked as `is_instance`, it means there's already
        another node in the Arnold scene graph we want to point to. If it's
        not, it means the original objects aren't currently visible in the
        scene so we need to create them and hide them.
        '''
        for ob in objects:
            node = ob
            
            if not node.is_instance:
                if isinstance(ob.data, BTOA_CONVERTIBLE_TYPES):
                    node = PolymeshExporter(self.session).export(ob)
                elif isinstance(ob.data, bpy.types.Light):
                    #node = LightExporter(self.session).export(ob)
                    pass

                #visibility = node.get_byte("visibility")
                #visibility = max(visibility - 3, 0)
                #node.set_byte("visibility", visibility)
            
            nodes.append(node)

        # Set up instancer node
        self.node = ArnoldNode('instancer')

        array = ArnoldArray()
        array.allocate(len(nodes), 1, 'POINTER')
        self.node.set_string("name", parent.name)
        self.node.set_uuid(parent.uuid)

        for i, node in enumerate(nodes):
            array.set_pointer(i, node)
        
        self.node.set_array("nodes", array)
        
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