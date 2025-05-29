from abc import abstractmethod, ABC
import src.hir.types as hir_types
import string

_VALID_CHARS = (frozenset(map(ord, string.ascii_letters)) |
                frozenset(map(ord, string.digits)) |
                frozenset(map(ord, ' !#$%&\'()*+,-./:;<=>?@[]^_`{|}~')))

def _escape_string(text, _map={}):
    """
    Escape the given bytestring for safe use as a LLVM array constant.
    Any unicode string input is first encoded with utf8 into bytes.
    """
    if isinstance(text, str):
        text = text.encode()
    assert isinstance(text, (bytes, bytearray))

    if not _map:
        for ch in range(256):
            if ch in _VALID_CHARS:
                _map[ch] = chr(ch)
            else:
                _map[ch] = '\\%02x' % ch

    buf = [_map[ch] for ch in text]
    return ''.join(buf)

class Value(ABC):
    def get_reference(self):
        raise NotImplementedError()

class NamedValue(Value):
    name_prefix = '%'
    deduplicate_name = True
    empty_name = "<empty>"

    def __init__(self, parent, type: hir_types.Type, name):
        self.parent = parent
        self.type = type
        self.name = name
        if self.name != NamedValue.empty_name and self.deduplicate_name:
            self.name = self.parent.scope.register(name)

    def get_reference(self):
        name = self.name
        # Quote and escape value name
        if '\\' in name or '"' in name:
            name = name.replace('\\', '\\5c').replace('"', '\\22')
        return '{0}{1}'.format(self.name_prefix, name)

    def deduplicate(self):
        self.name = self.parent.scope.register(self.name)

class ConstantValue(Value):
    def __init__(self, type: hir_types.Type, value):
        self.type = type
        self.value = value
        if isinstance(self.value, str):
            self.value += '\0'

    def __str__(self):
        return '{0} {1}'.format(self.type, self.value)

    def get_reference(self):
        if self.value is None:
            val = self.type.null

        elif isinstance(self.value, bytearray):
            val = 'c"{0}"'.format(_escape_string(self.value))
        elif not isinstance(self.type, hir_types.PointerType) and isinstance(self.value, str):
            val = 'c"{0}"'.format(self.value.replace('\n', '\\n').replace('\0', '\\0'))
        else:
            val = self.type.format_constant(self.value)

        return val

class GlobalValue(NamedValue):
    name_prefix = '@'
    deduplicate_name = False

class GlobalVariable(GlobalValue):
    def __init__(self, module, type: hir_types.Type, name, init_value=None):
        super(GlobalVariable, self).__init__(module, hir_types.PointerType(), name)
        self.value_type = type
        self.init_value = init_value
        self.global_constant = False

    def __str__(self):
        if self.global_constant:
            kind = 'constant'
        else:
            kind = 'global'

        result = f"{self.get_reference()} = {kind} {self.value_type}"
        if self.init_value is not None:
            if self.init_value.type != self.value_type:
                raise TypeError("got initializer of type %s "
                                "for global value type %s"
                                % (self.init_value.type, self.value_type))
            result += f" {self.init_value.get_reference()}"
        return result

class Argument(NamedValue):
    def __init__(self, parent, type: hir_types.Type, name=""):
        super(Argument, self).__init__(parent, type, name)

    def __str__(self):
        return "{0} {1}".format(self.type, self.get_reference())

class ReturnValue(NamedValue):
    def __str__(self):
        return str(self.type)

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

    @property
    def module(self):
        return self.parent

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

    def __str__(self):
        state = "define" if self.blocks else "declare"
        ret = self.return_value
        args = ", ".join(str(a) for a in self.args)
        name = self.get_reference()
        prefix = " ".join(str(x) for x in [state, ret] if x)
        result = f"{prefix} {name}({args})"
        if self.blocks:
            result += f"{{\n{ '\n'.join(list(map(str, self.blocks))) }}}\n"
        return result

class Block(NamedValue):
    def __init__(self, parent, name=""):
        super(Block, self).__init__(parent, hir_types.LabelType(), name)
        self.instructions = []
        self.terminator = None

    @property
    def scope(self):
        return self.parent.scope

    @property
    def is_terminated(self):
        return self.terminator is not None

    def __str__(self):
        body = ''.join([f"  {instr}\n" for instr in self.instructions])
        return f"{self.name}:\n{body}"


class HirDefaultValues:
    @staticmethod
    def get(tp: hir_types.Type):
        match type(tp):
            case t if t is hir_types.VoidType:
                return ConstantValue(tp, 'None')
            case t if t is hir_types.IntType:
                return ConstantValue(tp, 0)
            case t if t is hir_types.LongType:
                return ConstantValue(tp, 0)
            case t if t is hir_types.FloatType:
                return ConstantValue(tp, 0.0)
            case t if t is hir_types.DoubleType:
                return ConstantValue(tp, 0.0)
            case t if t is hir_types.BoolType:
                return ConstantValue(tp, False)
            case t if t is hir_types.PointerType:
                return ConstantValue(tp, hir_types.PointerType.null)
            case t if t is hir_types.ArrayType:
                return ConstantValue(tp, [HirDefaultValues.get(tp.element) for _ in range(tp.count)])
        raise ValueError(f"Unexpected type: {tp}")
