from src.hir.utils import Scope
from src.hir.values import GlobalValue

class Module:
    def __init__(self, name=""):
        self.name = name
        self.globals = []
        self.scope = Scope()

    def add_global(self, value):
        """
        Add a new global value.
        """
        assert not isinstance(value, GlobalValue)
        self.globals.append(value)