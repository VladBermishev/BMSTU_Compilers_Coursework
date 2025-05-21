
class Module:
    def __init__(self, name=""):
        self.name = name
        self.globals = []

    def add_global(self, value):
        """
        Add a new global value.
        """
        self.globals.append(value)