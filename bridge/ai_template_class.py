class AiTemplateClass:
    def __init__(self):
        self.data = None

    @property
    def is_valid(self):
        return self.data is not None

    # This does not do an is_valid check so we can create empty
    # ArnoldNodes and dynamically add data to them
    def set_data(self, data):
        self.data = data