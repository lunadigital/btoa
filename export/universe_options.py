from .node import ArnoldNode
import arnold

class UniverseOptions(ArnoldNode):
    def __init__(self):
        super().__init__()
        self.data = arnold.AiUniverseGetOptions()
    
    def get_render_region(self):
        return (
            self.get_int("region_min_x"),
            self.get_int("region_min_y"),
            self.get_int("region_max_x"),
            self.get_int("region_max_y"),
        )

    def set_render_region(self, min_x=None, min_y=None, max_x=None, max_y=None):
        if min_x and self.is_valid():
            self.set_int("region_min_x", min_x)
        
        if min_y and self.is_valid():
            self.set_int("region_min_y", min_y)

        if max_x and self.is_valid():
            self.set_int("region_max_x", max_x)

        if max_y and self.is_valid():
            self.set_int("region_max_y", max_y)
    
    def set_render_resolution(self, x, y):
        if self.is_valid():
            self.set_int("xres", x)
            self.set_int("yres", y)