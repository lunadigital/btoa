class DummyArnoldCameraData:
    def __init__(self):
        self.camera_type = "persp_camera"
        self.exposure = 0
        self.enable_dof = False
        self.aperture_size = 0
        self.aperture_blades = 0
        self.aperture_rotation = 0
        self.aperture_blade_curvature = 0
        self.aperture_aspect_ratio = 1
        self.flat_field_focus = False

class DummyDOFData:
    def __init__(self):
        self.focus_object = None
        self.focus_distance = 0

class BlenderCameraData:
    def __init__(self):
        self.angle = 0.610865 # 35 deg
        self.sensor_fit = 'AUTO'
        self.arnold = DummyArnoldCameraData()
        self.dof = DummyDOFData()
        self.clip_start = 0.01
        self.clip_end = 1000