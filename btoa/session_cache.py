from .camera_cache import CameraCache

class SessionCache:
    '''
    Caches Blender attributes required by an Arnold render session
    in a standard Python dictionary for easy reference.
    '''
    def __init__(self):
        self.scene = {}
        self.render = {}
        self.region = {}
        self.view_layer = None
        self.frame_set = None
        self.viewport_camera = CameraCache()

    def extract_attrs(self, datablock):
        result = {}

        for param in dir(datablock):
            if param[:2] != "__" and param != "bl_rna":
                result[param] = getattr(datablock, param)
        
        return result
        
    def sync(self, engine, depsgraph, context=None):
        self.scene = self.extract_attrs(depsgraph.scene)
        self.scene.update(self.extract_attrs(depsgraph.scene.arnold))

        self.render = self.extract_attrs(depsgraph.scene.render)

        if context:
            self.region = self.extract_attrs(context.region)

        self.view_layer = depsgraph.view_layer_eval
        self.frame_set = engine.frame_set