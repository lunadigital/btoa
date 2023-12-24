class ArnoldStatus:
    ''' A wrapper class for Arnold display output, render update, and render status constants '''
    
    def __init__(self, status):
        self.data = status
        self.value = status.value

    def __get__(self):
        return self.data
        
    def __int__(self):
        return int(self.value)
    
    def __str__(self):
        return str(self.value)