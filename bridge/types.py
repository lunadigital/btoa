from enum import Enum

class ExportDataType(Enum):
    NODE = 1
    COLOR = 2
    FLOAT = 3
    INT = 4
    VECTOR = 5
    VECTOR2 = 6
    STRING = 7
    BOOL = 8
    BYTE = 9
    RGB = 10
    RGBA = 11
    GROUP = 12

class ExportData:
    def __init__(self, data_type, value):
        self.type = data_type
        self.value = value

class NodeData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.NODE, value)
        self.from_socket = None

class ColorData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.COLOR, value)

    def has_alpha(self):
        return len(self.value) == 4

class FloatData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.FLOAT, value)

class IntData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.INT, value)

class VectorData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.VECTOR, value)

class StringData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.STRING, value)

class DisplacementData(ExportData):
    def __init__(self, value):
        super().__init__(ExportDataType.GROUP, value)