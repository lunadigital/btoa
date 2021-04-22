from . import btoa

class Session:
    def __init__(self, depsgraph):
        self.depsgraph = depsgraph
        self.scene = depsgraph.scene
        self.settings = depsgraph.scene.arnold_options
        self.options = btoa.BtOptions()
        self.resolution = self._get_baked_resolution()

        '''
        Blender puts the image origin point (0, 0) in the bottom-left corner
        Arnold puts the image origin point (0, 0) in the top-left corner
        We need to do a little math to flip the coordinates in the y-axis
        '''
        render = self.scene.render
        x, y = self.resolution

        if render.use_border:
            min_x = int(x * render.border_min_x)
            min_y = int(y * (1 - render.border_max_y))
            max_x = int(x * render.border_max_x)
            max_y = int(y * (1 - render.border_min_y))
        else:
            min_x, min_y = 0, 0
            max_x = x
            max_y = y

        self.region = min_x, min_y, max_x, max_y

    def _get_baked_resolution(self):
        render = self.scene.render
        scale = render.resolution_percentage / 100
        
        x = int(render.resolution_x * scale)
        y = int(render.resolution_y * scale)

        return x, y