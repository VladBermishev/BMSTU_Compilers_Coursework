from abc import abstractmethod, ABC
import struct

def _format_float_as_hex(value, packfmt, unpackfmt, numdigits):
    raw = struct.pack(packfmt, float(value))
    intrep = struct.unpack(unpackfmt, raw)[0]
    out = '{{0:#{0}x}}'.format(numdigits).format(intrep)
    return out


def _format_double(value):
    """
    Format *value* as a hexadecimal string of its IEEE double precision
    representation.
    """
    return _format_float_as_hex(value, 'd', 'Q', 16)

def _as_float(value):
    """
    Truncate to single-precision float.
    """
    return struct.unpack('f', struct.pack('f', value))[0]

class Type(ABC):
    null = 'zeroinitializer'
    mangle_suff = "T"
    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return isinstance(other, type(self))

    def format_constant(self, value):
        return str(value)

    def is_integral(self):
        return type(self) in [BoolType, IntType, LongType]
    def is_floating_point(self):
        return type(self) in [FloatType, DoubleType]

    def is_array(self):
        return type(self) is ArrayType

    def is_struct(self):
        return type(self) is StructType

    def is_pointer(self):
        return type(self) is PointerType

    def is_function(self):
        return type(self) is FunctionType

class VoidType(Type):
    mangle_suff = ""
    def __str__(self):
        return 'void'

# opaque-like
class PointerType(Type):
    mangle_suff = "P"
    null = 'null'

    def __str__(self):
        return 'ptr'

class FunctionType(Type):
    mangle_suff = "F"
    def __init__(self, return_type, args):
        self.args = tuple(args)
        self.return_type = return_type

    def __str__(self):
        return f'{str(self.return_type)}({', '.join(map(str, self.args))})'

class BoolType(Type):
    mangle_suff = "B"
    null = '0'
    def __str__(self):
        return 'i1'

    def format_constant(self, val):
        return str(val).lower()

class IntType(Type):
    mangle_suff = "I"
    null = '0'
    def __str__(self):
        return 'i32'

class LongType(Type):
    mangle_suff = "L"
    null = '0'
    def __str__(self):
        return 'i64'

class FloatType(Type):
    mangle_suff = "F"
    null = '0.0'
    def __str__(self):
        return 'float'
    def format_constant(self, value):
        return _format_double(_as_float(value)).strip()

class DoubleType(Type):
    mangle_suff = "D"
    null = '0.0'
    def __str__(self):
        return 'double'
    def format_constant(self, value):
        return _format_double(value).strip()

class ArrayType(Type):
    mangle_suff = "A"
    def __init__(self, array_type, count):
        self.element = array_type
        self.count = count
    def __str__(self):
        return f"[{self.count} x {self.element}]"

    def format_constant(self, value):
        itemstring = ", " .join(["{0} {1}".format(x.type, x.get_reference()) for x in value])
        return "[{0}]".format(itemstring)

class StructType(Type):
    mangle_suff = "S"
    def __init__(self, elements_types):
        self.elements_types = tuple(elements_types)

    def __str__(self):
        return f"{{{', '.join(map(str, self.elements_types))}}}"

class LabelType(Type):
    mangle_suff = "L"
    def __str__(self):
        return "label"

def mangle(name, tp: Type):
    return f"{name}{tp.mangle_suff}"

def sizeof(tp:Type):
    match type(tp):
        case t if t is PointerType:
            return 4
        case t if t is BoolType:
            return 1
        case t if t is IntType:
            return 4
        case t if t is LongType:
            return 8
        case t if t is FloatType:
            return 4
        case t if t is DoubleType:
            return 8
        case t if t is ArrayType:
            return sizeof(tp.element) * tp.count
        case t if t is StructType:
            return sum(map(sizeof, tp.elements_types))
    return 0
