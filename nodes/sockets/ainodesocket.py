import bpy
from . import utils

class SocketColor:
    FLOAT = (0.62745098, 0.62745098, 0.62745098, 1) # gray
    INTEGER = (0.37254902, 0.549019608, 0.360784314, 1) # green
    VECTOR = (0.380392157, 0.4, 0.776470588, 1) # dark blue
    COLOR = (0.780392157, 0.768627451, 0.17254902, 1) # yellow
    SHADER = (0.439215686, 0.776470588, 0.388235294, 1) # bright green
    
class AiNodeSocket:
    bl_label = ""
    default_type = None
    slider = True

    def draw_prop(self, context, layout, node, text):
        ''' This method can be overridden by subclasses as-needed '''
        layout.prop(self, "default_value", text=text, slider=self.slider)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            self.draw_prop(context, layout, node, text)
    
    def draw_color(self, context, node):
        return self.color

    def export_default(self):
        ''' Subclasses have to implement this method '''
        return None

    def export(self):
        rgba_outputs = ['', 'r', 'g', 'b', 'a']
        vector_outputs = ['', 'x', 'y', 'z']

        link = utils.get_link(self)

        if link:
            socket_index = utils.get_socket_index(link.from_socket)
            output_type = vector_outputs[socket_index] if hasattr(link.from_socket, 'default_value') and isinstance(link.from_socket.default_value, bpy.types.FloatProperty) else rgba_outputs[socket_index]

            return *link.from_node.export(), output_type
        elif hasattr(self, "default_value"):
            return *self.export_default(), ''
        else:
            return None