import bpy
import os
from .exporter import Exporter

from ..node import ArnoldNode
from ..array import ArnoldArray
from .. import utils as export_utils

class VolumeExporter(Exporter):
    def export(self, instance):
        super().export(instance)

        if isinstance(instance, bpy.types.DepsgraphObjectInstance):
            self.datablock_eval = export_utils.get_object_data_from_instance(instance)
        else:
            self.datablock_eval = instance

        # If self.node already exists, it will sync all new
        # data with the existing BtoA node
        if not self.node.is_valid():
            name = export_utils.get_unique_name(self.datablock_eval)

            self.node = ArnoldNode("volume")
            self.node.set_string("name", name)

        matrix = export_utils.flatten_matrix(self.datablock.matrix_world)
        self.node.set_matrix("matrix", matrix)
        
        self.node.set_string("filename", self.get_vdb_filepath())
        self.node.set_float("step_size", 0.1)

        grids = ArnoldArray()
        grids.allocate(5, 1, 'STRING')
        grids.set_string(0, "density")
        grids.set_string(1, "fuel")
        grids.set_string(2, "heat")
        grids.set_string(3, "temperature")
        grids.set_string(4, "velocity")
        self.node.set_array("grids", grids)

        return self.node
    
    def get_vdb_filepath(self):
        modifier = export_utils.get_volume_domain(self.datablock_eval)
        current_frame = self.session.cache.scene["frame_current"]
        
        cache_dir = bpy.path.abspath(modifier.domain_settings.cache_directory)
        data_dir = os.path.join(cache_dir, "data")
        vdb_filename = "fluid_data_{:04d}.vdb".format(current_frame)

        vdb_filepath = os.path.join(data_dir, vdb_filename)

        print("\n\n{}\n\n".format(vdb_filepath))

        return vdb_filepath