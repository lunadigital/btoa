from . import utils

class AiNodeSocket:
    bl_label = ""

    color = (1, 1, 1, 1)
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
        link = utils.get_link(self)

        if link:
            socket_index = int(link.from_socket.path_from_id()[-2:-1])
            return link.from_node.export(socket_index)
        elif hasattr(self, "default_value"):
            return self.export_default()
        else:
            return None