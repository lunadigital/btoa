import bpy
from os.path import basename, dirname

from .types import ExportDataType
from .status import ArnoldStatus

import arnold

BTOA_PACKAGE_NAME = basename(dirname(dirname(__file__)))

BTOA_TYPE_CONSTANTS = {
    "UINT": arnold.AI_TYPE_UINT,
    "STRING": arnold.AI_TYPE_STRING,
    "MATRIX": arnold.AI_TYPE_MATRIX,
    "ARRAY": arnold.AI_TYPE_ARRAY,
    "VECTOR": arnold.AI_TYPE_VECTOR,
    "VECTOR2": arnold.AI_TYPE_VECTOR2,
    "BYTE": arnold.AI_TYPE_BYTE,
    "POINTER": arnold.AI_TYPE_POINTER,
}

BTOA_LIGHT_CONVERSIONS = {
    "POINT": "point_light",
    "SUN": "distant_light",
    "SPOT": "spot_light"
}

BTOA_LIGHT_SHAPE_CONVERSIONS = {
    "SQUARE": "quad_light",
    "DISK": "disk_light",
    "RECTANGLE": "cylinder_light"
}

BTOA_CONVERTIBLE_TYPES = (
    bpy.types.Mesh,
    bpy.types.TextCurve,
    bpy.types.Curve
)

# For more info, visit https://docs.arnoldrenderer.com/display/A5NodeRef/polymesh#polymesh-visibility
BTOA_VISIBILITY = [1, 2, 4, 8, 16, 32, 64, 128]

BTOA_SET_LAMBDA = {
    ExportDataType.STRING: lambda n, i, v: n.set_string(i, v),
    ExportDataType.BOOL: lambda n, i, v: n.set_bool(i, v),
    ExportDataType.BYTE: lambda n, i, v: n.set_byte(i, v),
    ExportDataType.INT: lambda n, i, v: n.set_int(i, v),
    ExportDataType.FLOAT: lambda n, i, v: n.set_float(i , v),
    ExportDataType.RGB: lambda n, i, v: n.set_rgb(i, *v),
    ExportDataType.RGBA: lambda n, i, v: n.set_rgba(i, *v),
    ExportDataType.VECTOR: lambda n, i, v: n.set_vector(i, *v),
    ExportDataType.VECTOR2: lambda n, i, v: n.set_vector2(i, *v),
}

# Display output statuses
NO_DISPLAY_OUTPUTS = ArnoldStatus(arnold.AI_DISPLAY_OUTPUT_NONE)
PARTIAL_INTERACTIVE_OUTPUT = ArnoldStatus(arnold.AI_DISPLAY_OUTPUT_PARTIAL_INTERACTIVE)
INTERACTIVE_OUTPUT = ArnoldStatus(arnold.AI_DISPLAY_OUTPUT_INTERACTIVE)
ALL_OUTPUTS = ArnoldStatus(arnold.AI_DISPLAY_OUTPUT_ALL)

# Update statuses
INTERRUPTED = ArnoldStatus(arnold.AI_RENDER_UPDATE_INTERRUPT)
BEFORE_PASS = ArnoldStatus(arnold.AI_RENDER_UPDATE_BEFORE_PASS)
DURING_PASS = ArnoldStatus(arnold.AI_RENDER_UPDATE_DURING_PASS)
AFTER_PASS = ArnoldStatus(arnold.AI_RENDER_UPDATE_AFTER_PASS)
UPDATE_FINISHED = ArnoldStatus(arnold.AI_RENDER_UPDATE_FINISHED)
ERROR = ArnoldStatus(arnold.AI_RENDER_UPDATE_ERROR)
#UPDATE_IMAGERS = ArnoldStatus(arnold.AI_RENDER_UPDATE_IMAGERS)

# Render statuses
NOT_STARTED = ArnoldStatus(arnold.AI_RENDER_STATUS_NOT_STARTED)
PAUSED = ArnoldStatus(arnold.AI_RENDER_STATUS_PAUSED)
RESTARTING = ArnoldStatus(arnold.AI_RENDER_STATUS_RESTARTING)
RENDERING = ArnoldStatus(arnold.AI_RENDER_STATUS_RENDERING)
RENDER_FINISHED = ArnoldStatus(arnold.AI_RENDER_STATUS_FINISHED)
FAILED = ArnoldStatus(arnold.AI_RENDER_STATUS_FAILED)