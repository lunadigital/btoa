class CameraCache:
    def __init__(self):
        self.matrix_world = None
        self.ortho_scale = None
        self.camera_type = None
        self.zoom = 0
        self.offset = (0, 0)
        self.angle = 0.610865
        self.clip_start = 0.01
        self.clip_end = 1000

    def __matrix_changed(self, camera):
        return self.matrix_world != camera.matrix_world

    def __ortho_scale_changed(self, camera):
        return camera.data.arnold.camera_type == "ortho_camera" and camera.data.ortho_scale != self.ortho_scale
    
    def __view_zoom_changed(self, camera):
        return self.zoom != camera.data.zoom
    
    def __view_offset_changed(self, camera):
        return self.offset != tuple(list(camera.data.offset))

    def __camera_settings_changed(self, camera):
        if (
            self.angle != camera.data.angle
            or self.clip_start != camera.data.clip_start
            or self.clip_end != camera.data.clip_end
        ):
            return True

        return False

    def sync(self, camera):
        self.matrix_world = camera.matrix_world
        self.ortho_scale = camera.data.ortho_scale
        self.camera_type = camera.data.arnold.camera_type
        self.zoom = camera.data.zoom
        self.offset = tuple(list(camera.data.offset))
        self.angle = camera.data.angle
        self.clip_start = camera.data.clip_start
        self.clip_end = camera.data.clip_end

    def redraw_required(self, camera):
        if (
            self.__matrix_changed(camera)
            or self.__ortho_scale_changed(camera)
            or self.__view_zoom_changed(camera)
            or self.__view_offset_changed(camera)
            or self.__camera_settings_changed(camera)
        ):
            return True

        return False