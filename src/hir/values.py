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

    @property
    def last_block(self):
        return self.blocks[-1]

    def append_basic_block(self, name=''):
        blk = Block(parent=self, name=name)
        self.blocks.append(blk)
        return blk

    def insert_basic_block(self, before, name=''):
        """
        Insert block before
        """
        blk = Block(parent=self, name=name)
        self.blocks.insert(before, blk)
        return blk

class Block(NamedValue):
    def __init__(self, parent, name=""):
        super(Block, self).__init__(parent, hir_types.LabelType(), name)
        self.instructions = []
        self.terminator = None

    @property
    def is_terminated(self):
        return self.terminator is not None


class HirDefaultValues:
    @staticmethod
    def get(tp: hir_types.Type):
        match type(tp):
            case t if t is hir_types.VoidType:
                return ConstantValue(tp, 'None')
            case t if t is hir_types.IntType:
                return ConstantValue(tp, 0)
            case t if t is hir_types.FloatType:
                return ConstantValue(tp, 0.0)
            case t if t is hir_types.DoubleType:
                return ConstantValue(tp, 0.0)
            case t if t is hir_types.BoolType:
                return ConstantValue(tp, False)
            case t if t is hir_types.PointerType:
                return ConstantValue(tp, 'null')
            case t if t is hir_types.ArrayType:
                return ConstantValue(tp, [HirDefaultValues.get(tp.element) for _ in tp.count])
        raise ValueError(f"Unexpected type: {tp}")
