class CameraCache:
    def __init__(self):
        self.matrix_world = None
        self.ortho_scale = None
        self.camera_type = None
        self.view_camera_zoom = 0
        self.view_camera_offset = (0, 0)

    def __matrix_changed(self, camera):
        return self.matrix_world != camera.matrix_world

    def __ortho_scale_changed(self, camera):
        return camera.data.arnold.camera_type == "ortho_camera" and camera.data.ortho_scale != self.ortho_scale
    
    def __view_zoom_changed(self, camera):
        return self.view_camera_zoom != camera.data.view_camera_zoom
    
    def __view_offset_changed(self, camera):
        return self.view_camera_offset != tuple(list(camera.data.view_camera_offset))

    def sync(self, camera):
        self.matrix_world = camera.matrix_world
        self.ortho_scale = camera.data.ortho_scale
        self.camera_type = camera.data.arnold.camera_type
        self.view_camera_zoom = camera.data.view_camera_zoom
        self.view_camera_offset = tuple(list(camera.data.view_camera_offset))

    def redraw_required(self, camera):
        if (
            self.__matrix_changed(camera)
            or self.__ortho_scale_changed(camera)
            or self.__view_zoom_changed(camera)
            or self.__view_offset_changed(camera)
        ):
            return True

        return False