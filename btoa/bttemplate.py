class BtTemplate:
    def __init__(self):
        self._data = None

    def is_valid(self):
        return self._data is not None

    def _set_data(self, data):
        '''
        For GPL compliance, this should ONLY be called
        from within the BTOA module and shouldn't be
        considered a public method.
        '''
        self._data = data

    def _get_data(self):
        '''
        For GPL compliance, this should ONLY be called
        from within the BTOA module and shouldn't be
        considered a public method.
        '''
        return self._data