class ConfError(Exception):
    def __init__(self, error):
        self.parameter = error

    def __str__(self):
        return repr(self.parameter)
