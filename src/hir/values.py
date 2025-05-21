from abc import abstractmethod, ABC
import src.hir.types as hir_types

class Value(ABC):
    pass

class NamedValue(Value):
    def __init__(self, parent, type: hir_types.Type, name):
        self.parent = parent
        self.type = type
        self.name = name

class ConstantValue(Value):
    pass

class GlobalValue(NamedValue):
    pass

class GlobalVariable(GlobalValue):
    def __init__(self, module, type: hir_types.Type, name, init_value=None):
        super(GlobalVariable, self).__init__(module, type, name)
        self.init_value = init_value

class Argument(NamedValue):
    pass

class ReturnValue(NamedValue):
    pass

class Function(GlobalValue):
    def __init__(self, module, ftype: hir_types.FunctionType, name):
        super(Function, self).__init__(module, hir_types.PointerType(), name=name)
        self.ftype = ftype
        self.scope = _utils.NameScope()
        self.blocks = []
        self.args = tuple([Argument(self, t) for t in ftype.args])
        self.return_value = ReturnValue(self, ftype.return_type)

class Block(NamedValue):
    def __init__(self, parent, name=""):
        super(Block, self).__init__(parent, hir_types.LabelType(), name)
        self.instructions = []
        self.terminator = None