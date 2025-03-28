from .ai_template_class import AiTemplateClass

import arnold

class ArnoldMatrix(AiTemplateClass):
    def __init__(self):
        self.data = arnold.AiM4Identity()
        
    def convert_from_buffer(self, data):
        self.data = arnold.AtMatrix(*data)

    def get_data(self):
        return self.data

    def multiply(self, matrix):
        self.data = arnold.AiM4Mult(self.data, matrix.data)