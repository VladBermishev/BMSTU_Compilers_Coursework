from src.hir.utils import Scope
from src.hir.values import GlobalValue, Function

class Module:
    def __init__(self, name=""):
        self.name = name
        self.constructors = []
        self.globals = []
        self.scope = Scope()

    def add_global(self, value):
        """
        Add a new global value.
        """
        assert isinstance(value, GlobalValue)
        self.globals.append(value)

    def add_constructor(self, constructor):
        assert isinstance(constructor, Function)
        self.constructors.append(constructor)