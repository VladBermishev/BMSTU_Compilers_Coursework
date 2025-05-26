import enum
import typing

class WhileType(enum.Enum):
    Endless = 0
    PreUntil = 1
    PreWhile = 2
    PostUntil = 3
    PostWhile = 4


class Type:
    name = "undefined"
    mangle_suff = "Und"

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "Auto"

class ConstantT(Type):
    name = "constant"


class VoidT(Type):
    name = "void"
    mangle_name = ""

    def __str__(self):
        return "void"

class CharT(Type):
    name = "char"
    mangle_suff = "C"

    def __str__(self):
        return "char"

class NumericT(Type):
    name = "numeric"
    mangle_suff = "N"
    priority = 0

    def default_value(self):
        return 0


class IntegralT(NumericT):
    name = "integral"
    mangle_suff = "N"
    priority = 0


class FloatingPointT(NumericT):
    name = "floating_point"
    mangle_suff = "N"
    priority = 0


class BoolT(IntegralT):
    name = "bool"
    mangle_suff = "B"
    priority = 1

    def __str__(self):
        return "Bool"


class IntegerT(IntegralT):
    name = "%"
    mangle_suff = "I"
    priority = 2

    def __str__(self):
        return "Integer"


class LongT(IntegralT):
    name = "&"
    mangle_suff = "L"
    priority = 3

    def __str__(self):
        return "Long"


class FloatT(FloatingPointT):
    name = "!"
    mangle_suff = "F"
    priority = 4

    def __str__(self):
        return "Float"


class DoubleT(FloatingPointT):
    name = "#"
    mangle_suff = "D"
    priority = 5

    def __str__(self):
        return "Double"


class ArrayT(Type):
    name = "array"
    undef_size = -1

    def __init__(self, valueT: Type, size: list[int]):
        self.value_type = valueT
        self.size = size
        self.mangle_suff = "A" + valueT.mangle_suff * len(size)

    def __eq__(self, other):
        if isinstance(other, ArrayT):
            self_any = self.value_type == Type()
            other_any = other.value_type == Type()
            if self_any or other_any:
                return self.size == other.size if len(self.size) != 1 and len(other.size) != 1 else True
            if isinstance(self.size[0], int) and isinstance(other.size[0], int):
                return self.value_type == other.value_type and self.size == other.size
            else:
                return self.value_type == other.value_type and len(self.size) == len(other.size)
        return False

    def __str__(self):
        dims = list(map(lambda sz: 'und' if sz == ArrayT.undef_size else str(sz), self.size))
        return f"{self.value_type}[{','.join(dims)}]"


class StringT(ArrayT):
    name = "string"
    mangle_suff = "S"

    def __init__(self, length=ArrayT.undef_size):
        super().__init__(CharT(), [length])

    def __eq__(self, other):
        return isinstance(other, StringT)


class PointerT(Type):
    name = "pointer"

    def __init__(self, valueT: Type):
        self.type = valueT
        self.mangle_suff = f"Ptr{valueT.mangle_suff}"

    def __str__(self):
        return f"Ptr{{{self.type}}}"


class ProcedureT(Type):
    name = "proc"

    def __init__(self, retT: Type, argsT: list[Type]):
        self.return_type = retT
        self.arguments_type = argsT

    def __eq__(self, other):
        if not isinstance(other, ProcedureT):
            return False
        result = self.return_type == other.return_type and len(self.arguments_type) == len(other.arguments_type)
        return result and all([self.arguments_type[i] == other.arguments_type[i] for i in range(len(self.arguments_type))])

    def __str__(self):
        return f"{self.return_type}(" + ','.join([str(v) for v in self.arguments_type]) + ")"


def __unroll_type_tree(tp: Type):
    result = []
    current_node = tp.__class__
    while current_node != object:
        result.append(current_node)
        current_node = current_node.__base__
    return result


def __types_lca(lhs_type: Type, rhs_type: Type):
    lhs_path, rhs_path = list(reversed(__unroll_type_tree(lhs_type))), list(reversed(__unroll_type_tree(rhs_type)))
    idx = 0
    while idx < min(len(lhs_path), len(rhs_path)) and lhs_path[idx] == rhs_path[idx]:
        idx += 1
    return lhs_path[idx - 1]


def __common_type(lhs_type: Type, rhs_type: Type) -> typing.Union[Type | None]:
    if lhs_type == rhs_type:
        return lhs_type
    if type(lhs_type) is Type or type(rhs_type) is Type:
        return rhs_type if type(lhs_type) is Type else lhs_type
    lca_type = __types_lca(lhs_type, rhs_type)
    if isinstance(lhs_type, NumericT) and isinstance(rhs_type, NumericT):
        return lhs_type if lhs_type.priority > rhs_type.priority else rhs_type
    elif lca_type == PointerT:
        ptr_type = __common_type(lhs_type.type, rhs_type.type)
        if ptr_type is None:
            return None
        return PointerT(ptr_type)
    elif lca_type == ProcedureT:
        return_type = __common_type(lhs_type.return_type, rhs_type.return_type)
        if return_type is None or len(lhs_type.arguments_type) != len(rhs_type.arguments_type):
            return None
        args_type = [__common_type(lhs_arg_type, rhs_arg_type) for lhs_arg_type, rhs_arg_type in zip(lhs_type.arguments_type, rhs_type.arguments_type)]
        if any([arg_type is None for arg_type in args_type]):
            return None
        return ProcedureT(return_type, args_type)
    elif lca_type == ArrayT:
        arr_type = __common_type(lhs_type.type, rhs_type.type)
        if arr_type is None:
            return None
        if type(lhs_type) is not Type and type(rhs_type) is not Type and lhs_type.size != rhs_type.size:
            return None
        return ArrayT(arr_type, lhs_type.size if type(lhs_type) is not Type else rhs_type.size)
    return None

def common_type(*args, types: typing.List[Type]=None):
    result = None
    if len(args) > 0:
        result = args[0]
        if len(args) > 1:
            result = __common_type(args[0], args[1])
            for idx in range(2, len(args)):
                result = __common_type(result, args[idx])
    if types is not None and len(types) > 0:
        if result is not None:
            types = [result] + types
        result = types[0]
        if len(types) > 1:
            result = __common_type(types[0], types[1])
            for idx in range(2, len(types)):
                result = __common_type(result, types[idx])
    return result

def mangle(name, tp: Type):
    return f"{name}{tp.mangle_suff}"