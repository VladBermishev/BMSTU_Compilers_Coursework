from abc import abstractmethod, ABC

class Type(ABC):
    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

class VoidType(Type):
    def __str__(self):
        return 'void'

# opaque-like
class PointerType(Type):
    def __init__(self):
        pass

    def __str__(self):
        return 'ptr'

class FunctionType(Type):
    def __init__(self, return_type, args):
        self.args = tuple(args)
        self.return_type = return_type

    def __str__(self):
        return f'{str(self.return_type)}({', '.join(map(str, self.args))})'

class BoolType(Type):
    def __str__(self):
        return 'i1'

class IntType(Type):
    def __str__(self):
        return 'i32'

class LongType(Type):
    def __str__(self):
        return 'i64'

class FloatType(Type):
    def __str__(self):
        return 'float'

class DoubleType(Type):
    def __str__(self):
        return 'double'

class ArrayType(Type):
    def __init__(self, array_type, count):
        self.element = array_type
        self.count = count
    def __str__(self):
        return f"[{self.count} x {self.element}]"

class StructType(Type):
    def __init__(self, elements):
        self.elements = tuple(elements)

    def __str__(self):
        return f"{{{', '.join(map(str, self.elements))}}}"

class LabelType(Type):
    def __str__(self):
        return "label"