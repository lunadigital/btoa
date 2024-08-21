import numpy
import gpu
from gpu_extras.presets import draw_texture_2d

class FrameBuffer:
    def __init__(self, dimensions, scale):
        self.dimensions = dimensions
        self.scale = scale
        self.requires_update = False

        width, height = self.get_dimensions()
        buffer_size = width * height * 4
        
        self.buffer = numpy.array([0] * buffer_size, dtype=numpy.float32)
        self._buffer = gpu.types.Buffer('FLOAT', buffer_size, self.buffer)

        self.tag_update()

    def __del__(self):
        del self.texture
        del self._buffer

    def get_dimensions(self, scaling=True):
        width, height = self.dimensions

        if scaling:
            return int(width * self.scale), int(height * self.scale)
        
        return self.dimensions
    
    def draw(self):
        draw_texture_2d(self.texture, (0, 0), *self.get_dimensions(scaling=False))

    def tag_update(self):
        self.requires_update = False
        self.texture = gpu.types.GPUTexture(self.get_dimensions(), format='RGBA16F', data=self._buffer)

    def write_bucket(self, x, y, bucket_width, bucket_height, data):
        width, height = self.get_dimensions()
        index = 0

        for i in range(0, bucket_height):
            length = bucket_width * 4
            start = ((y + i) * width + x) * 4
            end = start + length

            self.buffer[start:end] = data[index:index+length]

            index += length
        
        self.requires_update = True