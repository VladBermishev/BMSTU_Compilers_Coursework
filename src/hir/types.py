from abc import abstractmethod, ABC

class Type(ABC):
    mangle_suff = "T"
    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

class VoidType(Type):
    mangle_suff = "V"
    def __str__(self):
        return 'void'

# opaque-like
class PointerType(Type):
    mangle_suff = "P"
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
    def __str__(self):
        return 'i1'

class IntType(Type):
    mangle_suff = "I"
    def __str__(self):
        return 'i32'

class LongType(Type):
    mangle_suff = "L"
    def __str__(self):
        return 'i64'

class FloatType(Type):
    mangle_suff = "F"
    def __str__(self):
        return 'float'

class DoubleType(Type):
    mangle_suff = "D"
    def __str__(self):
        return 'double'

class ArrayType(Type):
    mangle_suff = "A"
    def __init__(self, array_type, count):
        self.element = array_type
        self.count = count
    def __str__(self):
        return f"[{self.count} x {self.element}]"

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