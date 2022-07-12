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
        params = [
            self.matrix_world != camera.matrix_world,
            self.ortho_scale != camera.data.ortho_scale and camera.data.arnold.camera_type == "ortho_camera",
            self.zoom != camera.data.zoom,
            self.offset != tuple(list(camera.data.offset)),
            self.angle != camera.data.angle,
            self.clip_start != camera.data.clip_start,
            self.clip_end != camera.data.clip_end
        ]

        if any(params):
            return True

        return False