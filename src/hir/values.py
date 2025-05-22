from abc import abstractmethod, ABC
import src.hir.types as hir_types

class Value(ABC):
    pass

class NamedValue(Value):
    name_prefix = '%'
    deduplicate_name = True

    def __init__(self, parent, type: hir_types.Type, name):
        self.parent = parent
        self.type = type
        self.name = self.parent.scope.register(name) if self.deduplicate_name else name


class ConstantValue(Value):
    def __init__(self, type: hir_types.Type, value):
        self.type = type
        self.value = value

class GlobalValue(NamedValue):
    name_prefix = '@'
    deduplicate_name = False

class GlobalVariable(GlobalValue):
    def __init__(self, module, type: hir_types.Type, name, init_value=None):
        super(GlobalVariable, self).__init__(module, type, name)
        self.init_value = init_value

class Argument(NamedValue):
    def __init__(self, parent, type: hir_types.Type, name=""):
        super(Argument, self).__init__(parent, type, name)

class ReturnValue(NamedValue):
    pass

class Function(GlobalValue):
    def __init__(self, module, ftype: hir_types.FunctionType, name, arg_names=None):
        super(Function, self).__init__(module, hir_types.PointerType(), name=name)
        self.ftype = ftype
        self.scope = module.scope.child()
        self.blocks = []
        arg_names = arg_names or ["" for _ in ftype.args]
        self.args = tuple([Argument(self, tp, name) for tp, name in zip(ftype.args,arg_names)])
        self.return_value = ReturnValue(self, ftype.return_type, self.name)

class Block(NamedValue):
    def __init__(self, parent, name=""):
        super(Block, self).__init__(parent, hir_types.LabelType(), name)
        self.instructions = []
        self.terminator = None